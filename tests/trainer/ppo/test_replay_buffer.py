import math

import pytest
import torch

from verl import DataProto
from verl.trainer.ppo.replay_buffer import (
    FractionalUpdateScheduler,
    RolloutReplayBuffer,
    compute_source_advantage_metrics,
    make_mixed_ppo_batch,
    resolve_replay_sample_count,
    validate_replay_config,
)
from verl.utils import torch_functional as verl_F
from verl.utils.metric import finalize_weighted_source_metrics, reduce_metrics
from verl.utils.model import compute_position_id_with_mask


def _config(**overrides):
    config = {
        "sampler": "recency_advantage",
        "minimum_buffer_updates": 2,
        "minimum_buffer_rows": 0,
        "capacity_updates": None,
        "priority_alpha": 0.6,
        "return_alpha": 0.5,
        "prioritized_fraction": 0.9,
        "recency_half_life_updates": 16.0,
        "priority_epsilon": 1e-6,
        "seed": 7,
        "warmup_max_rows_per_update": None,
        "warmup_admission_seed": 11,
    }
    config.update(overrides)
    return config


def _batch(raw_advantages: list[float], sequence_length: int = 7, response_length: int = 3) -> DataProto:
    batch_size = len(raw_advantages)
    input_ids = torch.arange(batch_size * sequence_length).reshape(batch_size, sequence_length) + 1
    attention_mask = torch.ones_like(input_ids)
    response_mask = torch.ones((batch_size, response_length), dtype=torch.long)
    values = torch.zeros((batch_size, response_length), dtype=torch.float32)
    returns = torch.tensor(raw_advantages, dtype=torch.float32).unsqueeze(-1).expand(-1, response_length).clone()
    tensors = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "position_ids": compute_position_id_with_mask(attention_mask),
        "responses": input_ids[:, -response_length:],
        "response_mask": response_mask,
        "old_log_probs": torch.zeros((batch_size, response_length), dtype=torch.float32),
        "advantages": returns.clone(),
        "values": values,
        "returns": returns,
        "rewards": torch.tensor(raw_advantages, dtype=torch.float32),
    }
    return DataProto.from_dict(tensors=tensors, meta_info={"temperature": 1.0})


@pytest.mark.parametrize(
    ("fraction", "expected_rows", "expected_realized"),
    [
        (0.0, 0, 0.0),
        (0.2, 64, 0.2),
        (0.5, 256, 0.5),
        (2.0 / 3.0, 512, 2.0 / 3.0),
    ],
)
def test_resolve_replay_sample_count(fraction, expected_rows, expected_realized):
    rows, realized = resolve_replay_sample_count(256, fraction, divisor=8)
    assert rows == expected_rows
    assert realized == pytest.approx(expected_realized)


def test_fractional_update_scheduler_and_resume():
    scheduler = FractionalUpdateScheduler(0.25)
    assert [scheduler.step() for _ in range(8)] == [0, 0, 0, 1, 0, 0, 0, 1]
    assert scheduler.total_updates == 2

    state = scheduler.state_dict()
    resumed = FractionalUpdateScheduler(0.25)
    resumed.load_state_dict(state)
    assert resumed.step(eligible=False) == 0
    assert resumed.credit == scheduler.credit
    assert [resumed.step() for _ in range(4)] == [0, 0, 0, 1]


@pytest.mark.parametrize(("rate", "expected"), [(0.1, 1), (1.0, 10), (2.0, 20)])
def test_fractional_update_scheduler_rates(rate, expected):
    scheduler = FractionalUpdateScheduler(rate)
    assert sum(scheduler.step() for _ in range(10)) == expected


def test_buffer_collects_strictly_past_rows_and_decodes_compact_tensors():
    buffer = RolloutReplayBuffer(_config())
    first = _batch([1.0, -1.0])
    second = _batch([2.0, 0.5])
    buffer.append(first, collection_step=1)
    assert not buffer.ready
    buffer.append(second, collection_step=2)
    assert buffer.ready

    replay, metrics = buffer.sample(4, current_step=3)
    assert len(replay) == 4
    assert replay.batch["input_ids"].dtype == torch.long
    assert replay.batch["attention_mask"].dtype == torch.long
    assert replay.batch["is_replay"].all()
    assert replay.batch["replay_collection_step"].max().item() == 2
    assert replay.batch["replay_collection_step"].min().item() == 1
    assert metrics["replay/sample_age_mean"] >= 1.0
    torch.testing.assert_close(
        replay.batch["position_ids"], compute_position_id_with_mask(replay.batch["attention_mask"])
    )


def test_warmup_collections_make_first_actor_step_replay_ready():
    buffer = RolloutReplayBuffer(_config(minimum_buffer_updates=8))
    for warmup_step in range(1, 11):
        buffer.append(_batch([float(warmup_step), -1.0]), collection_step=warmup_step)
    assert buffer.ready
    replay, _ = buffer.sample(8, current_step=11)
    assert replay.batch["replay_collection_step"].max().item() <= 10
    assert replay.batch["replay_collection_step"].min().item() >= 1


def test_warmup_admission_uniformly_thins_without_modifying_critic_batch():
    buffer = RolloutReplayBuffer(_config(minimum_buffer_updates=1, minimum_buffer_rows=4, warmup_max_rows_per_update=4))
    warmup_batch = _batch([float(i) for i in range(10)])
    original_input_ids = warmup_batch.batch["input_ids"].clone()

    metrics = buffer.append(warmup_batch, collection_step=1, is_warmup=True)

    assert len(warmup_batch) == 10
    torch.testing.assert_close(warmup_batch.batch["input_ids"], original_input_ids)
    assert len(buffer) == 4
    assert buffer.ready
    assert metrics["replay/admission_candidate_rows"] == 10
    assert metrics["replay/admission_admitted_rows"] == 4
    assert metrics["replay/admission_fraction"] == pytest.approx(0.4)
    assert metrics["replay/buffer_warmup_rows"] == 4
    assert metrics["replay/buffer_post_warmup_rows"] == 0


def test_warmup_admission_uses_separate_resumable_rng():
    config = _config(minimum_buffer_updates=1, warmup_max_rows_per_update=3)
    buffer = RolloutReplayBuffer(config)
    buffer.append(_batch([float(i) for i in range(8)]), collection_step=1, is_warmup=True)

    restored = RolloutReplayBuffer(config)
    restored.load_state_dict(buffer.state_dict())
    next_batch = _batch([float(i) for i in range(10, 18)])
    buffer.append(next_batch, collection_step=2, is_warmup=True)
    restored.append(next_batch, collection_step=2, is_warmup=True)

    original_state = buffer.state_dict()
    restored_state = restored.state_dict()
    torch.testing.assert_close(original_state["chunks"][-1]["row_ids"], restored_state["chunks"][-1]["row_ids"])
    torch.testing.assert_close(
        original_state["chunks"][-1]["tensors"]["input_ids"],
        restored_state["chunks"][-1]["tensors"]["input_ids"],
    )


def test_production_warmup_shape_starts_step_11_with_2560_admitted_rows():
    buffer = RolloutReplayBuffer(
        _config(
            minimum_buffer_updates=8,
            minimum_buffer_rows=2048,
            warmup_max_rows_per_update=256,
        )
    )
    for warmup_step in range(1, 11):
        metrics = buffer.append(_batch([float(warmup_step)] * 2560), warmup_step, is_warmup=True)

    assert buffer.update_count == 10
    assert len(buffer) == 2560
    assert buffer.ready
    assert metrics["replay/admission_candidate_rows"] == 2560
    assert metrics["replay/admission_admitted_rows"] == 256
    assert metrics["replay/buffer_warmup_rows"] == 2560

    replay, sample_metrics = buffer.sample(256, current_step=11)
    assert len(replay) == 256
    assert replay.batch["replay_collection_step"].min().item() >= 1
    assert replay.batch["replay_collection_step"].max().item() <= 10
    assert sample_metrics["replay/sample_warmup_fraction"] == 1.0


def test_minimum_buffer_rows_is_an_independent_readiness_gate():
    buffer = RolloutReplayBuffer(_config(minimum_buffer_updates=1, minimum_buffer_rows=5))
    buffer.append(_batch([1.0, 2.0]), collection_step=1)
    assert not buffer.ready
    buffer.append(_batch([3.0, 4.0, 5.0]), collection_step=2)
    assert buffer.ready


def test_buffer_capacity_is_measured_in_collection_updates():
    buffer = RolloutReplayBuffer(_config(minimum_buffer_updates=1, capacity_updates=2))
    for step in range(1, 4):
        buffer.append(_batch([float(step), float(step)]), collection_step=step)
    assert buffer.update_count == 2
    assert len(buffer) == 4
    replay, _ = buffer.sample(4, current_step=4)
    assert replay.batch["replay_collection_step"].min().item() == 2


def test_capacity_cannot_prevent_minimum_occupancy():
    with pytest.raises(ValueError, match="capacity_updates"):
        validate_replay_config(_config(minimum_buffer_updates=3, capacity_updates=2))


def test_recency_advantage_priority_matches_formula():
    buffer = RolloutReplayBuffer(_config(minimum_buffer_updates=1, priority_alpha=1.0, recency_half_life_updates=2.0))
    buffer.append(_batch([1.0, 4.0]), collection_step=2)
    priorities, collection_steps, advantages, _, _, _ = buffer._flat_sampling_state(current_step=4)
    expected_recency = 2.0 ** (-2.0 / 2.0)
    torch.testing.assert_close(
        priorities,
        torch.tensor([(1.0 + 1e-6) * expected_recency, (4.0 + 1e-6) * expected_recency], dtype=torch.float64),
    )
    torch.testing.assert_close(collection_steps, torch.tensor([2, 2]))
    torch.testing.assert_close(advantages, torch.tensor([1.0, 4.0]))


def test_recency_advantage_return_priority_matches_formula():
    buffer = RolloutReplayBuffer(
        _config(
            sampler="recency_advantage_return",
            minimum_buffer_updates=1,
            priority_alpha=1.0,
            return_alpha=0.5,
            recency_half_life_updates=2.0,
        )
    )
    batch = _batch([1.0, 2.0])
    batch.batch["returns"] = torch.tensor([[4.0] * 3, [9.0] * 3])
    batch.batch["values"] = torch.tensor([[3.0] * 3, [7.0] * 3])
    buffer.append(batch, collection_step=2)

    priorities, collection_steps, advantages, mean_returns, _, _ = buffer._flat_sampling_state(current_step=4)
    expected_recency = 2.0 ** (-2.0 / 2.0)
    expected = torch.tensor(
        [
            (1.0 + 1e-6) * (4.0 + 1e-6) ** 0.5 * expected_recency,
            (2.0 + 1e-6) * (9.0 + 1e-6) ** 0.5 * expected_recency,
        ],
        dtype=torch.float64,
    )
    torch.testing.assert_close(priorities, expected)
    torch.testing.assert_close(collection_steps, torch.tensor([2, 2]))
    torch.testing.assert_close(advantages, torch.tensor([1.0, 2.0]))
    torch.testing.assert_close(mean_returns, torch.tensor([4.0, 9.0]))


def test_buffer_state_roundtrip_preserves_next_sample():
    buffer = RolloutReplayBuffer(_config())
    buffer.append(_batch([1.0, -1.0, 2.0]), collection_step=1)
    buffer.append(_batch([3.0, 0.0, 4.0]), collection_step=2)

    restored = RolloutReplayBuffer(_config())
    restored.load_state_dict(buffer.state_dict())
    original_sample, original_metrics = buffer.sample(4, current_step=3)
    restored_sample, restored_metrics = restored.sample(4, current_step=3)
    for key in original_sample.batch.keys():
        torch.testing.assert_close(original_sample.batch[key], restored_sample.batch[key])
    assert original_metrics == restored_metrics


def test_sample_exposes_unique_row_ids_channels_and_warmup_diagnostics():
    buffer = RolloutReplayBuffer(
        _config(
            sampler="recency_advantage_return",
            minimum_buffer_updates=1,
            warmup_max_rows_per_update=4,
        )
    )
    buffer.append(_batch([1.0, 2.0, 3.0, 4.0, 5.0]), collection_step=1, is_warmup=True)
    buffer.append(_batch([6.0, 7.0]), collection_step=2)

    replay, metrics = buffer.sample(6, current_step=3)

    assert replay.batch["replay_row_id"].unique().numel() == 6
    assert replay.batch["replay_is_prioritized"].sum().item() == 5
    assert replay.batch["replay_is_warmup"].sum().item() == 4
    assert metrics["replay/sample_warmup_fraction"] == pytest.approx(4 / 6)
    assert 0.0 <= metrics["replay/expected_warmup_probability_mass"] <= 1.0
    assert 1.0 <= metrics["replay/sampling_effective_sample_size"] <= 6.0
    assert 0.0 < metrics["replay/sampling_top_1pct_probability_mass"] <= 1.0


def test_mixed_batch_rewhitens_raw_advantages_and_labels_sources():
    online = _batch([-2.0, -1.0])
    replay = _batch([1.0, 4.0])
    replay.batch["is_replay"] = torch.ones(2, dtype=torch.bool)
    replay.batch["replay_collection_step"] = torch.tensor([1, 2])
    generator = torch.Generator(device="cpu").manual_seed(9)

    mixed = make_mixed_ppo_batch(online, replay, generator)
    assert len(mixed) == 4
    assert mixed.batch["is_replay"].sum().item() == 2
    assert (~mixed.batch["is_replay"]).sum().item() == 2
    assert mixed.batch["replay_collection_step"][~mixed.batch["is_replay"]].eq(-1).all()
    assert verl_F.masked_mean(mixed.batch["advantages"], mixed.batch["response_mask"]).item() == pytest.approx(
        0.0, abs=1e-6
    )
    assert math.isclose(
        verl_F.masked_var(mixed.batch["advantages"], mixed.batch["response_mask"]).item(),
        1.0,
        rel_tol=1e-5,
    )
    source_metrics = compute_source_advantage_metrics(mixed)
    assert source_metrics["replay/online_raw_advantage_mean"] == pytest.approx(-1.5)
    assert source_metrics["replay/replay_raw_advantage_mean"] == pytest.approx(2.5)
    assert source_metrics["replay/online_raw_advantage_positive_fraction"] == 0.0
    assert source_metrics["replay/replay_raw_advantage_positive_fraction"] == 1.0
    assert source_metrics["replay/online_whitened_advantage_mean"] < 0.0
    assert source_metrics["replay/replay_whitened_advantage_mean"] > 0.0


def test_critic_source_metrics_are_token_weighted_with_zero_count_worker():
    # Each inner list is the fixed-shape payload from one worker. Worker 0
    # deliberately received no replay tokens.
    metrics = {
        "critic/replay_token_count": [[0.0], [2.0], [8.0]],
        "critic/replay_mse_numerator": [[0.0], [8.0], [8.0]],
        "critic/replay_clipfrac_numerator": [[0.0], [1.0], [3.0]],
        "critic/online_token_count": [[5.0], [5.0], [0.0]],
        "critic/online_mse_numerator": [[5.0], [15.0], [0.0]],
        "critic/online_clipfrac_numerator": [[1.0], [2.0], [0.0]],
    }

    finalize_weighted_source_metrics(reduce_metrics(metrics), role="critic")

    assert metrics["critic/replay_mse"] == pytest.approx(1.6)
    assert metrics["critic/replay_clipfrac"] == pytest.approx(0.4)
    assert metrics["critic/online_mse"] == pytest.approx(2.0)
    assert metrics["critic/online_clipfrac"] == pytest.approx(0.3)
    assert not any(key.endswith(("_token_count", "_numerator")) for key in metrics)


def test_actor_source_metrics_are_token_weighted_across_workers():
    metrics = {
        "actor/replay_token_count": [[1.0], [3.0]],
        "actor/replay_approx_kl_numerator": [[0.1], [0.9]],
        "actor/replay_clipfrac_numerator": [[0.0], [2.0]],
        "actor/replay_ratio_mean_numerator": [[1.2], [2.8]],
        "actor/online_token_count": [[2.0], [2.0]],
        "actor/online_approx_kl_numerator": [[0.2], [0.2]],
        "actor/online_clipfrac_numerator": [[1.0], [0.0]],
        "actor/online_ratio_mean_numerator": [[2.0], [2.0]],
    }

    finalize_weighted_source_metrics(reduce_metrics(metrics), role="actor")

    assert metrics["actor/replay_approx_kl"] == pytest.approx(0.25)
    assert metrics["actor/replay_clipfrac"] == pytest.approx(0.5)
    assert metrics["actor/replay_ratio_mean"] == pytest.approx(1.0)
    assert metrics["actor/online_approx_kl"] == pytest.approx(0.1)
    assert metrics["actor/online_clipfrac"] == pytest.approx(0.25)
    assert metrics["actor/online_ratio_mean"] == pytest.approx(1.0)
