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
"""Consensus multi-agent agent loop for verl-0.8.

Port of the OLD Verlog fork's env-driven, multi-agent turn loop
(``ToolAgentLoop.run`` + ``MultiAgentToolAgentLoop`` agent selection) onto the
verl-0.8 ``AgentLoopBase`` API. One ``AgentLoopOutput`` is emitted per real
turn plus per-agent value-carrier bootstrap rows, so each ``(env_idx, agent_id)``
GAE chain closes cleanly.

Instrumentation from the old fork (game/io/episode-jsonl logging, per-turn
profiling, and vote-logprob metadata extraction) is intentionally omitted here:
the action dict carries ``metadata={}`` and no files are written.
"""

import copy
import logging
import os
from typing import Any, List, Optional
from uuid import uuid4

from verl.experimental.agent_loop.agent_loop import (
    AgentLoopBase,
    AgentLoopMetrics,
    AgentLoopOutput,
    register,
)
from verl.utils.profiler import simple_timer
from verl.utils.rollout_trace import rollout_trace_op

logger = logging.getLogger(__file__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))

_DEFAULT_AGENTS = ["prof_1", "prof_2", "prof_3"]
_FALLBACK_BOOTSTRAP_TOKEN = 151645  # <|im_end|> for Qwen tokenizers


@register("consensus_multi_agent")
class ConsensusAgentLoop(AgentLoopBase):
    """Env-driven multi-agent consensus loop.

    Selects one acting agent per sample (like ``MultiAgentToolAgentLoop``) and
    runs the env's turn loop, reserving a shared global real-turn slot BEFORE
    each generation so concurrent async workers cannot overrun the trainer batch.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt_length = self.rollout_config.prompt_length
        self.response_length = self.rollout_config.response_length
        # 0.8 AgentLoopBase exposes apply_chat_template_kwargs; tool schemas are
        # not wired for this env-driven loop.
        self.tool_schemas = getattr(self, "tool_schemas", None)

    # ------------------------------------------------------------------
    # Prompt construction (ported from the old fork)
    # ------------------------------------------------------------------
    def _build_prompt_ids(self, messages: list[dict[str, Any]]) -> list[int]:
        """Build prompt ids while preserving the initial system prompt when truncating."""
        tokenize_kwargs = dict(self.apply_chat_template_kwargs)
        # We manage truncation ourselves to preserve system prompt + newest turns.
        tokenize_kwargs.pop("truncation", None)
        tokenize_kwargs.pop("max_length", None)

        def _tokenize(msgs: list[dict[str, Any]]) -> list[int]:
            enc = self.tokenizer.apply_chat_template(
                msgs,
                tools=self.tool_schemas,
                add_generation_prompt=True,
                tokenize=True,
                **tokenize_kwargs,
            )
            # transformers 5.x apply_chat_template returns a BatchEncoding dict
            # ({"input_ids": [...], "attention_mask": [...]}); older returned list[int].
            if isinstance(enc, dict) or hasattr(enc, "input_ids"):
                enc = enc["input_ids"]
            # unwrap a possible batch dimension ([[...]] -> [...])
            if enc and isinstance(enc[0], list):
                enc = enc[0]
            return list(enc)

        if not messages:
            return _tokenize(messages)

        has_system = messages[0].get("role") == "system"
        prefix_messages = [messages[0]] if has_system else []
        tail_messages = messages[1:] if has_system else messages

        best_ids: Optional[list[int]] = None
        best_start_idx: Optional[int] = None

        # Start from the shortest candidate and progressively add older turns.
        # This avoids tokenizing the full history first, which can emit long-sequence warnings.
        if has_system:
            # Start at len-1 (system + newest turn), NOT len: a system-only candidate has no
            # user turn and Qwen3.5's chat template raises "No user query found in messages".
            start_indices = range(len(tail_messages) - 1, -1, -1)
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
                                "oldest conversation history dropped (%d -> %d user tokens).",
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
        # Always include the newest user turn: a system-only message list makes Qwen3.5's
        # chat template raise "No user query found in messages".
        if tail_messages:
            minimal_messages = prefix_messages + [tail_messages[-1]]
        else:
            minimal_messages = prefix_messages
        minimal_ids = _tokenize(minimal_messages)
        logger.warning(
            "Minimal prompt still exceeds prompt_length (%d > %d); truncating token IDs as fallback.",
            len(minimal_ids),
            self.prompt_length,
        )
        return minimal_ids[-self.prompt_length:]

    def _detect_loop(self, messages: list[dict[str, Any]]) -> bool:
        """Detect a repetition loop via a ``[Hint:`` marker in the last user message."""
        if not messages:
            return False
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if "[Hint:" in content or "[Hint " in content:
                    return True
                break
        return False

    @staticmethod
    def _flatten_info(info_obj):
        """Normalise agent-keyed info dicts to a flat single-agent info dict."""
        if isinstance(info_obj, dict) and info_obj:
            first_val = next(iter(info_obj.values()))
            if isinstance(first_val, dict) and "active_agent" in first_val:
                return first_val
        return info_obj

    @staticmethod
    def _possible_agents(env) -> list:
        possible_agents = (
            getattr(env, "possible_agents", None)
            or getattr(getattr(env, "env", None), "possible_agents", None)
        )
        if possible_agents:
            return list(possible_agents)
        return list(_DEFAULT_AGENTS)

    # ------------------------------------------------------------------
    # Main env-driven turn loop
    # ------------------------------------------------------------------
    @rollout_trace_op
    async def run(
        self,
        env,
        counter,
        env_idx: int,
        sampling_params: dict[str, Any],
        is_val: bool,
        *,
        global_steps: int = -1,
        epoch: int = -1,
        **kwargs,
    ) -> List[AgentLoopOutput]:
        possible_agents = self._possible_agents(env)

        agent_id = kwargs.get("agent_id")
        if agent_id is None and possible_agents:
            agent_id = possible_agents[env_idx % len(possible_agents)]

        # Reset / resume env, normalising (obs, info) for both legacy Env wrappers
        # and gym-style multi-agent envs.
        if is_val:
            messages, info = env.reset(agent_id=agent_id)
        else:
            messages, info = env.get_last_obs(agent_id=agent_id)
            if not messages:
                messages, info = env.reset(agent_id=agent_id)
        info = self._flatten_info(info)
        if info and info.get("active_agent") is not None:
            agent_id = info.get("active_agent")

        request_id = uuid4().hex
        gen_metrics: dict[str, Any] = {}

        prompt_ids = await self.loop.run_in_executor(
            None,
            lambda: self._build_prompt_ids(messages),
        )

        outputs: List[AgentLoopOutput] = []
        num_turns = 0
        reward: Any = 0.0
        scalar_reward = 0.0
        bootstrap_added = False
        last_prompt_ids = list(prompt_ids)
        # Index into `outputs` of each agent's most recent turn in the CURRENT
        # episode. At episode end, every non-closing agent's terminal utility is
        # routed onto their own last row so each (env, agent) GAE chain sees its
        # own outcome reward.
        episode_last_row: dict[str, int] = {}

        while True:
            # Reserve a real-turn slot BEFORE generation/env.step so concurrent
            # async workers cannot each pass a pre-generation fullness check and
            # overrun gen_batch_size.
            reserved_turn_fills_counter = False
            if not is_val:
                turn_accepted, reserved_turn_fills_counter = await counter.increment.remote()
                if not turn_accepted:
                    break

            with simple_timer("generate_sequences", gen_metrics):
                output = await self.server_manager.generate(
                    request_id=request_id,
                    prompt_ids=prompt_ids,
                    sampling_params=sampling_params,
                    image_data=None,
                )

            response_ids = output.token_ids[: self.response_length]
            response_mask = [1] * len(response_ids)

            assert len(prompt_ids) <= self.prompt_length
            assert len(response_ids) <= self.response_length

            if output.log_probs:
                response_logprobs = list(output.log_probs[: self.response_length])
            else:
                # Keep shapes uniform across the batch when vLLM returns no logprobs.
                response_logprobs = [0.0] * len(response_ids)

            action_text = await self.loop.run_in_executor(
                None,
                lambda: self.tokenizer.decode(response_ids, skip_special_tokens=True),
            )

            # Wrap the action for the multi-agent env. Vote-logprob metadata is
            # stubbed out (instrumentation only) -> metadata={}.
            if agent_id is not None:
                actions = {agent_id: {"text": action_text, "metadata": {}}}
            else:
                actions = action_text

            last_prompt_ids = copy.deepcopy(prompt_ids)
            observation = copy.deepcopy(messages)

            acting_agent_id = agent_id
            messages, reward, terminated, truncated, info = env.step(actions)

            _flat_info = self._flatten_info(info)
            if _flat_info and _flat_info.get("active_agent") is not None:
                agent_id = _flat_info.get("active_agent")

            # Normalise reward / terminated / truncated (dict per-agent or scalar).
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

            # Loop detection retained as a diagnostic (no file writes).
            _ = self._detect_loop(observation)

            # Capture per-episode env metrics into AgentLoopMetrics.env_metrics.
            step_env_metrics = _flat_info.get("metrics", {}) if isinstance(_flat_info, dict) else {}
            turn_metrics = AgentLoopMetrics(
                generate_sequences=gen_metrics.get("generate_sequences", 0.0),
                env_metrics=step_env_metrics or {},
            )

            turn_data = AgentLoopOutput(
                prompt_ids=prompt_ids,
                response_ids=response_ids,
                response_mask=response_mask,
                response_logprobs=response_logprobs,
                metrics=turn_metrics,
                rewards=scalar_reward,
                done=done,
                num_turns=num_turns,
                env_idx=env_idx,
                agent_id=str(acting_agent_id),
                turn_id=num_turns,
            )
            num_turns += 1

            # Record this turn's row. Handle `done` BEFORE the truncation exit so
            # the real closing-action row is always kept.
            if done:
                outputs.append(turn_data)

                # Route every non-closing agent's terminal utility onto their own
                # last turn (an interior row of their GAE chain) and mark it done.
                if isinstance(reward, dict):
                    for other_agent, other_reward in reward.items():
                        if str(other_agent) == str(acting_agent_id):
                            continue
                        row_idx = episode_last_row.get(str(other_agent))
                        if row_idx is not None:
                            outputs[row_idx].rewards += float(other_reward)
                            outputs[row_idx].done = True
                episode_last_row = {}
            else:
                outputs.append(turn_data)
                episode_last_row[str(acting_agent_id)] = len(outputs) - 1

            if reserved_turn_fills_counter and not is_val:
                # Buffer full: append one value-carrier bootstrap row per agent so
                # every (env, agent) chain ends with a strippable terminal row.
                for boot_agent_id in possible_agents:
                    boot_resp_ids = [outputs[-1].response_ids[0]] if outputs and outputs[-1].response_ids else [
                        _FALLBACK_BOOTSTRAP_TOKEN
                    ]
                    bootstrap_turn = AgentLoopOutput(
                        prompt_ids=last_prompt_ids,
                        response_ids=boot_resp_ids,
                        response_mask=[1],
                        response_logprobs=[0.0] * len(boot_resp_ids),
                        metrics=AgentLoopMetrics(),
                        rewards=0.0,
                        done=True,
                        num_turns=num_turns,
                        env_idx=env_idx,
                        agent_id=str(boot_agent_id),
                        turn_id=num_turns,
                    )
                    outputs.append(bootstrap_turn)
                bootstrap_added = True
                break

            if done:
                if is_val:
                    break
                # Training continues filling the shared counter, but the next
                # generation must start from a fresh episode.
                messages, info = env.reset(agent_id=agent_id)
                info = self._flatten_info(info)
                if info and info.get("active_agent") is not None:
                    agent_id = info.get("active_agent")
                prompt_ids = await self.loop.run_in_executor(
                    None,
                    lambda: self._build_prompt_ids(messages),
                )
                continue

            prompt_ids = await self.loop.run_in_executor(
                None,
                lambda: self._build_prompt_ids(messages),
            )

        # Episode completed naturally (not truncated by buffer-full) - append
        # one value-carrier bootstrap row per agent.
        if not bootstrap_added:
            for boot_agent_id in possible_agents:
                # Validation: each agent's bootstrap row carries that agent's OWN
                # terminal utility (val metric reads the last row per (env, agent)).
                if is_val:
                    if isinstance(reward, dict):
                        boot_reward = float(reward.get(boot_agent_id, 0.0))
                    else:
                        boot_reward = scalar_reward
                else:
                    boot_reward = 0.0
                boot_resp_ids = [outputs[-1].response_ids[0]] if outputs and outputs[-1].response_ids else [
                    _FALLBACK_BOOTSTRAP_TOKEN
                ]
                bootstrap_turn = AgentLoopOutput(
                    prompt_ids=last_prompt_ids,
                    response_ids=boot_resp_ids,
                    response_mask=[1],
                    response_logprobs=[0.0] * len(boot_resp_ids),
                    metrics=AgentLoopMetrics(),
                    rewards=boot_reward,
                    done=True,
                    num_turns=num_turns,
                    env_idx=env_idx,
                    agent_id=str(boot_agent_id),
                    turn_id=num_turns,
                )
                outputs.append(bootstrap_turn)

        return outputs
