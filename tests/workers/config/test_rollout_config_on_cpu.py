# Copyright 2026 Bytedance Ltd. and/or its affiliates
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

from verl.workers.config.rollout import AgentLoopConfig


def test_reward_manager_cpu_reservation_is_fractional_and_configurable():
    assert AgentLoopConfig().reward_manager_num_cpus == 0.25
    assert AgentLoopConfig(reward_manager_num_cpus=0.5).reward_manager_num_cpus == 0.5


def test_reward_manager_cpu_reservation_must_be_non_negative():
    with pytest.raises(ValueError, match="reward_manager_num_cpus must be non-negative"):
        AgentLoopConfig(reward_manager_num_cpus=-0.25)
