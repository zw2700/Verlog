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

import pytest

from verl.trainer.ppo.ray_trainer import _checkpoint_modules_for_step, _is_step_in_save_schedule


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
