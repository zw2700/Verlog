import math

from verl.experimental.agent_loop.agent_loop import aggregate_env_metrics


def test_aggregate_env_metrics_adds_step_level_counts_and_rates():
    stats = aggregate_env_metrics(
        [
            {
                "negotiation/consensus_reached": 1,
                "outcome/chosen_student_rank_global": 1,
                "communication/total_messages": 2,
            },
            {
                "negotiation/consensus_reached": 1,
                "outcome/chosen_student_rank_global": 2,
                "communication/total_messages": 4,
            },
            {
                "negotiation/consensus_reached": 0,
                "outcome/chosen_student_rank_global": None,
                "communication/total_messages": 6,
            },
        ]
    )

    assert stats["env/step/episodes_rolled_out"] == 3.0
    assert stats["env/step/episodes_consensus"] == 2.0
    assert stats["env/step/episodes_socially_optimal"] == 1.0
    assert math.isclose(stats["env/step/socially_optimal_given_consensus_rate"], 0.5)
    assert math.isclose(stats["env/step/socially_optimal_rate"], 1.0 / 3.0)
    assert math.isclose(stats["env/communication/total_messages"], 4.0)
    assert math.isclose(stats["env/outcome/chosen_student_rank_global"], 1.5)


def test_aggregate_env_metrics_returns_empty_for_no_completed_episodes():
    assert aggregate_env_metrics([]) == {}
    assert aggregate_env_metrics([{}, {}]) == {}
