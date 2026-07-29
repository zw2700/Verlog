# Copyright 2025 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import asyncio
import copy
import logging
import os
import re
import time
from contextlib import contextmanager
from pathlib import Path
from enum import Enum
from typing import Any, Optional, List
from uuid import uuid4
from datetime import datetime

# Lightweight per-turn profiler. Enabled by VERL_PROFILE_AGENT_LOOP=1.
# When enabled, ToolAgentLoop.run accumulates wall-clock per phase and emits
# a single summary line at episode end. Designed to be a no-op when disabled.
_PROFILE_ENABLED = os.environ.get("VERL_PROFILE_AGENT_LOOP", "0") == "1"


@contextmanager
def _phase(profile: Optional[dict], name: str):
    if profile is None:
        yield
        return
    t0 = time.perf_counter()
    try:
        yield
    finally:
        slot = profile.setdefault(name, [0.0, 0])
        slot[0] += time.perf_counter() - t0
        slot[1] += 1


def _format_profile(profile: dict, *, env_idx: int, turns: int, agent_id: Optional[str]) -> str:
    total = sum(v[0] for v in profile.values())
    parts = []
    for name, (t, n) in sorted(profile.items(), key=lambda kv: -kv[1][0]):
        pct = 100.0 * t / total if total > 0 else 0.0
        parts.append(f"{name}={t:.2f}s({pct:.1f}%, n={n})")
    return (
        f"[AGENT_LOOP_PROFILE env_idx={env_idx} agent={agent_id} turns={turns} "
        f"total={total:.2f}s] " + " ".join(parts)
    )

from verl.experimental.agent_loop.agent_loop import AgentLoopBase, AgentLoopOutput, register
from verl.experimental.agent_loop.tool_parser import FunctionCall, ToolParser
from verl.envs import hiring_episode_logging as episode_logging
from verl.interactions.base import BaseInteraction
from verl.interactions.utils.interaction_registry import initialize_interactions_from_config
from verl.tools.schemas import ToolResponse
from verl.tools.utils.tool_registry import initialize_tools_from_config
from verl.utils.profiler import simple_timer
from verl.utils.rollout_trace import rollout_trace_op

logger = logging.getLogger(__file__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))

CRITIC_OBSERVATION_MODES = {"actor_visible", "all_utilities"}
_CRITIC_CONTEXT_HEADER = "<CRITIC_ONLY_PRIVILEGED_STATE>"


def build_critic_messages(
    messages: list[dict[str, Any]],
    *,
    mode: str,
    critic_context: Optional[dict[str, Any]] = None,
) -> list[dict[str, Any]]:
    """Return the critic prompt without changing the actor-visible messages."""
    if mode not in CRITIC_OBSERVATION_MODES:
        raise ValueError(f"critic observation mode must be one of {sorted(CRITIC_OBSERVATION_MODES)}, got {mode!r}")
    if mode == "actor_visible":
        return copy.deepcopy(messages)
    if not isinstance(critic_context, dict):
        raise ValueError("all_utilities critic observation requires critic context")

    professor_ids = [str(value) for value in critic_context.get("professor_ids", [])]
    utility_map = critic_context.get("student_utilities")
    if not professor_ids or not isinstance(utility_map, dict):
        raise ValueError("critic context must contain professor_ids and student_utilities")
    student_counts = {len(utility_map[professor_id]) for professor_id in professor_ids}
    if len(student_counts) != 1:
        raise ValueError("all professor utility vectors must have the same number of students")

    lines = [
        _CRITIC_CONTEXT_HEADER,
        "Training-only state for the value critic; this block is never visible to the acting policy.",
        "Utilities for every professor and student:",
    ]
    lines.append("student\t" + "\t".join(professor_ids))
    for student_idx in range(next(iter(student_counts))):
        values = [float(utility_map[professor_id][student_idx]) for professor_id in professor_ids]
        lines.append(f"{student_idx}\t" + "\t".join(f"{value:.4f}" for value in values))
    lines.append("</CRITIC_ONLY_PRIVILEGED_STATE>")
    privileged_block = "\n".join(lines)

    critic_messages = copy.deepcopy(messages)
    for message in critic_messages:
        if message.get("role") == "system":
            if _CRITIC_CONTEXT_HEADER in str(message.get("content", "")):
                raise ValueError("critic-only state was already present in the actor prompt")
            message["content"] = f"{message.get('content', '')}\n\n{privileged_block}"
            break
    else:
        critic_messages.insert(0, {"role": "system", "content": privileged_block})
    return critic_messages

class AgentState(Enum):
    PENDING = "pending"
    GENERATING = "generating"
    PROCESSING_TOOLS = "processing_tools"
    TERMINATED = "terminated"
    INTERACTING = "interacting"


class AgentData:
    """Encapsulates all state variables for the agent loop."""

    def __init__(
        self,
        messages: list[dict[str, Any]],
        image_data: Any,
        metrics: dict[str, Any],
        request_id: str,
        tools_kwargs: dict[str, Any],
        interaction: Optional[BaseInteraction] = None,
        interaction_kwargs: Optional[dict[str, Any]] = None,
    ):
        self.messages = messages
        self.image_data = image_data
        self.metrics = metrics
        self.request_id = request_id
        self.tools_kwargs = tools_kwargs
        self.interaction = interaction
        self.interaction_kwargs = interaction_kwargs or {}

        # State variables
        self.prompt_ids: list[int] = []
        self.response_ids: list[int] = []
        self.response_mask: list[int] = []
        self.response_logprobs: list[float] = []
        self.turn_scores: list[float] = []
        self.tool_rewards: list[float] = []
        self.user_turns = 0
        self.assistant_turns = 0

        # Temporary state for tool calls
        self.tool_calls: list[FunctionCall] = []


@register("tool_agent")
class ToolAgentLoop(AgentLoopBase):
    @classmethod
    def init_class(cls, config, tokenizer, processor, **kwargs):
        if cls._class_initialized:
            return
        cls._class_initialized = True
        print("Performing class-level ToolAgentLoop initialization")

        # Initialize tools from config file
        cls.tokenizer = tokenizer
        cls.processor = processor
        cls.max_user_turns = config.actor_rollout_ref.rollout.multi_turn.max_user_turns
        cls.max_assistant_turns = config.actor_rollout_ref.rollout.multi_turn.max_assistant_turns
        cls.max_parallel_calls = config.actor_rollout_ref.rollout.multi_turn.max_parallel_calls
        cls.max_tool_response_length = config.actor_rollout_ref.rollout.multi_turn.max_tool_response_length
        cls.tool_response_truncate_side = config.actor_rollout_ref.rollout.multi_turn.tool_response_truncate_side
        tool_config_path = config.actor_rollout_ref.rollout.multi_turn.tool_config_path
        tool_list = initialize_tools_from_config(tool_config_path) if tool_config_path else []
        cls.tools = {tool.name: tool for tool in tool_list}
        cls.tool_schemas = [tool.tool_schema.model_dump(exclude_unset=True, exclude_none=True) for tool in tool_list]
        cls.tool_parser = ToolParser.get_tool_parser(config.actor_rollout_ref.rollout.multi_turn.format, cls.tokenizer)
        print(f"Initialized tools: {cls.tools}")

        cls.apply_chat_template_kwargs = config.data.get("apply_chat_template_kwargs", {})
        critic_observation = config.get("critic_observation", {})
        cls.critic_observation_mode = str(critic_observation.get("mode", "actor_visible"))
        if cls.critic_observation_mode not in CRITIC_OBSERVATION_MODES:
            raise ValueError(
                "critic_observation.mode must be one of "
                f"{sorted(CRITIC_OBSERVATION_MODES)}, got {cls.critic_observation_mode!r}"
            )
        cls.prompt_length = config.actor_rollout_ref.rollout.prompt_length
        cls.response_length = config.actor_rollout_ref.rollout.response_length
        cls.io_log_path = os.getenv("VERL_AGENT_IO_LOG_PATH", "logs/agent_model_io5.log")
        cls.io_log_full_prompt = os.getenv("VERL_AGENT_IO_LOG_FULL_PROMPT", "1") == "1"
        cls.episode_log_path = os.getenv("VERL_AGENT_EPISODE_LOG_PATH", None)
        cls.game_log_path = os.getenv("VERL_GAME_LOG_PATH", None)
        cls.game_log_interval = int(os.getenv("VERL_GAME_LOG_INTERVAL", "1"))
        cls._game_log_prompt_written = False
        cls._io_log_prompt_written = False
        cls.system_prompt = tokenizer.apply_chat_template(
            [{}], add_generation_prompt=False, tokenize=True, **cls.apply_chat_template_kwargs
        )
        # Initialize interactions from config file
        cls.interaction_config_file = config.actor_rollout_ref.rollout.multi_turn.interaction_config_path
        if cls.interaction_config_file:
            cls.interaction_map: dict[str, BaseInteraction] = cls._initialize_interactions(cls.interaction_config_file)

    def _append_step_io_log(
        self,
        *,
        env_idx: int,
        turn_id: int,
        agent_id: str | None,
        messages: list[dict[str, Any]],
        prompt_ids: list[int],
        response_ids: list[int],
    ) -> str:
        prompt_text = self.tokenizer.decode(prompt_ids, skip_special_tokens=False)
        response_text = self.tokenizer.decode(response_ids, skip_special_tokens=False)
        timestamp = datetime.utcnow().isoformat(timespec="seconds")
        turn_context = self._extract_turn_context(messages)
        prompt_section = (
            f"[PROMPT]\n{prompt_text}"
            if self.io_log_full_prompt
            else f"[TURN CONTEXT]\n{turn_context}"
        )
        log_block = (
            f"\n=== {timestamp}Z env={env_idx} turn={turn_id} agent={agent_id} "
            f"prompt_tokens={len(prompt_ids)} response_tokens={len(response_ids)} ===\n"
            f"{prompt_section}\n\n"
            f"[OUTPUT]\n{response_text}\n"
        )

        log_file = Path(self.io_log_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as f:
            if not self.io_log_full_prompt and not self.__class__._io_log_prompt_written:
                f.write(
                    "\n"
                    + "=" * 70
                    + f"\n=== AGENT I/O LOG compact_prompt=1 {timestamp}Z ===\n"
                    + "=" * 70
                    + "\nFull system prompts are omitted from per-turn entries. "
                    + "Set VERL_AGENT_IO_LOG_FULL_PROMPT=1 to log decoded full prompts.\n"
                )
                self.__class__._io_log_prompt_written = True
            f.write(log_block)

        return (
            f"\n=== {timestamp}Z env={env_idx} turn={turn_id} agent={agent_id} "
            f"prompt_tokens={len(prompt_ids)} response_tokens={len(response_ids)} ===\n"
            f"[TURN CONTEXT]\n{turn_context}\n\n"
            f"[OUTPUT]\n{response_text}\n"
        )

    _VOTE_PATTERN = re.compile(r"<VOTE>\s*(\d+)\s*</VOTE>")

    def _extract_vote_metadata(
        self,
        *,
        action_text: str,
        response_ids: list[int],
        top_logprobs: Optional[list[dict[int, float]]],
        chosen_logprobs: Optional[list[float]],
    ) -> dict[str, Any]:
        """Build a minimal vote-logprob payload for env.step().

        Only decodes the digit token between <VOTE>...</VOTE> plus the top-K
        alternatives at that single position. Returns sentinel empty dict on
        fast paths (no vote, no logprobs available, position not locatable).
        """
        meta: dict[str, Any] = {"vote_alternatives": None, "vote_chosen_token": None}
        if not action_text:
            return meta
        m = self._VOTE_PATTERN.search(action_text)
        if not m:
            return meta
        digit_str = m.group(1)
        digit_char_start = m.start(1)
        prefix_text = action_text[:digit_char_start]
        try:
            prefix_ids = self.tokenizer.encode(prefix_text, add_special_tokens=False)
        except Exception:
            return meta
        vote_idx = len(prefix_ids)
        if vote_idx >= len(response_ids):
            return meta
        # Best-effort: confirm the token at vote_idx decodes to something
        # starting with the expected digit. If not, search a small window.
        chosen_token_id = response_ids[vote_idx]
        chosen_token_str = self.tokenizer.decode([chosen_token_id], skip_special_tokens=True)
        if digit_str not in chosen_token_str:
            for offset in (-1, 1, -2, 2):
                cand = vote_idx + offset
                if 0 <= cand < len(response_ids):
                    s = self.tokenizer.decode([response_ids[cand]], skip_special_tokens=True)
                    if digit_str in s:
                        vote_idx = cand
                        chosen_token_id = response_ids[cand]
                        chosen_token_str = s
                        break
            else:
                return meta
        chosen_lp = None
        if chosen_logprobs is not None and vote_idx < len(chosen_logprobs):
            chosen_lp = float(chosen_logprobs[vote_idx])
        alts: list[tuple[str, float]] = []
        if top_logprobs is not None and vote_idx < len(top_logprobs):
            pos_dict = top_logprobs[vote_idx]
            if pos_dict:
                ids_to_decode = list(pos_dict.keys())
                strs = [self.tokenizer.decode([tid], skip_special_tokens=True) for tid in ids_to_decode]
                alts = [(s, float(pos_dict[tid])) for s, tid in zip(strs, ids_to_decode)]
        meta["vote_chosen_token"] = chosen_token_str
        meta["vote_chosen_logprob"] = chosen_lp
        meta["vote_alternatives"] = alts
        return meta

    @staticmethod
    def _json_safe(obj: Any) -> Any:
        """Convert numpy/scalar objects into JSON-serializable values."""
        return episode_logging.json_safe(obj)

    @staticmethod
    def _append_jsonl_locked(path: str | Path, row: dict[str, Any]) -> None:
        """Append one JSONL row under a file lock to avoid multi-worker interleaving."""
        episode_logging.append_jsonl_locked(path, row)

    @classmethod
    def _extract_action_text(cls, output: str) -> str:
        return episode_logging.extract_action_text(output)

    @classmethod
    def _parse_action_summary(cls, action_text: str) -> dict[str, Any]:
        return episode_logging.parse_action_summary(action_text)

    @classmethod
    def _extract_utilities_from_context(cls, turn_context: str) -> dict[str, float]:
        return episode_logging.extract_utilities_from_context(turn_context)

    def _build_episode_turn_entry(
        self,
        *,
        timestamp: str,
        env_idx: int,
        global_steps: int,
        epoch: int,
        turn_id: int,
        episode_turn_id: int,
        agent_id: str | None,
        prompt_ids: list[int],
        response_ids: list[int],
        messages: list[dict[str, Any]],
        output_text: str,
    ) -> dict[str, Any]:
        return episode_logging.build_episode_turn_entry(
            timestamp=timestamp,
            env_idx=env_idx,
            global_steps=global_steps,
            epoch=epoch,
            turn_id=turn_id,
            episode_turn_id=episode_turn_id,
            agent_id=agent_id,
            prompt_tokens=len(prompt_ids),
            response_tokens=len(response_ids),
            messages=messages,
            output_text=output_text,
        )

    def _append_episode_jsonl_log(
        self,
        *,
        epoch: int,
        global_steps: int,
        env_idx: int,
        episode_index: int,
        turns: list[dict[str, Any]],
        reward: Any,
        info: dict[str, Any] | None,
    ) -> None:
        if not self.episode_log_path:
            return

        episode_logging.append_episode_jsonl_log(
            self.episode_log_path,
            epoch=epoch,
            global_steps=global_steps,
            env_idx=env_idx,
            episode_index=episode_index,
            turns=turns,
            reward=reward,
            info=info,
        )

    def _extract_turn_context(self, messages: list[dict[str, Any]]) -> str:
        """Return only the current observation shown to the acting professor."""
        return episode_logging.extract_turn_context(messages)

    @staticmethod
    def _format_episode_diagnosis(
        env_idx: int,
        reward: Any,
        info: dict[str, Any] | None,
    ) -> str:
        """One per-episode reward/error summary block for the game log.

        `reward` is the terminal per-agent reward dict from env.step; the
        per-agent turn/error counts come from
        info["episode_metrics"]["action_validity"]["by_agent"].
        """
        return episode_logging.format_episode_diagnosis(env_idx, reward, info)

    def _format_game_log_prompt_header(
        self,
        system_prompts: dict[str, str] | None,
        messages: list[dict[str, Any]],
    ) -> str:
        timestamp = datetime.utcnow().isoformat(timespec="seconds")
        lines = [
            f"\n{'='*70}",
            f"=== GAME LOG RUN PROMPTS {timestamp}Z ===",
            f"{'='*70}",
            "System prompts logged once for this training process. Per-turn entries below log only the dynamic turn context.",
        ]

        if system_prompts:
            for agent_id in sorted(system_prompts):
                lines.extend([
                    "",
                    f"--- SYSTEM PROMPT agent={agent_id} ---",
                    str(system_prompts[agent_id]).strip(),
                ])
        else:
            system_content = ""
            for msg in messages:
                if msg.get("role") == "system":
                    system_content = str(msg.get("content", ""))
                    break
            lines.extend([
                "",
                f"--- SYSTEM PROMPT agent=unknown ---",
                system_content.strip() if system_content else "(no system prompt found)",
            ])

        return "\n".join(lines) + "\n"

    def _build_prompt_ids(self, messages: list[dict[str, Any]]) -> list[int]:
        """Build prompt ids while preserving the initial system prompt when truncating."""
        tokenize_kwargs = dict(self.apply_chat_template_kwargs)
        # We manage truncation ourselves to preserve system prompt + newest turns.
        tokenize_kwargs.pop("truncation", None)
        tokenize_kwargs.pop("max_length", None)

        def _tokenize(msgs: list[dict[str, Any]]) -> list[int]:
            return self.tokenizer.apply_chat_template(
                msgs,
                tools=self.tool_schemas,
                add_generation_prompt=True,
                tokenize=True,
                **tokenize_kwargs,
            )

        if not messages:
            return _tokenize(messages)

        has_system = messages[0].get("role") == "system"
        prefix_messages = [messages[0]] if has_system else []
        tail_messages = messages[1:] if has_system else messages

        best_ids: list[int] | None = None
        best_start_idx: int | None = None

        # Start from the shortest candidate and progressively add older turns.
        # This avoids tokenizing the full history first, which can emit long-sequence warnings.
        if has_system:
            start_indices = range(len(tail_messages), -1, -1)
        else:
            # Without a system prompt, keep at least the latest message.
            if not tail_messages:
                return []
            start_indices = range(len(tail_messages) - 1, -1, -1)

        for start_idx in start_indices:
            candidate_messages = prefix_messages + tail_messages[start_idx:]
            candidate_ids = _tokenize(candidate_messages)
            if len(candidate_ids) <= self.prompt_length:
                best_ids = candidate_ids
                best_start_idx = start_idx
            elif best_ids is not None:
                # Adding older turns made it too long; previous fit is maximal under budget.
                break

        if best_ids is not None:
            if best_start_idx and best_start_idx > 0:
                # System-only fit but system + user observation didn't.
                # Try left-truncating the user content to keep as much recent
                # conversation history as possible (drop oldest entries).
                if tail_messages and tail_messages[-1].get("role") == "user":
                    user_msg = tail_messages[-1]
                    user_ids_raw = self.tokenizer.encode(
                        user_msg["content"], add_special_tokens=False
                    )
                    # Budget for user content: prompt_length minus system-only token
                    # count, minus a small buffer for chat-template overhead tokens
                    # (im_start/im_end for the user turn, ~15 tokens).
                    available = self.prompt_length - len(best_ids) - 15
                    if available > 0 and len(user_ids_raw) > available:
                        truncated_content = self.tokenizer.decode(
                            user_ids_raw[-available:], skip_special_tokens=False
                        )
                        candidate_msgs = prefix_messages + [
                            {**user_msg, "content": truncated_content}
                        ]
                        candidate_ids = _tokenize(candidate_msgs)
                        if len(candidate_ids) <= self.prompt_length:
                            logger.warning(
                                "User observation left-truncated to fit prompt_length; "
                                "oldest conversation history dropped (%d → %d user tokens).",
                                len(user_ids_raw),
                                available,
                            )
                            return candidate_ids
                logger.warning(
                    "Prompt exceeded prompt_length; dropped %d oldest non-system messages.",
                    best_start_idx,
                )
            return best_ids

        # If even minimal context is too long, truncate token IDs as a final fallback.
        minimal_messages = prefix_messages if has_system else [tail_messages[-1]]
        minimal_ids = _tokenize(minimal_messages)
        logger.warning(
            "Minimal prompt still exceeds prompt_length (%d > %d); truncating token IDs as fallback.",
            len(minimal_ids),
            self.prompt_length,
        )
        return minimal_ids[-self.prompt_length:]

    async def _build_critic_prompt_ids(
        self,
        env,
        messages: list[dict[str, Any]],
        actor_prompt_ids: list[int],
    ) -> list[int]:
        if self.critic_observation_mode == "actor_visible":
            # Preserve exact actor/critic input equality in the baseline cell.
            return copy.deepcopy(actor_prompt_ids)
        if not hasattr(env, "get_critic_context"):
            raise TypeError("all_utilities critic observation requires env.get_critic_context()")
        critic_messages = build_critic_messages(
            messages,
            mode=self.critic_observation_mode,
            critic_context=env.get_critic_context(),
        )
        return await self.loop.run_in_executor(None, lambda: self._build_prompt_ids(critic_messages))

    async def _build_bootstrap_prompts(self, env, professor_id: str) -> tuple[list[int], list[int]]:
        if not hasattr(env, "get_observation_for_agent"):
            raise TypeError("multi-agent bootstrap requires env.get_observation_for_agent()")
        actor_messages = env.get_observation_for_agent(professor_id)
        actor_prompt_ids = await self.loop.run_in_executor(None, lambda: self._build_prompt_ids(actor_messages))
        critic_prompt_ids = await self._build_critic_prompt_ids(env, actor_messages, actor_prompt_ids)
        return actor_prompt_ids, critic_prompt_ids

    def _bootstrap_response_ids(self, outputs: list[AgentLoopOutput]) -> list[int]:
        if outputs and outputs[-1].response_ids:
            return [outputs[-1].response_ids[0]]
        fallback_id = self.tokenizer.eos_token_id
        if fallback_id is None:
            fallback_id = self.tokenizer.pad_token_id
        if fallback_id is None:
            raise ValueError("tokenizer must define eos_token_id or pad_token_id for bootstrap rows")
        return [int(fallback_id)]

    def _detect_loop(self, messages: list[dict[str, Any]]) -> bool:
        """
        Detect if a loop occurred by checking if the last message contains a hint.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Returns:
            bool: True if a hint is detected in the last user message, False otherwise
        """
        if not messages:
            return False
        
        # Find the last user message
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                # Check if the content contains the hint pattern
                if "[Hint:" in content or "[Hint " in content:
                    return True
                break
        
        return False

    @rollout_trace_op
    async def run(self, env, counter, env_idx: int, sampling_params: dict[str, Any], is_val: bool, global_steps: int = -1, epoch: int = -1, **kwargs) -> List[AgentLoopOutput]:
        agent_id = kwargs.get("agent_id")
        # Normalize env.reset outputs to (messages, info) for both legacy Env
        # wrapper (which already returns messages + info) and new multi-agent
        # gym-style envs (e.g. AsyncTickerAdmissionsEnv) that return
        # (observations, infos_dict).
        def _flatten_info(info_obj):
            if isinstance(info_obj, dict) and info_obj:
                first_val = next(iter(info_obj.values()))
                if isinstance(first_val, dict) and "active_agent" in first_val:
                    return first_val
            return info_obj

        def _critic_probe_target(info_obj, professor_id):
            if not isinstance(info_obj, dict) or professor_id is None:
                return None
            targets = info_obj.get("critic_probe_targets")
            if not isinstance(targets, dict):
                for value in info_obj.values():
                    if isinstance(value, dict) and isinstance(value.get("critic_probe_targets"), dict):
                        targets = value["critic_probe_targets"]
                        break
            if not isinstance(targets, dict) or str(professor_id) not in targets:
                return None
            return float(targets[str(professor_id)])

        if is_val:
            messages, info = env.reset(agent_id=agent_id)
        else:
            messages, info = env.get_last_obs(agent_id=agent_id)
            if not messages:
                messages, info = env.reset(agent_id=agent_id)
        info = _flatten_info(info)
        if info and info.get("active_agent") is not None:
            agent_id = info.get("active_agent")
        game_log_system_prompts = info.get("system_prompts") if isinstance(info, dict) else None

        metrics = {}
        request_id = uuid4().hex

        # Initialize loop tracking in metrics (for both val and training)
        all_loop_counts = 0

        profile: Optional[dict] = {} if _PROFILE_ENABLED else None
        _t_run_start = time.perf_counter() if _PROFILE_ENABLED else None

        with _phase(profile, "build_prompt_ids"):
            prompt_ids = await self.loop.run_in_executor(
                None,
                lambda: self._build_prompt_ids(messages),
            )
            critic_prompt_ids = await self._build_critic_prompt_ids(env, messages, prompt_ids)

        professor_ids = [str(value) for value in getattr(env, "professor_ids", [])]
        if not professor_ids:
            raise ValueError("multi-agent rollout requires the environment to expose professor_ids")
        
        outputs = []
        num_turns = 0
        episode_index = 0
        episode_turns: list[dict[str, Any]] = []
        reward = 0.0
        bootstrap_added = False
        # Index into `outputs` of each agent's most recent turn in the CURRENT
        # episode. Used at episode end to route every professor's own terminal
        # utility into their own (env_idx, agent_id) GAE chain — otherwise only
        # the consensus-closing agent's utility ever reaches a training row
        # (see bugs_todo.md: non-closing professors receive zero outcome reward).
        episode_last_row: dict[str, int] = {}
        # Real rollout rows from the current env episode. Completed probe
        # episodes are marked so diagnostics can exclude rollout truncations,
        # whose returns legitimately use critic bootstrapping instead of +/-1.
        episode_row_indices: list[int] = []
        game_entries = []
        log_this_game = (
            self.game_log_path is not None
            and not is_val
            and env_idx == 0
            and global_steps >= 0
            and self.game_log_interval > 0
            and global_steps % self.game_log_interval == 0
        )
        # Ensure we request top-K logprobs so env can measure vote-digit
        # preference distribution. 20 is enough to cover digits 0-9 reliably.
        sampling_params = dict(sampling_params)
        if not isinstance(sampling_params.get("logprobs"), int) or sampling_params["logprobs"] < 20:
            sampling_params["logprobs"] = 20
        while True:
            # Reserve a real-turn slot BEFORE generation/env.step. If we only
            # increment after generation, multiple async workers can pass the
            # pre-generation fullness check at once and append extra real rows
            # beyond gen_batch_size, causing trainer batch-size mismatches.
            reserved_turn_fills_counter = False
            if not is_val:
                with _phase(profile, "counter_increment"):
                    turn_accepted, reserved_turn_fills_counter = await counter.increment.remote()
                if not turn_accepted:
                    # Another worker filled the shared rollout counter while
                    # this worker was idle. Do not generate or step the env
                    # beyond the requested real-turn budget.
                    break

            with simple_timer("generate_sequences", metrics), _phase(profile, "vllm_generate"):
                output = await self.server_manager.generate(
                    request_id=request_id,
                    prompt_ids=prompt_ids,
                    sampling_params=sampling_params,
                    image_data=None,
                    # env_idx=env_idx,
                )

            # truncate response_ids to response_length
            response_ids = output.token_ids[: self.response_length]
            response_mask = [1] * len(response_ids)

            assert len(prompt_ids) <= self.prompt_length
            assert len(response_ids) <= self.response_length

            if output.log_probs:
                response_logprobs = list(output.log_probs[: self.response_length])
            else:
                # vLLM occasionally returns an empty log_probs list (e.g. zero-token
                # response). We always request logprobs=20, so downstream batching
                # expects every turn to carry a logprob vector. Synthesise zeros to
                # keep shapes uniform across the batch.
                response_logprobs = [0.0] * len(response_ids)

            with _phase(profile, "decode_response"):
                actions = await self.loop.run_in_executor(
                    None,
                    lambda: self.tokenizer.decode(response_ids, skip_special_tokens=True)
                )
            output_text_for_log = actions
            timestamp_for_log = datetime.utcnow().isoformat(timespec="seconds")
            episode_turns.append(
                self._build_episode_turn_entry(
                    timestamp=timestamp_for_log,
                    env_idx=env_idx,
                    global_steps=global_steps,
                    epoch=epoch,
                    turn_id=num_turns,
                    episode_turn_id=len(episode_turns),
                    agent_id=agent_id,
                    prompt_ids=prompt_ids,
                    response_ids=response_ids,
                    messages=messages,
                    output_text=output_text_for_log,
                )
            )
            with _phase(profile, "append_io_log"):
                log_entry = await self.loop.run_in_executor(
                    None,
                    lambda: self._append_step_io_log(
                        env_idx=env_idx,
                        turn_id=num_turns,
                        agent_id=agent_id,
                        messages=messages,
                        prompt_ids=prompt_ids,
                        response_ids=response_ids,
                    ),
                )
            if log_this_game:
                game_entries.append(log_entry)
            if agent_id is not None:
                with _phase(profile, "extract_vote_meta"):
                    vote_meta = self._extract_vote_metadata(
                        action_text=actions,
                        response_ids=response_ids,
                        top_logprobs=getattr(output, "top_logprobs", None),
                        chosen_logprobs=response_logprobs if output.log_probs else None,  # only real ones
                    )
                actions = {agent_id: {
                    "text": actions,
                    "metadata": vote_meta,
                }}

            # Store observation before step (always, for loop detection)
            observation = copy.deepcopy(messages)

            acting_agent_id = agent_id
            critic_probe_target = _critic_probe_target(info, acting_agent_id)
            with _phase(profile, "env_step"):
                messages, reward, terminated, truncated, info = env.step(actions)
            # info may be a flat dict (single-agent env) or agent-keyed dict
            # (multi-agent env like hiring_env: {"prof_1": base_info, ...}).
            # Normalise to a flat dict for all downstream lookups.
            _flat_info = _flatten_info(info)
            if _flat_info and _flat_info.get("active_agent") is not None:
                agent_id = _flat_info.get("active_agent")
            if isinstance(reward, dict):
                scalar_reward = float(reward.get(acting_agent_id, sum(reward.values())))
            else:
                scalar_reward = float(reward)
            if isinstance(terminated, dict):
                scalar_terminated = any(terminated.values())
            else:
                scalar_terminated = bool(terminated)
            if isinstance(truncated, dict):
                scalar_truncated = any(truncated.values())
            else:
                scalar_truncated = bool(truncated)
            done = scalar_terminated or scalar_truncated
            
            # Detect loop: check if the observation contains a hint (for both val and training)
            is_loop = self._detect_loop(observation)
            if is_loop:
                all_loop_counts += 1
            
            # Update metrics with info and loop tracking
            step_env_metrics = _flat_info.get("metrics", {})
            if step_env_metrics:
                metrics["env_metrics"] = step_env_metrics
            metrics["loop_counts"] = 1.0 if is_loop else 0.0
            metrics["loop_rate"] = all_loop_counts / (num_turns + 1) if (num_turns + 1) > 0 else 0.0
            
            turn_data = AgentLoopOutput(
                prompt_ids=prompt_ids,
                critic_prompt_ids=critic_prompt_ids,
                response_ids=response_ids,
                response_mask=response_mask,
                response_logprobs=response_logprobs,
                metrics=metrics,
                rewards=scalar_reward,
                done=done,
                num_turns=num_turns,
                env_idx=env_idx,
                agent_id=str(acting_agent_id),
                turn_id=num_turns,
                # DataProto.concat requires every non-tensor field to have one
                # entry per row. Keep both probe fields present even for
                # non-probe and incomplete rows; the metric filters on the
                # explicit completion flag below.
                extra_fields={
                    "critic_probe_target": critic_probe_target,
                    "critic_probe_complete": False,
                    "critic_observation_mode": self.critic_observation_mode,
                    "critic_prompt_tokens": len(critic_prompt_ids),
                    "actor_prompt_tokens": len(prompt_ids),
                    "episode_index": episode_index,
                    "episode_turn_id": len(episode_turns) - 1,
                    "is_bootstrap": False,
                },
            )
            num_turns += 1

            # batch_size = await counter.get_batch_size.remote()
            # mini_batch_size = int(batch_size // 32)
            # if num_turns == mini_batch_size + 1:
            #     break

            # Record this turn's row. We handle `done` BEFORE the truncation
            # exit so the real closing-action row is always kept (even when the
            # closing turn is also the one that fills the counter): it carries
            # the closing agent's own utility and stays an interior row once the
            # value-carrier bootstrap rows are appended after it.
            if done:
                outputs.append(turn_data)
                episode_row_indices.append(len(outputs) - 1)

                if critic_probe_target is not None:
                    for row_index in episode_row_indices:
                        outputs[row_index].extra_fields["critic_probe_complete"] = True

                # Route every other professor's terminal utility onto their last
                # turn of this episode (an interior row of their (env, agent)
                # GAE chain) and mark it done=True. The closing agent's utility
                # already rides on turn_data above (skip them). done=True closes
                # each chain at the episode boundary — otherwise GAE bootstraps
                # values across episodes (only the closer's row had done set).
                # Utilities must NOT go on bootstrap rows: GAE forces the last
                # row of each chain to advantage 0 and never reads its reward
                # (value carrier only — see compute_gae_advantage_return_core).
                if isinstance(reward, dict):
                    for other_agent, other_reward in reward.items():
                        if str(other_agent) == str(acting_agent_id):
                            continue
                        row_idx = episode_last_row.get(str(other_agent))
                        if row_idx is not None:
                            outputs[row_idx].rewards += float(other_reward)
                            outputs[row_idx].done = True
                episode_last_row = {}
                episode_row_indices = []

                # Per-episode reward/error diagnosis in the game log.
                if log_this_game:
                    game_entries.append(
                        self._format_episode_diagnosis(env_idx, reward, _flat_info)
                    )
                self._append_episode_jsonl_log(
                    epoch=epoch,
                    global_steps=global_steps,
                    env_idx=env_idx,
                    episode_index=episode_index,
                    turns=episode_turns,
                    reward=reward,
                    info=_flat_info,
                )
                episode_turns = []
                episode_index += 1
            else:
                # Normal non-terminal turn. If this accepted turn filled the
                # counter, keep it as the final real row and append bootstrap
                # rows below.
                outputs.append(turn_data)
                episode_row_indices.append(len(outputs) - 1)
                episode_last_row[str(acting_agent_id)] = len(outputs) - 1

            if reserved_turn_fills_counter and not is_val:
                # Buffer full: append one value-carrier bootstrap row per agent
                # so every (env, agent) chain ends with a strippable terminal
                # row (removed before training; reward ignored by GAE, kept 0.0).
                # A terminal turn_data appended above stays interior (bootstrap
                # rows get the higher turn_id and are the ones dropped).
                for boot_agent_id in professor_ids:
                    boot_prompt_ids, boot_critic_prompt_ids = await self._build_bootstrap_prompts(
                        env, boot_agent_id
                    )
                    boot_resp_ids = self._bootstrap_response_ids(outputs)
                    bootstrap_turn = AgentLoopOutput(
                        prompt_ids=boot_prompt_ids,
                        critic_prompt_ids=boot_critic_prompt_ids,
                        response_ids=boot_resp_ids,
                        response_mask=[1],
                        response_logprobs=[0.0] * len(boot_resp_ids),
                        metrics=dict(),
                        rewards=0.0,
                        done=True,
                        num_turns=num_turns,
                        env_idx=env_idx,
                        agent_id=boot_agent_id,
                        turn_id=num_turns,
                        extra_fields={
                            "critic_probe_target": None,
                            "critic_probe_complete": False,
                            "critic_observation_mode": self.critic_observation_mode,
                            "critic_prompt_tokens": len(boot_critic_prompt_ids),
                            "actor_prompt_tokens": len(boot_prompt_ids),
                            "episode_index": episode_index,
                            "episode_turn_id": len(episode_turns),
                            "is_bootstrap": True,
                        },
                    )
                    outputs.append(bootstrap_turn)
                bootstrap_added = True
                break  # Exit loop after buffer truncation

            if done:
                if is_val:
                    break
                # Training must continue filling the shared rollout counter,
                # but the next generation must start from a fresh episode
                # rather than the terminal observation returned with done=True.
                messages, info = env.reset(agent_id=agent_id)
                info = _flatten_info(info)
                if info and info.get("active_agent") is not None:
                    agent_id = info.get("active_agent")
                prompt_ids = await self.loop.run_in_executor(
                    None,
                    lambda: self._build_prompt_ids(messages),
                )
                critic_prompt_ids = await self._build_critic_prompt_ids(env, messages, prompt_ids)
                continue

            prompt_ids = await self.loop.run_in_executor(
                None,
                lambda: self._build_prompt_ids(messages),
            )
            critic_prompt_ids = await self._build_critic_prompt_ids(env, messages, prompt_ids)

        # Episode completed naturally (not truncated) - add final bootstrap turn
        # This happens when done=True from environment termination
        if not bootstrap_added:
            # for loop over all agents
            for boot_agent_id in professor_ids:
                # Validation: each agent's bootstrap row carries that agent's
                # OWN terminal utility (the val metric reads the last row per
                # (env, agent)). Previously every agent got the closer's
                # scalar_reward, so val/mean_rewards was the closer's reward
                # replicated per agent.
                if is_val:
                    if isinstance(reward, dict):
                        boot_reward = float(reward.get(boot_agent_id, 0.0))
                    else:
                        boot_reward = scalar_reward
                else:
                    boot_reward = 0.0
                boot_prompt_ids, boot_critic_prompt_ids = await self._build_bootstrap_prompts(env, boot_agent_id)
                boot_resp_ids = self._bootstrap_response_ids(outputs)
                bootstrap_turn = AgentLoopOutput(
                    prompt_ids=boot_prompt_ids,
                    critic_prompt_ids=boot_critic_prompt_ids,
                    response_ids=boot_resp_ids,
                    response_mask=[1],
                    response_logprobs=[0.0] * len(boot_resp_ids),
                    metrics=dict(),
                    rewards=boot_reward,
                    done=True,
                    num_turns=num_turns,
                    env_idx=env_idx,
                    agent_id=boot_agent_id,
                    turn_id=num_turns,
                    extra_fields={
                        "critic_probe_target": None,
                        "critic_probe_complete": False,
                        "critic_observation_mode": self.critic_observation_mode,
                        "critic_prompt_tokens": len(boot_critic_prompt_ids),
                        "actor_prompt_tokens": len(boot_prompt_ids),
                        "episode_index": max(0, episode_index - 1),
                        "episode_turn_id": len(episode_turns),
                        "is_bootstrap": True,
                    },
                )
                outputs.append(bootstrap_turn)

        if game_entries:
            header = (
                f"\n{'='*70}\n"
                f"=== GAME LOG epoch={epoch} global_steps={global_steps} env={env_idx} ===\n"
                f"{'='*70}\n"
            )
            game_log_file = Path(self.game_log_path)
            game_log_file.parent.mkdir(parents=True, exist_ok=True)
            with game_log_file.open("a", encoding="utf-8") as f:
                if not self.__class__._game_log_prompt_written:
                    f.write(self._format_game_log_prompt_header(game_log_system_prompts, messages))
                    self.__class__._game_log_prompt_written = True
                f.write(header + "".join(game_entries))

        if _PROFILE_ENABLED and profile is not None:
            wall = time.perf_counter() - _t_run_start if _t_run_start is not None else 0.0
            profile.setdefault("_run_wall", [wall, 1])
            print(_format_profile(profile, env_idx=env_idx, turns=num_turns, agent_id=agent_id), flush=True)

        return outputs

    @classmethod
    def _initialize_interactions(cls, interaction_config_file):
        """Initialize interactions from configuration.
        Returns:
            dict[str, BaseInteraction]: A dictionary mapping interaction names to interaction instances.
        """
        if interaction_config_file is None:
            return {}

        interaction_map = initialize_interactions_from_config(interaction_config_file)
        logger.info(f"Initialize interactions from configuration: interaction_map: {list(interaction_map.keys())}")
        return interaction_map
