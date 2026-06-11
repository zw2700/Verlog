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
import json
import logging
import os
import re
import time
from contextlib import contextmanager
from pathlib import Path
from enum import Enum
from typing import Any, Optional, List
from uuid import uuid4
import numpy as np
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
from verl.interactions.base import BaseInteraction
from verl.interactions.utils.interaction_registry import initialize_interactions_from_config
from verl.tools.schemas import ToolResponse
from verl.tools.utils.tool_registry import initialize_tools_from_config
from verl.utils.profiler import simple_timer
from verl.utils.rollout_trace import rollout_trace_op

logger = logging.getLogger(__file__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))

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
        cls.prompt_length = config.actor_rollout_ref.rollout.prompt_length
        cls.response_length = config.actor_rollout_ref.rollout.response_length
        cls.io_log_path = os.getenv("VERL_AGENT_IO_LOG_PATH", "logs/agent_model_io5.log")
        cls.game_log_path = os.getenv("VERL_GAME_LOG_PATH", None)
        cls.game_log_interval = int(os.getenv("VERL_GAME_LOG_INTERVAL", "1"))
        cls._game_log_prompt_written = False
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
        log_block = (
            f"\n=== {timestamp}Z env={env_idx} turn={turn_id} agent={agent_id} "
            f"prompt_tokens={len(prompt_ids)} response_tokens={len(response_ids)} ===\n"
            f"[PROMPT]\n{prompt_text}\n\n"
            f"[OUTPUT]\n{response_text}\n"
        )

        log_file = Path(self.io_log_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as f:
            f.write(log_block)

        turn_context = self._extract_turn_context(messages)
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

    def _extract_turn_context(self, messages: list[dict[str, Any]]) -> str:
        """Return only the current observation shown to the acting professor."""
        user_content = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_content = str(msg.get("content", ""))
                break

        if not user_content:
            return "(no user turn context found)"

        marker = "=== YOUR TURN"
        marker_idx = user_content.find(marker)
        if marker_idx >= 0:
            return user_content[marker_idx:].strip()
        return user_content.strip()

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
        
        outputs = []
        num_turns = 0
        reward = 0.0
        is_full = False
        bootstrap_added = False
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

            last_prompt_ids = copy.deepcopy(prompt_ids)
            with _phase(profile, "counter_is_full"):
                is_full = await counter.is_full.remote()
            if is_full and not is_val:
                break

            # Store observation before step (always, for loop detection)
            observation = copy.deepcopy(messages)

            acting_agent_id = agent_id
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
            )
            num_turns += 1

            # batch_size = await counter.get_batch_size.remote()
            # mini_batch_size = int(batch_size // 32)
            # if num_turns == mini_batch_size + 1:
            #     break

            with _phase(profile, "counter_increment"):
                is_full = await counter.increment.remote()
            if is_full and not is_val:
                # Training truncation path: append exactly one bootstrap sample
                # so output cardinality stays aligned with trainer expectations.
                # for loop over all agents
                for end_agent_id in range(3):
                    boot_resp_ids = [outputs[-1].response_ids[0]] if outputs else [151645]
                    bootstrap_turn = AgentLoopOutput(
                        prompt_ids=last_prompt_ids,
                        response_ids=boot_resp_ids,
                        response_mask=[1],
                        response_logprobs=[0.0] * len(boot_resp_ids),
                        metrics=dict(),
                        rewards=0.0,
                        done=True,
                        num_turns=num_turns,
                        env_idx=env_idx,
                        agent_id=f"prof_{end_agent_id+1}",
                        turn_id=num_turns,
                    )
                    outputs.append(bootstrap_turn)
                bootstrap_added = True
                break  # Exit loop after buffer truncation
            if done:
                outputs.append(turn_data)
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
                continue
            else:
                # Buffer not full or validation - append normal turn and continue
                outputs.append(turn_data)

            prompt_ids = await self.loop.run_in_executor(
                None,
                lambda: self._build_prompt_ids(messages),
            )

        # Episode completed naturally (not truncated) - add final bootstrap turn
        # This happens when done=True from environment termination
        if not bootstrap_added:
            # for loop over all agents
            for end_agent_id in range(3):
                boot_resp_ids = [outputs[-1].response_ids[0]] if outputs else [151645]
                bootstrap_turn = AgentLoopOutput(
                    prompt_ids=last_prompt_ids,
                    response_ids=boot_resp_ids,
                    response_mask=[1],
                    response_logprobs=[0.0] * len(boot_resp_ids),
                    metrics=dict(),
                    rewards=scalar_reward if is_val else 0.0,
                    done=True,
                    num_turns=num_turns,
                    env_idx=env_idx,
                    agent_id=f"prof_{end_agent_id+1}",
                    turn_id=num_turns,
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
