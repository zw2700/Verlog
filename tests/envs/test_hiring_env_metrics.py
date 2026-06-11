import math
import os
import sys
import types
import importlib.util

import numpy as np


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
HIRING_ENV_DIR = os.path.join(REPO_ROOT, "verl/envs/hiring_env")

# Load the hiring env without importing top-level verl, which may require
# optional distributed-training dependencies unrelated to these env metrics.
sys.modules.setdefault("verl", types.ModuleType("verl"))
sys.modules.setdefault("verl.envs", types.ModuleType("verl.envs"))
hiring_pkg = types.ModuleType("verl.envs.hiring_env")
hiring_pkg.__path__ = [HIRING_ENV_DIR]
sys.modules["verl.envs.hiring_env"] = hiring_pkg

spec = importlib.util.spec_from_file_location(
    "verl.envs.hiring_env.env",
    os.path.join(HIRING_ENV_DIR, "env.py"),
)
hiring_env_module = importlib.util.module_from_spec(spec)
sys.modules["verl.envs.hiring_env.env"] = hiring_env_module
spec.loader.exec_module(hiring_env_module)
AsyncTickerAdmissionsEnv = hiring_env_module.AsyncTickerAdmissionsEnv


def _make_env():
    env = AsyncTickerAdmissionsEnv({
        "professor_ids": ["prof_a", "prof_b", "prof_c"],
        "students_per_batch": 3,
        "token_budget": 100,
        "feature_dim": 3,
        "vote_threshold": 1.0,
        "seed": 7,
    })
    env.reset()
    env.student_batch = [
        {"index": 0, "id": "student_0", "name": "Student 0", "profile_vector": [1.0, 0.0, 0.0]},
        {"index": 1, "id": "student_1", "name": "Student 1", "profile_vector": [0.0, 1.0, 0.0]},
        {"index": 2, "id": "student_2", "name": "Student 2", "profile_vector": [0.0, 0.0, 1.0]},
    ]
    env.professor_interests = {
        "prof_a": np.array([3.0, 2.0, 1.0]),
        "prof_b": np.array([3.0, 2.0, 1.0]),
        "prof_c": np.array([1.0, 3.0, 2.0]),
    }
    return env


def _metrics(env):
    rewards = env._calculate_rewards()
    metrics = env._calculate_episode_metrics(rewards)
    return metrics, env._flatten_metrics_for_logging(metrics)


def test_outcome_quality_and_satisfaction_metrics_for_final_choice():
    env = _make_env()
    env.episode_state["consensus_reached"] = True
    env.episode_state["consensus_choice"] = 2

    metrics, flat = _metrics(env)

    assert metrics["outcome_quality"]["has_final_choice"] == 1
    assert metrics["outcome_quality"]["chosen_student_rank_global"] == 3
    assert metrics["outcome_quality"]["pareto_dominated_choice"] == 1

    satisfaction = metrics["individual_satisfaction"]
    assert satisfaction["by_agent"]["prof_a"]["final_choice_rank"] == 3
    assert math.isclose(satisfaction["by_agent"]["prof_b"]["regret"], 2.0)
    assert math.isclose(satisfaction["by_agent"]["prof_c"]["normalized_regret"], 1.0 / 3.0)
    assert math.isclose(satisfaction["final_choice_rank_variance"], 2.0 / 9.0)

    assert flat["outcome/has_final_choice"] == 1
    assert flat["outcome/chosen_student_rank_global"] == 3
    assert flat["outcome/pareto_dominated_choice"] == 1
    assert flat["satisfaction/prof_a/final_choice_rank"] == 3


def test_rank_metrics_treat_utility_ties_as_same_rank():
    env = _make_env()
    env.episode_state["consensus_reached"] = True
    env.episode_state["consensus_choice"] = 1

    metrics, flat = _metrics(env)

    assert metrics["outcome_quality"]["has_final_choice"] == 1
    assert metrics["social_welfare"]["actual_total_utility"] == metrics["social_welfare"]["optimal_total_utility"]
    assert metrics["outcome_quality"]["chosen_student_rank_global"] == 1
    assert metrics["individual_satisfaction"]["by_agent"]["prof_a"]["final_choice_rank"] == 2
    assert metrics["individual_satisfaction"]["by_agent"]["prof_b"]["final_choice_rank"] == 2
    assert metrics["individual_satisfaction"]["by_agent"]["prof_c"]["final_choice_rank"] == 1
    assert math.isclose(
        metrics["individual_satisfaction"]["final_choice_rank_variance"],
        2.0 / 9.0,
    )

    assert flat["outcome/chosen_student_rank_global"] == 1
    assert flat["satisfaction/prof_c/final_choice_rank"] == 1


def test_new_metrics_use_sentinels_without_final_choice():
    env = _make_env()
    env.episode_state["consensus_reached"] = False
    env.episode_state["consensus_choice"] = None

    metrics, flat = _metrics(env)

    assert metrics["outcome_quality"]["has_final_choice"] == 0
    assert metrics["outcome_quality"]["chosen_student_rank_global"] is None
    assert metrics["outcome_quality"]["pareto_dominated_choice"] is None
    assert metrics["individual_satisfaction"]["final_choice_rank_variance"] is None
    assert metrics["individual_satisfaction"]["by_agent"]["prof_a"]["regret"] is None
    assert metrics["individual_satisfaction"]["by_agent"]["prof_a"]["normalized_regret"] is None
    assert metrics["influence"]["leader_success"] is None
    assert metrics["vote_change_quality"]["global_rank_delta_mean"] == 0.0
    assert metrics["vote_justification"]["vote_with_group_justification_rate"] == 0.0
    assert metrics["communication_process"]["argument_repetition_rate"] == 0.0
    assert metrics["communication_process"]["new_student_mentions_rate"] == 0.0
    assert metrics["communication_process"]["consensus_language_rate"] == 0.0
    assert flat["outcome/has_final_choice"] == 0
    assert flat["outcome/chosen_student_rank_global"] is None
    assert flat["outcome/pareto_dominated_choice"] is None
    assert flat["satisfaction/final_choice_rank_variance"] is None
    assert flat["satisfaction/prof_a/regret"] is None
    assert flat["satisfaction/prof_a/normalized_regret"] is None
    assert flat["influence/leader_success"] is None


def test_voting_dynamics_and_influence_metrics_from_history():
    env = _make_env()
    env.episode_state["consensus_reached"] = True
    env.episode_state["consensus_choice"] = 1
    env.episode_state["votes"] = {"prof_a": 1, "prof_b": 1, "prof_c": 1}

    env.history_manager.add_public(
        "prof_a",
        "<GROUP>I propose Student 2</GROUP>",
        ticker_time=1,
        token_count=4,
        message_type="communication",
    )
    env.history_manager.add_public(
        "prof_a",
        "<VOTE>2</VOTE>",
        ticker_time=1,
        token_count=1,
        message_type="vote",
        extra_fields={"choice": 2},
    )
    env.history_manager.add_public(
        "prof_b",
        "<VOTE>1</VOTE>",
        ticker_time=2,
        token_count=1,
        message_type="vote",
        extra_fields={"choice": 1},
    )
    env.history_manager.add_public(
        "prof_a",
        "<VOTE>1</VOTE>",
        ticker_time=3,
        token_count=1,
        message_type="vote",
        extra_fields={"choice": 1},
    )
    env.history_manager.add_public(
        "prof_c",
        "<VOTE>2</VOTE>",
        ticker_time=4,
        token_count=1,
        message_type="vote",
        extra_fields={"choice": 2},
    )
    env.history_manager.add_public(
        "prof_c",
        "<VOTE>1</VOTE>",
        ticker_time=5,
        token_count=1,
        message_type="vote",
        extra_fields={"choice": 1},
    )

    metrics, flat = _metrics(env)
    voting = metrics["voting_dynamics"]
    influence = metrics["influence"]
    vote_change_quality = metrics["vote_change_quality"]
    vote_justification = metrics["vote_justification"]

    assert voting["total_vote_changes"] == 2
    assert voting["by_agent"]["prof_a"]["vote_changes"] == 1
    assert voting["by_agent"]["prof_c"]["vote_changes"] == 1
    assert voting["by_agent"]["prof_a"]["first_vote_turn"] == 1
    assert voting["by_agent"]["prof_c"]["first_vote_turn"] == 4
    assert voting["by_agent"]["prof_c"]["final_vote_turn"] == 5
    assert voting["by_agent"]["prof_a"]["vote_without_discussion"] == 0
    assert voting["by_agent"]["prof_b"]["vote_without_discussion"] == 1
    assert voting["minority_persistence_total"] == 1
    assert voting["by_agent"]["prof_c"]["minority_persistence"] == 1

    assert influence["leader_agent"] == "prof_a"
    assert influence["leader_agent_index"] == 0
    assert influence["leader_student"] == 2
    assert influence["leader_success"] == 0
    assert influence["votes_adopted_from_plurality_count"] == 1
    assert math.isclose(influence["votes_adopted_from_plurality_rate"], 1.0 / 3.0)
    assert influence["votes_adopted_from_plurality_ambiguous"] == 2
    assert influence["vote_changes_to_plurality_count"] == 1
    assert influence["vote_changes_to_plurality_ambiguous"] == 1
    assert math.isclose(influence["vote_changes_to_plurality_rate"], 1.0)

    assert math.isclose(vote_change_quality["global_rank_delta_mean"], 2.0)
    assert math.isclose(vote_change_quality["collective_utility_delta_mean"], 3.0)
    assert math.isclose(vote_change_quality["agent_utility_delta_mean"], 1.0)
    assert math.isclose(vote_change_quality["improves_global_rank_rate"], 1.0)
    assert math.isclose(vote_change_quality["improves_collective_utility_rate"], 1.0)
    assert math.isclose(vote_change_quality["improves_agent_utility_rate"], 1.0)

    assert vote_justification["vote_with_group_justification_count"] == 1
    assert math.isclose(vote_justification["vote_with_group_justification_rate"], 1.0 / 5.0)
    assert math.isclose(
        vote_justification["by_agent"]["prof_a"]["vote_with_group_justification_rate"],
        0.5,
    )
    assert vote_justification["by_agent"]["prof_b"]["vote_with_group_justification_rate"] == 0.0

    assert flat["voting/total_vote_changes"] == 2
    assert flat["voting/prof_c/minority_persistence"] == 1
    assert math.isclose(flat["voting/vote_change_global_rank_delta_mean"], 2.0)
    assert math.isclose(flat["voting/vote_with_group_justification_rate"], 1.0 / 5.0)
    assert flat["influence/leader_agent_index"] == 0
    assert flat["influence/vote_changes_to_plurality_count"] == 1


def test_minority_persistence_counts_silent_terminal_minority_voter():
    env = _make_env()
    env.episode_state["consensus_reached"] = True
    env.episode_state["consensus_choice"] = 1
    env.episode_state["votes"] = {"prof_a": 0, "prof_b": 1, "prof_c": 1}

    env.history_manager.add_public(
        "prof_a",
        "<VOTE>0</VOTE>",
        ticker_time=1,
        token_count=1,
        message_type="vote",
        extra_fields={"choice": 0},
    )
    env.history_manager.add_public(
        "prof_b",
        "<VOTE>1</VOTE>",
        ticker_time=2,
        token_count=1,
        message_type="vote",
        extra_fields={"choice": 1},
    )
    env.history_manager.add_public(
        "prof_c",
        "<VOTE>1</VOTE>",
        ticker_time=3,
        token_count=1,
        message_type="vote",
        extra_fields={"choice": 1},
    )

    metrics, flat = _metrics(env)

    assert metrics["voting_dynamics"]["by_agent"]["prof_a"]["minority_persistence"] == 1
    assert metrics["voting_dynamics"]["minority_persistence_total"] == 1
    assert flat["voting/prof_a/minority_persistence"] == 1


def test_communication_process_metrics_from_group_messages():
    env = _make_env()

    env.history_manager.add_public(
        "prof_a",
        "<GROUP>Student 0 is best because systems fit.</GROUP>",
        ticker_time=1,
        token_count=7,
        message_type="communication",
    )
    env.history_manager.add_public(
        "prof_b",
        "<GROUP>I can support Student 1 for consensus.</GROUP>",
        ticker_time=2,
        token_count=7,
        message_type="communication",
    )
    env.history_manager.add_public(
        "prof_a",
        "<GROUP>Student 2 is best because systems fit.</GROUP>",
        ticker_time=3,
        token_count=7,
        message_type="communication",
    )

    metrics, flat = _metrics(env)
    process = metrics["communication_process"]

    assert process["repetitive_messages"] == 1
    assert process["repetition_comparisons"] == 1
    assert math.isclose(process["argument_repetition_rate"], 1.0)
    assert math.isclose(process["by_agent"]["prof_a"]["argument_repetition_rate"], 1.0)
    assert process["by_agent"]["prof_a"]["max_repetition_streak"] == 1
    assert process["by_agent"]["prof_b"]["argument_repetition_rate"] == 0.0

    assert process["new_student_mentions_count"] == 3
    assert process["distinct_students_discussed"] == 3
    assert math.isclose(process["new_student_mentions_rate"], 1.0)

    assert process["consensus_language_messages"] == 1
    assert math.isclose(process["consensus_language_rate"], 1.0 / 3.0)
    assert math.isclose(process["by_agent"]["prof_b"]["consensus_language_rate"], 1.0)
    assert process["by_agent"]["prof_a"]["consensus_language_rate"] == 0.0

    assert math.isclose(flat["communication/argument_repetition_rate"], 1.0)
    assert flat["communication/new_student_mentions_count"] == 3
    assert flat["communication/distinct_students_discussed"] == 3
    assert math.isclose(flat["communication/consensus_language_rate"], 1.0 / 3.0)
    assert flat["communication/prof_a/max_repetition_streak"] == 1


def test_proposal_detection_ignores_ambiguous_multiple_students():
    env = _make_env()

    assert env._detect_proposed_student("I recommend Student 1") == 1
    assert env._detect_proposed_student("Student 1 has high AI/ML") is None
    assert env._detect_proposed_student(
        "I recommend Student 1, but we should vote for Student 2"
    ) is None
