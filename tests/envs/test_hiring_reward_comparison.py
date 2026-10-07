"""Exercise all reward conditions through real majority-vote transitions."""
import importlib.util
import sys
import types
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for name, path in [("verl", ROOT / "verl"), ("verl.envs", ROOT / "verl/envs"),
                   ("verl.envs.hiring_env", ROOT / "verl/envs/hiring_env")]:
    package = sys.modules.setdefault(name, types.ModuleType(name))
    package.__path__ = [str(path)]

from verl.envs.hiring_env_wrapper import make_async_ticker_env

MODES = ["individual", "group", "binary_individual", "binary_social_optimum"]
AGENTS = ["prof_a", "prof_b", "prof_c"]


def make_env(mode, **overrides):
    config = dict(professor_ids=AGENTS, students_per_batch=3, token_budget=500,
                  feature_dim=3, vote_threshold=0.5, max_steps=50, seed=7,
                  reward_mode=mode, reward_optimum_atol=1e-9,
                  format_penalty=0.1, invalid_action_penalty=0.1)
    config.update(overrides)
    wrapped = make_async_ticker_env(config)
    wrapped.reset()
    wrapped.env.student_batch = [dict(index=i, id=f"student_{i}", name=f"Student {i}",
                                      profile_vector=np.eye(3)[i].tolist()) for i in range(3)]
    wrapped.env.professor_interests = {
        "prof_a": np.array([3., 2., 1.]), "prof_b": np.array([3., 2., 1.]),
        "prof_c": np.array([2., 3., 1.]),
    }
    return wrapped


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("choice", [0, 1, 2])
def test_consensus_rewards_and_welfare_logs(mode, choice):
    wrapped = make_env(mode)
    _, rewards, done, _, _ = wrapped.step({"prof_a": f"<THINK>x</THINK><VOTE>{choice}</VOTE>"})
    assert rewards == dict.fromkeys(AGENTS, 0.)
    assert not any(done.values())
    _, rewards, done, _, info = wrapped.step({"prof_b": f"<THINK>x</THINK><VOTE>{choice}</VOTE>"})
    numerical = [[3., 3., 2.], [2., 2., 3.], [1., 1., 1.]][choice]
    expected = {"individual": numerical, "group": [sum(numerical)] * 3,
                "binary_individual": [[1., 1., 0.], [0., 0., 1.], [0., 0., 0.]][choice],
                "binary_social_optimum": [float(choice == 0)] * 3}[mode]
    assert all(done.values())
    assert rewards == dict(zip(AGENTS, expected))
    assert info["prof_a"]["agent_rewards"] == rewards
    assert info["prof_a"]["episode_metrics"]["social_welfare"]["actual_total_utility"] == sum(numerical)
    assert info["prof_a"]["metrics"]["outcome/chosen_student_rank_global"] == choice + 1


@pytest.mark.parametrize("mode", MODES)
def test_failed_agreement_and_same_action_penalties(mode):
    wrapped = make_env(mode, max_steps=1)
    _, rewards, done, _, _ = wrapped.step({"prof_a": "<THINK>x</THINK><VOTE>0</VOTE>"})
    assert all(done.values())
    assert rewards == dict.fromkeys(AGENTS, 0.)
    wrapped = make_env(mode)
    _, rewards, done, _, _ = wrapped.step({"prof_a": "<THINK>x</THINK><VOTE>99</VOTE>"})
    assert rewards == {"prof_a": -0.1, "prof_b": 0., "prof_c": 0.}
    assert not any(done.values())


@pytest.mark.parametrize("mode", ["binary_individual", "binary_social_optimum"])
@pytest.mark.parametrize("distance,success", [(1e-15, True), (1e-7, False)])
def test_roundoff_ties_succeed_but_close_nonoptima_do_not(mode, distance, success):
    wrapped = make_env(mode)
    env = wrapped.env
    env.student_batch[1]["profile_vector"] = [1-distance, distance, 0.]
    env.episode_state.update(consensus_reached=True, consensus_choice=1)
    expected = dict.fromkeys(AGENTS, float(success))
    if mode == "binary_individual":
        # In this fixture professor c prefers candidate 1 even after replacement.
        expected["prof_c"] = 1.
    assert env._calculate_rewards() == expected
    metrics = env._calculate_episode_metrics(env._calculate_rewards())
    if mode == "binary_social_optimum":
        assert (metrics["outcome_quality"]["chosen_student_rank_global"] == 1) == success


@pytest.mark.parametrize("mode", ["binary_individual", "binary_social_optimum"])
@pytest.mark.parametrize("choice", [None, -1, 3])
def test_invalid_terminal_choice_cannot_earn_binary_reward(mode, choice):
    env = make_env(mode).env
    env.episode_state.update(consensus_reached=True, consensus_choice=choice)
    assert env._calculate_rewards() == dict.fromkeys(AGENTS, 0.)


def test_rewards_do_not_change_observations_or_action_rules():
    observations = [make_env(mode).env._build_chat_messages("prof_a") for mode in MODES]
    assert all(obs == observations[0] for obs in observations)


def test_ordinary_factory_keeps_original_environment():
    from verl.envs.hiring_env.env import AsyncTickerAdmissionsEnv
    wrapped = make_async_ticker_env(dict(professor_ids=AGENTS, students_per_batch=3,
                                        feature_dim=3, token_budget=500))
    assert type(wrapped.env) is AsyncTickerAdmissionsEnv
