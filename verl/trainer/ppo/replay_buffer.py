# Copyright 2026
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
"""CPU replay storage and scheduling utilities for strictly-past PPO replay."""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from typing import Any, Mapping

import torch

from verl import DataProto
from verl.utils import torch_functional as verl_F
from verl.utils.model import compute_position_id_with_mask

REPLAY_STATE_VERSION = 2

_STORAGE_DTYPES = {
    "input_ids": torch.int32,
    "attention_mask": torch.bool,
    "response_mask": torch.bool,
    "old_log_probs": torch.float32,
    "values": torch.float32,
    "returns": torch.float32,
    "ref_log_prob": torch.float32,
    "rollout_is_weights": torch.float32,
}
_REQUIRED_STORAGE_KEYS = (
    "input_ids",
    "attention_mask",
    "response_mask",
    "old_log_probs",
    "values",
    "returns",
)
_OPTIONAL_STORAGE_KEYS = ("ref_log_prob", "rollout_is_weights")


def validate_replay_config(config: Mapping[str, Any]) -> None:
    """Validate replay options before an expensive distributed run starts."""
    fraction = float(config.get("replay_fraction", 0.5))
    if not 0.0 <= fraction < 1.0:
        raise ValueError(f"replay_fraction must be in [0, 1), got {fraction}")
    sampler = config.get("sampler", "recency_advantage")
    if sampler not in ("uniform", "recency_advantage", "recency_advantage_return"):
        raise ValueError(f"unsupported replay sampler: {sampler}")
    if int(config.get("minimum_buffer_updates", 8)) < 1:
        raise ValueError("minimum_buffer_updates must be positive")
    if int(config.get("minimum_buffer_rows", 0)) < 0:
        raise ValueError("minimum_buffer_rows cannot be negative")
    capacity = config.get("capacity_updates", None)
    if capacity is not None and int(capacity) < 1:
        raise ValueError("capacity_updates must be positive or null")
    if capacity is not None and int(capacity) < int(config.get("minimum_buffer_updates", 8)):
        raise ValueError("capacity_updates cannot be smaller than minimum_buffer_updates")
    if float(config.get("priority_alpha", 0.6)) < 0.0:
        raise ValueError("priority_alpha cannot be negative")
    if float(config.get("return_alpha", 0.5)) < 0.0:
        raise ValueError("return_alpha cannot be negative")
    prioritized_fraction = float(config.get("prioritized_fraction", 0.9))
    if not 0.0 <= prioritized_fraction <= 1.0:
        raise ValueError("prioritized_fraction must be in [0, 1]")
    if float(config.get("recency_half_life_updates", 16.0)) <= 0.0:
        raise ValueError("recency_half_life_updates must be positive")
    if float(config.get("priority_epsilon", 1e-6)) <= 0.0:
        raise ValueError("priority_epsilon must be positive")
    warmup_max_rows = config.get("warmup_max_rows_per_update", None)
    if warmup_max_rows is not None and int(warmup_max_rows) < 1:
        raise ValueError("warmup_max_rows_per_update must be positive or null")


def validate_interleaved_sft_config(config: Mapping[str, Any]) -> None:
    """Validate interleaved SFT options."""
    if config.get("source", "sampled_replay") != "sampled_replay":
        raise ValueError("only interleaved_sft.source=sampled_replay is currently supported")
    if float(config.get("updates_per_global_step", 0.25)) < 0.0:
        raise ValueError("updates_per_global_step cannot be negative")
    if int(config.get("global_batch_size", 32)) < 1:
        raise ValueError("interleaved SFT global_batch_size must be positive")
    if float(config.get("learning_rate_multiplier", 1.0)) <= 0.0:
        raise ValueError("interleaved SFT learning_rate_multiplier must be positive")
    start = config.get("start_global_step", None)
    end = config.get("end_global_step", None)
    if start is not None and int(start) < 1:
        raise ValueError("interleaved SFT start_global_step must be positive or null")
    if end is not None and int(end) < 1:
        raise ValueError("interleaved SFT end_global_step must be positive or null")
    if start is not None and end is not None and int(end) < int(start):
        raise ValueError("interleaved SFT end_global_step precedes start_global_step")


def resolve_replay_sample_count(online_count: int, replay_fraction: float, divisor: int = 1) -> tuple[int, float]:
    """Resolve a requested final-batch replay fraction to a shardable row count."""
    if online_count < 1:
        raise ValueError("online_count must be positive")
    if not 0.0 <= replay_fraction < 1.0:
        raise ValueError("replay_fraction must be in [0, 1)")
    if divisor < 1:
        raise ValueError("divisor must be positive")
    if replay_fraction == 0.0:
        return 0, 0.0

    target = online_count * replay_fraction / (1.0 - replay_fraction)
    replay_count = max(divisor, int(math.floor(target / divisor + 0.5)) * divisor)
    realized_fraction = replay_count / (online_count + replay_count)
    return replay_count, realized_fraction


@dataclass
class FractionalUpdateScheduler:
    """Turn a fractional updates-per-step rate into a deterministic schedule."""

    updates_per_step: float
    credit: float = 0.0
    total_updates: int = 0

    def __post_init__(self) -> None:
        if self.updates_per_step < 0.0:
            raise ValueError("updates_per_step cannot be negative")

    def step(self, eligible: bool = True) -> int:
        if not eligible:
            return 0
        self.credit += self.updates_per_step
        updates = int(math.floor(self.credit + 1e-12))
        self.credit -= updates
        self.total_updates += updates
        return updates

    def state_dict(self) -> dict[str, Any]:
        return {
            "updates_per_step": self.updates_per_step,
            "credit": self.credit,
            "total_updates": self.total_updates,
        }

    def load_state_dict(self, state: Mapping[str, Any]) -> None:
        saved_rate = float(state["updates_per_step"])
        if not math.isclose(saved_rate, self.updates_per_step):
            raise ValueError(f"SFT rate changed across resume: checkpoint={saved_rate}, config={self.updates_per_step}")
        self.credit = float(state["credit"])
        self.total_updates = int(state["total_updates"])


@dataclass
class _ReplayChunk:
    collection_step: int
    tensors: dict[str, torch.Tensor]
    mean_raw_advantage: torch.Tensor
    mean_return: torch.Tensor
    row_ids: torch.Tensor
    is_warmup: bool
    rewards: torch.Tensor | None = None

    def __len__(self) -> int:
        return self.mean_raw_advantage.shape[0]


class RolloutReplayBuffer:
    """FIFO chunks of post-GAE agent turns stored in compact CPU tensors."""

    def __init__(self, config: Mapping[str, Any]):
        validate_replay_config(config)
        self.sampler = str(config.get("sampler", "recency_advantage"))
        self.minimum_buffer_updates = int(config.get("minimum_buffer_updates", 8))
        self.minimum_buffer_rows = int(config.get("minimum_buffer_rows", 0))
        capacity = config.get("capacity_updates", None)
        self.capacity_updates = None if capacity is None else int(capacity)
        self.priority_alpha = float(config.get("priority_alpha", 0.6))
        self.return_alpha = float(config.get("return_alpha", 0.5))
        self.prioritized_fraction = float(config.get("prioritized_fraction", 0.9))
        self.recency_half_life_updates = float(config.get("recency_half_life_updates", 16.0))
        self.priority_epsilon = float(config.get("priority_epsilon", 1e-6))
        warmup_max_rows = config.get("warmup_max_rows_per_update", None)
        self.warmup_max_rows_per_update = None if warmup_max_rows is None else int(warmup_max_rows)
        self.seed = int(config.get("seed", 90001))
        self.warmup_admission_seed = int(config.get("warmup_admission_seed", 90003))
        self.generator = torch.Generator(device="cpu")
        self.generator.manual_seed(self.seed)
        self.admission_generator = torch.Generator(device="cpu")
        self.admission_generator.manual_seed(self.warmup_admission_seed)
        self._chunks: deque[_ReplayChunk] = deque()
        self._next_row_id = 0

    def __len__(self) -> int:
        return sum(len(chunk) for chunk in self._chunks)

    @property
    def update_count(self) -> int:
        return len(self._chunks)

    @property
    def ready(self) -> bool:
        return self.update_count >= self.minimum_buffer_updates and len(self) >= max(1, self.minimum_buffer_rows)

    def append(self, data: DataProto, collection_step: int, *, is_warmup: bool = False) -> dict[str, float]:
        missing = [key for key in _REQUIRED_STORAGE_KEYS if key not in data.batch]
        if missing:
            raise KeyError(f"cannot append replay batch; missing keys: {missing}")
        if len(data) == 0:
            raise ValueError("cannot append an empty replay batch")

        candidate_rows = len(data)
        should_thin_warmup = (
            is_warmup
            and self.warmup_max_rows_per_update is not None
            and candidate_rows > self.warmup_max_rows_per_update
        )
        if should_thin_warmup:
            admitted_indices = (
                torch.randperm(candidate_rows, generator=self.admission_generator)[: self.warmup_max_rows_per_update]
                .sort()
                .values
            )
            data = data.select_idxs(admitted_indices)

        tensors = {}
        for key in _REQUIRED_STORAGE_KEYS + _OPTIONAL_STORAGE_KEYS:
            if key in data.batch:
                tensors[key] = data.batch[key].detach().to(device="cpu", dtype=_STORAGE_DTYPES[key]).contiguous()

        raw_advantage = tensors["returns"] - tensors["values"]
        response_mask = tensors["response_mask"]
        denominator = response_mask.sum(dim=-1).clamp_min(1)
        mean_raw_advantage = (raw_advantage * response_mask).sum(dim=-1) / denominator
        mean_return = (tensors["returns"] * response_mask).sum(dim=-1) / denominator
        row_ids = torch.arange(self._next_row_id, self._next_row_id + len(data), dtype=torch.long)
        self._next_row_id += len(data)
        rewards = None
        if "rewards" in data.batch:
            rewards = (
                data.batch["rewards"].detach().to(device="cpu", dtype=torch.float32).reshape(len(data), -1).mean(-1)
            )

        self._chunks.append(
            _ReplayChunk(
                collection_step=int(collection_step),
                tensors=tensors,
                mean_raw_advantage=mean_raw_advantage.to(torch.float32).contiguous(),
                mean_return=mean_return.to(torch.float32).contiguous(),
                row_ids=row_ids,
                is_warmup=bool(is_warmup),
                rewards=rewards,
            )
        )
        if self.capacity_updates is not None:
            while len(self._chunks) > self.capacity_updates:
                self._chunks.popleft()

        warmup_rows = sum(len(chunk) for chunk in self._chunks if chunk.is_warmup)
        post_warmup_rows = len(self) - warmup_rows
        return {
            "replay/buffer_rows": float(len(self)),
            "replay/buffer_updates": float(self.update_count),
            "replay/inserted_rows": float(len(data)),
            "replay/admission_candidate_rows": float(candidate_rows),
            "replay/admission_admitted_rows": float(len(data)),
            "replay/admission_fraction": float(len(data) / candidate_rows),
            "replay/buffer_warmup_rows": float(warmup_rows),
            "replay/buffer_post_warmup_rows": float(post_warmup_rows),
            "replay/buffer_warmup_fraction": float(warmup_rows / len(self)),
        }

    def _flat_sampling_state(
        self, current_step: int
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        advantages = torch.cat([chunk.mean_raw_advantage for chunk in self._chunks])
        mean_returns = torch.cat([chunk.mean_return for chunk in self._chunks])
        row_ids = torch.cat([chunk.row_ids for chunk in self._chunks])
        is_warmup = torch.cat([torch.full((len(chunk),), chunk.is_warmup, dtype=torch.bool) for chunk in self._chunks])
        collection_steps = torch.cat(
            [torch.full((len(chunk),), chunk.collection_step, dtype=torch.long) for chunk in self._chunks]
        )
        ages = (int(current_step) - collection_steps).clamp_min(1)
        if self.sampler == "uniform":
            priorities = torch.ones_like(advantages)
        else:
            advantage_priority = (advantages.clamp_min(0.0) + self.priority_epsilon).pow(self.priority_alpha)
            recency_priority = torch.pow(2.0, -ages.to(torch.float32) / self.recency_half_life_updates)
            priorities = advantage_priority * recency_priority
            if self.sampler == "recency_advantage_return":
                return_priority = (mean_returns.clamp_min(0.0) + self.priority_epsilon).pow(self.return_alpha)
                priorities = priorities * return_priority
        return priorities.to(torch.float64), collection_steps, advantages, mean_returns, is_warmup, row_ids

    def _sample_indices(self, count: int, priorities: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        available = priorities.numel()
        count = min(int(count), available)
        if count < 1:
            raise ValueError("replay sample count must be positive and the buffer must be nonempty")
        if self.sampler == "uniform":
            return torch.randperm(available, generator=self.generator)[:count], torch.zeros(count, dtype=torch.bool)

        prioritized_count = min(count, int(math.floor(count * self.prioritized_fraction + 0.5)))
        if prioritized_count:
            selected_priority = torch.multinomial(
                priorities,
                num_samples=prioritized_count,
                replacement=False,
                generator=self.generator,
            )
        else:
            selected_priority = torch.empty(0, dtype=torch.long)

        selected_mask = torch.zeros(available, dtype=torch.bool)
        selected_mask[selected_priority] = True
        remaining = torch.nonzero(~selected_mask, as_tuple=False).squeeze(-1)
        uniform_count = count - prioritized_count
        if uniform_count:
            uniform_order = torch.randperm(len(remaining), generator=self.generator)[:uniform_count]
            selected_uniform = remaining[uniform_order]
            selected = torch.cat([selected_priority, selected_uniform])
            selected_is_prioritized = torch.cat(
                [torch.ones(prioritized_count, dtype=torch.bool), torch.zeros(uniform_count, dtype=torch.bool)]
            )
        else:
            selected = selected_priority
            selected_is_prioritized = torch.ones(prioritized_count, dtype=torch.bool)
        shuffle = torch.randperm(len(selected), generator=self.generator)
        return selected[shuffle], selected_is_prioritized[shuffle]

    def _gather(self, flat_indices: torch.Tensor) -> dict[str, torch.Tensor]:
        chunks = list(self._chunks)
        offsets = []
        running = 0
        for chunk in chunks:
            offsets.append((running, running + len(chunk)))
            running += len(chunk)

        locations: dict[int, list[tuple[int, int]]] = {}
        for output_index, flat_index in enumerate(flat_indices.tolist()):
            for chunk_index, (start, end) in enumerate(offsets):
                if start <= flat_index < end:
                    locations.setdefault(chunk_index, []).append((output_index, flat_index - start))
                    break

        keys = set.intersection(*(set(chunk.tensors) for chunk in chunks))
        output: dict[str, torch.Tensor] = {}
        for key in keys:
            exemplar = chunks[0].tensors[key]
            tensor = torch.empty((len(flat_indices), *exemplar.shape[1:]), dtype=exemplar.dtype)
            for chunk_index, pairs in locations.items():
                output_positions = torch.tensor([pair[0] for pair in pairs], dtype=torch.long)
                local_positions = torch.tensor([pair[1] for pair in pairs], dtype=torch.long)
                tensor[output_positions] = chunks[chunk_index].tensors[key][local_positions]
            output[key] = tensor
        return output

    def sample(self, count: int, current_step: int) -> tuple[DataProto, dict[str, float]]:
        if not self.ready:
            raise RuntimeError(f"replay is not ready: {self.update_count}/{self.minimum_buffer_updates} stored updates")
        priorities, collection_steps, mean_advantages, mean_returns, is_warmup, row_ids = self._flat_sampling_state(
            current_step
        )
        selected, selected_is_prioritized = self._sample_indices(count, priorities)
        prioritized_count = int(selected_is_prioritized.sum().item())
        tensors = self._gather(selected)
        response_length = tensors["response_mask"].shape[-1]
        tensors["input_ids"] = tensors["input_ids"].to(torch.long)
        tensors["attention_mask"] = tensors["attention_mask"].to(torch.long)
        tensors["response_mask"] = tensors["response_mask"].to(torch.long)
        tensors["responses"] = tensors["input_ids"][:, -response_length:]
        tensors["position_ids"] = compute_position_id_with_mask(tensors["attention_mask"])
        tensors["advantages"] = tensors["returns"] - tensors["values"]
        tensors["is_replay"] = torch.ones(len(selected), dtype=torch.bool)
        tensors["replay_collection_step"] = collection_steps[selected]
        tensors["replay_row_id"] = row_ids[selected]
        tensors["replay_is_warmup"] = is_warmup[selected]
        tensors["replay_is_prioritized"] = selected_is_prioritized
        tensors["replay_mean_raw_advantage"] = mean_advantages[selected]
        tensors["replay_mean_return"] = mean_returns[selected]

        selected_ages = int(current_step) - collection_steps[selected]
        selected_advantages = mean_advantages[selected]
        selected_returns = mean_returns[selected]
        selected_warmup = is_warmup[selected]

        available = len(priorities)
        if self.sampler == "uniform":
            expected_probabilities = torch.full((available,), 1.0 / available, dtype=torch.float64)
            priority_warmup_mass = is_warmup.to(torch.float64).mean()
        else:
            normalized_priorities = priorities / priorities.sum()
            priority_warmup_mass = normalized_priorities[is_warmup].sum()
            realized_prioritized_fraction = prioritized_count / len(selected)
            expected_probabilities = (
                realized_prioritized_fraction * normalized_priorities
                + (1.0 - realized_prioritized_fraction) / available
            )
        effective_sample_size = expected_probabilities.square().sum().reciprocal()
        top_count = max(1, int(math.ceil(available * 0.01)))
        top_one_percent_mass = expected_probabilities.topk(top_count).values.sum()

        def _quantile(values: torch.Tensor, q: float) -> float:
            return float(torch.quantile(values.to(torch.float32), q).item())

        metrics = {
            "replay/sampled_rows": float(len(selected)),
            "replay/prioritized_rows": float(prioritized_count),
            "replay/uniform_rows": float(len(selected) - prioritized_count),
            "replay/sample_age_mean": float(selected_ages.to(torch.float32).mean()),
            "replay/sample_age_max": float(selected_ages.max()),
            "replay/sample_age_p50": _quantile(selected_ages, 0.5),
            "replay/sample_age_p90": _quantile(selected_ages, 0.9),
            "replay/sample_advantage_mean": float(selected_advantages.mean()),
            "replay/sample_advantage_p10": _quantile(selected_advantages, 0.1),
            "replay/sample_advantage_p50": _quantile(selected_advantages, 0.5),
            "replay/sample_advantage_p90": _quantile(selected_advantages, 0.9),
            "replay/sample_advantage_positive_fraction": float((selected_advantages > 0).to(torch.float32).mean()),
            "replay/sample_return_mean": float(selected_returns.mean()),
            "replay/sample_return_p10": _quantile(selected_returns, 0.1),
            "replay/sample_return_p50": _quantile(selected_returns, 0.5),
            "replay/sample_return_p90": _quantile(selected_returns, 0.9),
            "replay/sample_return_positive_fraction": float((selected_returns > 0).to(torch.float32).mean()),
            "replay/sample_warmup_fraction": float(selected_warmup.to(torch.float32).mean()),
            "replay/priority_warmup_probability_mass": float(priority_warmup_mass),
            "replay/expected_warmup_probability_mass": float(expected_probabilities[is_warmup].sum()),
            "replay/sample_unique_collection_steps": float(collection_steps[selected].unique().numel()),
            "replay/sampling_effective_sample_size": float(effective_sample_size),
            "replay/sampling_effective_sample_fraction": float(effective_sample_size / available),
            "replay/sampling_top_1pct_probability_mass": float(top_one_percent_mass),
        }
        return DataProto.from_dict(tensors=tensors), metrics

    def state_dict(self) -> dict[str, Any]:
        return {
            "version": REPLAY_STATE_VERSION,
            "sampler": self.sampler,
            "minimum_buffer_updates": self.minimum_buffer_updates,
            "minimum_buffer_rows": self.minimum_buffer_rows,
            "capacity_updates": self.capacity_updates,
            "priority_alpha": self.priority_alpha,
            "return_alpha": self.return_alpha,
            "prioritized_fraction": self.prioritized_fraction,
            "recency_half_life_updates": self.recency_half_life_updates,
            "priority_epsilon": self.priority_epsilon,
            "warmup_max_rows_per_update": self.warmup_max_rows_per_update,
            "seed": self.seed,
            "warmup_admission_seed": self.warmup_admission_seed,
            "generator_state": self.generator.get_state(),
            "admission_generator_state": self.admission_generator.get_state(),
            "next_row_id": self._next_row_id,
            "chunks": [
                {
                    "collection_step": chunk.collection_step,
                    "tensors": chunk.tensors,
                    "mean_raw_advantage": chunk.mean_raw_advantage,
                    "mean_return": chunk.mean_return,
                    "row_ids": chunk.row_ids,
                    "is_warmup": chunk.is_warmup,
                    "rewards": chunk.rewards,
                }
                for chunk in self._chunks
            ],
        }

    def load_state_dict(self, state: Mapping[str, Any]) -> None:
        if int(state.get("version", -1)) != REPLAY_STATE_VERSION:
            raise ValueError(f"unsupported replay state version: {state.get('version')}")
        comparable = (
            "sampler",
            "minimum_buffer_updates",
            "minimum_buffer_rows",
            "capacity_updates",
            "priority_alpha",
            "return_alpha",
            "prioritized_fraction",
            "recency_half_life_updates",
            "priority_epsilon",
            "warmup_max_rows_per_update",
            "seed",
            "warmup_admission_seed",
        )
        for key in comparable:
            if state[key] != getattr(self, key):
                raise ValueError(f"replay config changed across resume for {key}: {state[key]} != {getattr(self, key)}")
        self.generator.set_state(state["generator_state"])
        self.admission_generator.set_state(state["admission_generator_state"])
        self._next_row_id = int(state["next_row_id"])
        self._chunks = deque(
            _ReplayChunk(
                collection_step=int(chunk["collection_step"]),
                tensors=chunk["tensors"],
                mean_raw_advantage=chunk["mean_raw_advantage"],
                mean_return=chunk["mean_return"],
                row_ids=chunk["row_ids"],
                is_warmup=bool(chunk["is_warmup"]),
                rewards=chunk.get("rewards", None),
            )
            for chunk in state["chunks"]
        )


def compute_source_advantage_metrics(data: DataProto) -> dict[str, float]:
    """Summarize each source before and after mixed-batch advantage whitening."""
    if "is_replay" not in data.batch:
        return {}

    raw_advantages = data.batch["returns"] - data.batch["values"]
    whitened_advantages = data.batch["advantages"]
    response_mask = data.batch["response_mask"].to(torch.bool)
    metrics: dict[str, float] = {}
    for source, source_rows in (
        ("online", ~data.batch["is_replay"].to(torch.bool)),
        ("replay", data.batch["is_replay"].to(torch.bool)),
    ):
        source_mask = response_mask & source_rows.unsqueeze(-1)
        if not source_mask.any():
            continue
        for stage, advantages in (("raw", raw_advantages), ("whitened", whitened_advantages)):
            values = advantages[source_mask].to(torch.float32)
            metrics[f"replay/{source}_{stage}_advantage_mean"] = float(values.mean())
            metrics[f"replay/{source}_{stage}_advantage_std"] = float(values.std(unbiased=False))
            metrics[f"replay/{source}_{stage}_advantage_positive_fraction"] = float(
                (values > 0).to(torch.float32).mean()
            )
    return metrics


def make_mixed_ppo_batch(online: DataProto, replay: DataProto, generator: torch.Generator) -> DataProto:
    """Build a source-labelled PPO batch and whiten raw advantages over the mixture."""
    online_keys = set(online.batch.keys())
    replay_keys = set(replay.batch.keys())
    required = set(_REQUIRED_STORAGE_KEYS) | {"responses", "position_ids", "advantages"}
    missing_online = required - online_keys
    missing_replay = required - replay_keys
    if missing_online or missing_replay:
        raise KeyError(f"mixed PPO keys missing: online={sorted(missing_online)}, replay={sorted(missing_replay)}")

    keys = required | (set(_OPTIONAL_STORAGE_KEYS) & online_keys & replay_keys)
    online_tensors = {key: online.batch[key] for key in keys}
    replay_tensors = {key: replay.batch[key] for key in keys}
    online_tensors["is_replay"] = torch.zeros(len(online), dtype=torch.bool)
    replay_tensors["is_replay"] = replay.batch["is_replay"]
    online_tensors["replay_collection_step"] = torch.full((len(online),), -1, dtype=torch.long)
    replay_tensors["replay_collection_step"] = replay.batch["replay_collection_step"]

    tensors = {key: torch.cat([online_tensors[key], replay_tensors[key]], dim=0) for key in online_tensors}
    order = torch.randperm(len(online) + len(replay), generator=generator)
    tensors = {key: value[order] for key, value in tensors.items()}
    raw_advantages = tensors["returns"] - tensors["values"]
    tensors["advantages"] = verl_F.masked_whiten(raw_advantages, tensors["response_mask"])

    meta_info = dict(online.meta_info)
    meta_info["global_token_num"] = tensors["attention_mask"].sum(dim=-1).tolist()
    return DataProto.from_dict(tensors=tensors, meta_info=meta_info)
