"""Check binary success through the real environment and VERL factory."""

import importlib.util
import sys
import types
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[2]
HIRING = ROOT / "verl/envs/hiring_env"
sys.modules.setdefault("verl", types.ModuleType("verl"))
sys.modules.setdefault("verl.envs", types.ModuleType("verl.envs"))
package = types.ModuleType("verl.envs.hiring_env")
package.__path__ = [str(HIRING)]
sys.modules["verl.envs.hiring_env"] = package


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_load("verl.envs.hiring_env.env", HIRING / "env.py")
wrapper_module = _load(
    "verl.envs.hiring_env_wrapper", ROOT / "verl/envs/hiring_env_wrapper.py"
)


def _make_env(**overrides):
    config = {
        "professor_ids": ["prof_a", "prof_b", "prof_c"],
        "students_per_batch": 3,
        "token_budget": 500,
        "feature_dim": 3,
        "vote_threshold": 0.5,
        "seed": 7,
        "reward_mode": "binary_social_optimum",
        "format_penalty": 0,
        "invalid_action_penalty": 0,
    }
    config.update(overrides)
    wrapped = wrapper_module.make_async_ticker_env(config)
    wrapped.reset()
    env = wrapped.env
    env.student_batch = [
        {
            "index": i,
            "id": f"student_{i}",
            "name": f"Student {i}",
            "profile_vector": np.eye(3)[i].tolist(),
        }
        for i in range(3)
    ]
    env.professor_interests = {
        "prof_a": np.array([3.0, 2.0, 1.0]),
        "prof_b": np.array([3.0, 2.0, 1.0]),
        "prof_c": np.array([2.0, 3.0, 1.0]),
    }
    return wrapped


@pytest.mark.parametrize("choice, expected", [(0, 1.0), (1, 0.0), (2, 0.0)])
def test_consensus_rewards_and_logged_welfare(choice, expected):
    wrapped = _make_env()
    _, rewards, done, _, _ = wrapped.step(
        {"prof_a": f"<THINK>choice</THINK><VOTE>{choice}</VOTE>"}
    )
    assert rewards == dict.fromkeys(wrapped.env.professor_ids, 0.0)
    assert not any(done.values())
    _, rewards, done, _, info = wrapped.step(
        {"prof_b": f"<THINK>agree</THINK><VOTE>{choice}</VOTE>"}
    )
    assert all(done.values())
    # Also rewards prof_c, who has not acted before majority consensus.
    assert rewards == dict.fromkeys(wrapped.env.professor_ids, expected)
    recorded = info["prof_a"]
    assert recorded["agent_rewards"] == rewards
    assert recorded["episode_metrics"]["social_welfare"]["actual_total_utility"] == [8, 7, 3][choice]


def test_any_exact_welfare_tie_succeeds():
    wrapped = _make_env()
    wrapped.env.professor_interests["prof_c"] = np.array([1.0, 3.0, 2.0])
    wrapped.env.episode_state.update(consensus_reached=True, consensus_choice=1)
    assert wrapped.env._calculate_rewards() == dict.fromkeys(wrapped.env.professor_ids, 1.0)


def test_near_optimum_does_not_succeed_even_if_displayed_utilities_tie():
    wrapped = _make_env()
    wrapped.env.student_batch[1]["profile_vector"] = [1 - 1e-8, 1e-8, 0]
    wrapped.env.episode_state.update(consensus_reached=True, consensus_choice=1)
    assert wrapped.env._calculate_rewards() == dict.fromkeys(wrapped.env.professor_ids, 0.0)


@pytest.mark.parametrize("choice", [None, -1, 3])
def test_invalid_final_choice_cannot_succeed(choice):
    wrapped = _make_env()
    wrapped.env.episode_state.update(consensus_reached=True, consensus_choice=choice)
    assert wrapped.env._calculate_rewards() == dict.fromkeys(wrapped.env.professor_ids, 0.0)


def test_timeout_without_consensus_and_invalid_action_have_zero_reward():
    wrapped = _make_env(max_steps=1)
    _, rewards, done, _, _ = wrapped.step(
        {"prof_a": "<THINK>invalid</THINK><VOTE>99</VOTE>"}
    )
    assert all(done.values())
    assert not wrapped.env.episode_state["consensus_reached"]
    assert rewards == dict.fromkeys(wrapped.env.professor_ids, 0.0)


@pytest.mark.parametrize("penalty", ["format_penalty", "invalid_action_penalty"])
def test_binary_mode_rejects_auxiliary_environment_rewards(penalty):
    with pytest.raises(ValueError, match="strictly binary"):
        _make_env(**{penalty: 0.1})


def test_vanilla_reward_is_unchanged():
    wrapped = _make_env(reward_mode="individual")
    assert type(wrapped.env) is wrapper_module.AsyncTickerAdmissionsEnv
    wrapped.env.episode_state.update(consensus_reached=True, consensus_choice=0)
    assert wrapped.env._calculate_rewards() == {"prof_a": 3.0, "prof_b": 3.0, "prof_c": 2.0}
