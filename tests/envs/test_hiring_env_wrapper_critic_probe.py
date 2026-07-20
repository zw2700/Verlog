import copy

import gym
import pytest

from verl.envs.hiring_env_wrapper import AsyncTickerEnvWrapper


class _FakeHiringEnv(gym.Env):
    professor_ids = ["prof_1", "prof_2", "prof_3"]
    possible_agents = professor_ids

    def __init__(self):
        super().__init__()
        self._step = 0

    @staticmethod
    def _messages(agent_id):
        return [
            {"role": "system", "content": f"You are {agent_id}."},
            {"role": "user", "content": "Choose a student."},
        ]

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._step = 0
        return self._messages("prof_1"), {"active_agent": "prof_1"}

    def step(self, action):
        self._step += 1
        if self._step == 1:
            return (
                self._messages("prof_2"),
                {agent: 9.0 for agent in self.professor_ids},
                False,
                False,
                {"active_agent": "prof_2"},
            )
        return None, {agent: 9.0 for agent in self.professor_ids}, True, False, {"active_agent": "prof_3"}


def _last_user_content(messages):
    return next(message["content"] for message in reversed(messages) if message["role"] == "user")


def test_visible_probe_adds_target_and_replaces_all_environment_rewards():
    wrapper = AsyncTickerEnvWrapper(_FakeHiringEnv(), critic_probe_mode="visible", critic_probe_seed=7)

    messages, info = wrapper.reset()
    targets = info["critic_probe_targets"]
    assert set(targets) == set(wrapper.professor_ids)
    assert set(targets.values()) <= {-1.0, 1.0}
    assert f"{targets['prof_1']:+.1f}" in _last_user_content(messages)

    next_messages, reward, terminated, truncated, next_info = wrapper.step({"prof_1": "anything"})
    assert not terminated
    assert not truncated
    assert reward == {agent: 0.0 for agent in wrapper.professor_ids}
    assert next_info["critic_probe_targets"] == targets
    assert f"{targets['prof_2']:+.1f}" in _last_user_content(next_messages)

    _, reward, terminated, truncated, terminal_info = wrapper.step({"prof_2": "anything"})
    assert terminated
    assert not truncated
    assert reward == targets
    assert terminal_info["critic_probe_targets"] == targets


def test_hidden_probe_replaces_rewards_without_changing_prompt():
    env = _FakeHiringEnv()
    expected_messages, _ = env.reset()
    wrapper = AsyncTickerEnvWrapper(env, critic_probe_mode="hidden", critic_probe_seed=11)

    messages, info = wrapper.reset()
    targets = copy.deepcopy(info["critic_probe_targets"])
    assert messages == expected_messages

    wrapper.step({"prof_1": "anything"})
    _, reward, terminated, _, _ = wrapper.step({"prof_2": "anything"})
    assert terminated
    assert reward == targets


def test_probe_rejects_unknown_mode():
    with pytest.raises(ValueError, match="critic_probe_mode"):
        AsyncTickerEnvWrapper(_FakeHiringEnv(), critic_probe_mode="surprise")
