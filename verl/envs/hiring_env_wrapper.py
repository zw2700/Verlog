# verl/envs/hiring_env_wrapper.py
"""
Wrapper for hiring_env submodule to integrate with VERL framework.
"""

from __future__ import annotations

import copy
import random
from typing import Any

import gym


CRITIC_PROBE_MODES = {"off", "visible", "hidden"}
CRITIC_PROBE_PROMPT = (
    "CRITIC SANITY CHECK: Your terminal reward for this episode will be {target:+.1f}. "
    "This reward is fixed and does not depend on your actions."
)


def _active_agent(info: Any) -> str | None:
    if not isinstance(info, dict):
        return None
    if info.get("active_agent") is not None:
        return str(info["active_agent"])
    for value in info.values():
        if isinstance(value, dict) and value.get("active_agent") is not None:
            return str(value["active_agent"])
    return None


def _append_probe_prompt(observation: Any, target: float) -> Any:
    """Append the probe target to one professor observation without mutating the env object."""
    suffix = CRITIC_PROBE_PROMPT.format(target=target)
    observation = copy.deepcopy(observation)

    if isinstance(observation, str):
        return f"{observation}\n\n{suffix}"

    if isinstance(observation, list):
        for message in reversed(observation):
            if isinstance(message, dict) and message.get("role") == "user":
                message["content"] = f"{message.get('content', '')}\n\n{suffix}"
                return observation
        observation.append({"role": "user", "content": suffix})
        return observation

    if isinstance(observation, dict):
        if "prompt" in observation:
            observation["prompt"] = _append_probe_prompt(observation["prompt"], target)
            return observation
        if "messages" in observation:
            observation["messages"] = _append_probe_prompt(observation["messages"], target)
            return observation

    raise TypeError(f"Unsupported hiring observation type for critic probe: {type(observation).__name__}")


class AsyncTickerEnvWrapper(gym.Wrapper):
    """
    VERL wrapper for AsyncTickerAdmissionsEnv.

    Handles:
    - Observation caching for get_last_obs()
    - Auto-reset logic
    - Episode state management
    - Integration with VERL training loops
    """

    def __init__(
        self,
        env: Any,
        critic_probe_mode: str = "off",
        critic_probe_seed: int | None = None,
    ):
        super().__init__(env)
        if critic_probe_mode not in CRITIC_PROBE_MODES:
            raise ValueError(
                f"critic_probe_mode must be one of {sorted(CRITIC_PROBE_MODES)}, got {critic_probe_mode!r}"
            )
        self.last_obs = None
        self.last_info = None
        self.episode_done = False
        self.critic_probe_mode = critic_probe_mode
        self._critic_probe_rng = random.Random(critic_probe_seed)
        self._critic_probe_targets: dict[str, float] = {}

        professor_ids = getattr(env, "professor_ids", None) or getattr(env, "possible_agents", None) or []
        self.professor_ids = [str(professor_id) for professor_id in professor_ids]
        if self.critic_probe_mode != "off" and not self.professor_ids:
            raise ValueError("critic probe requires the hiring env to expose professor_ids or possible_agents")

    def _sample_critic_probe_targets(self) -> None:
        self._critic_probe_targets = {
            professor_id: self._critic_probe_rng.choice((-1.0, 1.0)) for professor_id in self.professor_ids
        }

    def _decorate_probe_observation(self, observation: Any, info: Any) -> Any:
        if self.critic_probe_mode != "visible":
            return observation

        if isinstance(observation, dict) and any(
            professor_id in observation for professor_id in self._critic_probe_targets
        ):
            observation = copy.deepcopy(observation)
            for professor_id, target in self._critic_probe_targets.items():
                if professor_id in observation:
                    observation[professor_id] = _append_probe_prompt(observation[professor_id], target)
            return observation

        active_agent = _active_agent(info)
        if active_agent not in self._critic_probe_targets:
            raise ValueError(f"critic probe could not identify active professor from info: {info!r}")
        return _append_probe_prompt(observation, self._critic_probe_targets[active_agent])

    def _decorate_probe_info(self, info: Any) -> Any:
        if self.critic_probe_mode == "off":
            return info
        if not isinstance(info, dict):
            raise TypeError(f"critic probe expected dict info, got {type(info).__name__}")

        info = copy.deepcopy(info)
        agent_keyed = any(
            professor_id in info and isinstance(info[professor_id], dict) for professor_id in self.professor_ids
        )
        if agent_keyed:
            for professor_id in self.professor_ids:
                if professor_id not in info or not isinstance(info[professor_id], dict):
                    continue
                info[professor_id]["critic_probe_target"] = self._critic_probe_targets[professor_id]
                info[professor_id]["critic_probe_targets"] = dict(self._critic_probe_targets)
        else:
            active_agent = _active_agent(info)
            info["critic_probe_targets"] = dict(self._critic_probe_targets)
            if active_agent in self._critic_probe_targets:
                info["critic_probe_target"] = self._critic_probe_targets[active_agent]
        return info

    def _zero_probe_rewards(self) -> dict[str, float]:
        return {professor_id: 0.0 for professor_id in self.professor_ids}

    def get_last_obs(self, agent_id=None):
        """Return last observation (used by VERL for resuming after reset).

        `agent_id` is accepted for compatibility with verl's tool_agent_loop /
        multi_tool_agent_loop, which always pass it through. The hiring env
        manages active-agent selection internally (info["active_agent"]), so
        we ignore the hint here.
        """
        return self.last_obs, self.last_info

    def get_observation_for_agent(self, agent_id: str) -> Any:
        """Build the current actor-visible observation for one professor.

        Bootstrap value rows are evaluated after the final real action in a
        rollout fragment. They therefore need each professor's current state,
        not a copy of whichever professor happened to act last.
        """
        agent_id = str(agent_id)
        if agent_id not in self.professor_ids:
            raise ValueError(f"unknown professor id {agent_id!r}")
        observation = self.env._build_chat_messages(agent_id)
        if self.critic_probe_mode == "visible":
            observation = _append_probe_prompt(observation, self._critic_probe_targets[agent_id])
        return observation

    def get_critic_context(self) -> dict[str, Any]:
        """Return deterministic privileged state approved for critic prompts."""
        utilities = self.env._get_student_utilities_by_agent()
        return {
            "professor_ids": list(self.professor_ids),
            "student_utilities": {
                professor_id: [float(value) for value in utilities[professor_id]]
                for professor_id in self.professor_ids
            },
        }

    def reset(self, agent_id=None, **kwargs):
        """Reset environment and cache initial observation.

        `agent_id` is accepted for verl agent-loop compatibility but dropped
        before delegating: AsyncTickerAdmissionsEnv.reset() takes no args and
        picks `active_agent` itself.
        """
        obs, info = self.env.reset(**kwargs)
        if self.critic_probe_mode != "off":
            self._sample_critic_probe_targets()
            obs = self._decorate_probe_observation(obs, info)
            info = self._decorate_probe_info(info)
        self.last_obs = obs
        self.last_info = info
        self.episode_done = False
        return obs, info

    def step(self, action):
        """Step environment with auto-reset on termination."""
        # If episode already done, auto-reset
        if self.episode_done:
            obs, info = self.reset()
            reward = self._zero_probe_rewards() if self.critic_probe_mode != "off" else 0.0
            return obs, reward, False, False, info

        obs, reward, terminated, truncated, info = self.env.step(action)

        # Track episode status
        # NOTE: terminated/truncated may be per-agent dicts; a non-empty dict is
        # always truthy, so check actual values — not the dict itself.
        scalar_term = any(terminated.values()) if isinstance(terminated, dict) else bool(terminated)
        scalar_trunc = any(truncated.values()) if isinstance(truncated, dict) else bool(truncated)
        if scalar_term or scalar_trunc:
            self.episode_done = True

        if self.critic_probe_mode != "off":
            if not self.episode_done:
                obs = self._decorate_probe_observation(obs, info)
            info = self._decorate_probe_info(info)
            reward = dict(self._critic_probe_targets) if self.episode_done else self._zero_probe_rewards()

        # Cache for get_last_obs()
        self.last_obs = obs
        self.last_info = info

        return obs, reward, terminated, truncated, info


def make_async_ticker_env(config: dict[str, Any], tokenizer=None) -> AsyncTickerEnvWrapper:
    """
    Factory function to create wrapped AsyncTickerAdmissionsEnv.

    Args:
        config: Environment configuration dict with keys:
            - professor_ids: List[str]
            - students_per_batch: int
            - token_budget: int
            - feature_dim: int (default 5)
            - vote_threshold: float (default 0.5)
            - max_steps: int (optional)
            - reward_mode: str ("individual"/"group"/"combined")
            - reward_alpha: float (for "combined" mode)
            - system_prompt: str or Dict[str, str]
            - prompt_length: int (optional, for token-based truncation)
            - max_prompt_words: int (optional, for word-based truncation)
            - seed: int (optional)
            - critic_probe_mode: "off", "visible", or "hidden"
            - critic_probe_seed: Optional deterministic probe target seed
        tokenizer: Optional tokenizer for prompt truncation

    Returns:
        Wrapped environment ready for VERL training
    """
    from verl.envs.hiring_env.env import AsyncTickerAdmissionsEnv

    env_config = dict(config)
    critic_probe_mode = str(env_config.pop("critic_probe_mode", "off"))
    critic_probe_seed = env_config.pop("critic_probe_seed", None)
    env = AsyncTickerAdmissionsEnv(env_config, tokenizer=tokenizer)
    return AsyncTickerEnvWrapper(
        env,
        critic_probe_mode=critic_probe_mode,
        critic_probe_seed=critic_probe_seed,
    )
