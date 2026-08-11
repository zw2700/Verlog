# Copyright 2024 Bytedance Ltd. and/or its affiliates
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

import json

import pytest
import torch

from verl import DataProto
from verl.trainer.ppo.ray_trainer import (
    _append_replay_sample_trace,
    _checkpoint_modules_for_step,
    _is_step_in_save_schedule,
)


@pytest.mark.parametrize(
    ("configured_steps", "global_step", "expected"),
    [
        (None, 1, False),
        ([], 1, False),
        ([1, 5, 10], 5, True),
        ("[1,5,10]", 10, True),
        ("1, 5, 10", 2, False),
    ],
)
def test_is_step_in_save_schedule(configured_steps, global_step, expected):
    assert _is_step_in_save_schedule(configured_steps, global_step) is expected


def test_module_specific_checkpoint_schedules():
    config = {
        "save_freq": -1,
        "save_steps": None,
        "actor_save_steps": [30, 75],
        "critic_save_steps": [1, 5, 10, 30, 75],
        "save_actor_checkpoint": True,
        "save_critic_checkpoint": True,
    }
    expected = {
        1: (False, True),
        5: (False, True),
        10: (False, True),
        29: (False, False),
        30: (True, True),
        75: (True, True),
    }
    for global_step, modules in expected.items():
        assert _checkpoint_modules_for_step(
            config,
            global_step,
            is_last_step=global_step == 75,
            esi_close_to_expiration=False,
            use_critic=True,
        ) == modules


def test_legacy_shared_schedule_and_module_gates_are_preserved():
    config = {
        "save_freq": -1,
        "save_steps": "[1,5]",
        "save_actor_checkpoint": False,
        "save_critic_checkpoint": True,
    }
    assert _checkpoint_modules_for_step(
        config,
        5,
        is_last_step=False,
        esi_close_to_expiration=False,
        use_critic=True,
    ) == (False, True)


def test_periodic_schedule_still_saves_both_modules():
    config = {
        "save_freq": 5,
        "save_freq_offset": 0,
        "save_actor_checkpoint": True,
        "save_critic_checkpoint": True,
    }
    assert _checkpoint_modules_for_step(
        config,
        5,
        is_last_step=False,
        esi_close_to_expiration=False,
        use_critic=True,
    ) == (True, True)


def test_replay_sample_trace_records_exact_ids_and_channels(tmp_path):
    replay_batch = DataProto.from_dict(
        tensors={
            "replay_row_id": torch.tensor([9, 3, 12]),
            "replay_collection_step": torch.tensor([1, 2, 2]),
            "replay_is_warmup": torch.tensor([True, False, False]),
            "replay_is_prioritized": torch.tensor([True, False, True]),
            "replay_mean_raw_advantage": torch.tensor([0.1, -0.2, 0.3]),
            "replay_mean_return": torch.tensor([1.0, 0.0, 2.0]),
        }
    )
    trace_path = tmp_path / "nested" / "trace.jsonl"

    _append_replay_sample_trace(str(trace_path), 11, "recency_advantage_return", replay_batch)
    record = json.loads(trace_path.read_text())

    assert record["format_version"] == 1
    assert record["global_step"] == 11
    assert record["sampler"] == "recency_advantage_return"
    assert record["sampled_row_ids"] == [9, 3, 12]
    assert record["prioritized_row_ids"] == [9, 12]
    assert record["uniform_row_ids"] == [3]
    assert record["collection_steps"] == [1, 2, 2]
    assert record["is_warmup"] == [True, False, False]
