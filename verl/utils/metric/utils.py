# Copyright 2025 Bytedance Ltd. and/or its affiliates
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
"""
Metrics utils.
"""

from typing import Any

import numpy as np

_WEIGHTED_SOURCE_METRICS = {
    "actor": ("approx_kl", "clipfrac", "ratio_mean"),
    "critic": ("mse", "clipfrac"),
}


def reduce_metrics(metrics: dict[str, list[Any]]) -> dict[str, Any]:
    """
    Reduces a dictionary of metric lists by computing the mean, max, or min of each list.
    The reduce operation is determined by the key name:
    - If the key contains "max", np.max is used
    - If the key contains "min", np.min is used
    - Otherwise, np.mean is used

    Args:
        metrics: A dictionary mapping metric names to lists of metric values.

    Returns:
        A dictionary with the same keys but with each list replaced by its reduced value.

    Example:
        >>> metrics = {
        ...     "loss": [1.0, 2.0, 3.0],
        ...     "accuracy": [0.8, 0.9, 0.7],
        ...     "max_reward": [5.0, 8.0, 6.0],
        ...     "min_error": [0.1, 0.05, 0.2]
        ... }
        >>> reduce_metrics(metrics)
        {"loss": 2.0, "accuracy": 0.8, "max_reward": 8.0, "min_error": 0.05}
    """
    for key, val in metrics.items():
        if "max" in key:
            metrics[key] = np.max(val)
        elif "min" in key:
            metrics[key] = np.min(val)
        else:
            metrics[key] = np.mean(val)
    return metrics


def finalize_weighted_source_metrics(metrics: dict[str, Any], role: str) -> dict[str, Any]:
    """Convert reduced source numerator/count metrics into token-weighted means.

    Actor and critic workers emit one fixed-shape sufficient-statistic value per
    source, even when a worker sees zero tokens from that source. After the
    cross-worker reduction, the ratio of the mean numerator to the mean count
    equals the ratio of their global sums.

    The function is a no-op when the batch did not carry source labels (for
    example, critic-only warmup before a mixed replay batch is constructed).
    """
    try:
        metric_names = _WEIGHTED_SOURCE_METRICS[role]
    except KeyError as exc:
        raise ValueError(f"unsupported weighted source metric role: {role}") from exc

    for source in ("online", "replay"):
        count_key = f"{role}/{source}_token_count"
        if count_key not in metrics:
            continue
        token_count = float(metrics.pop(count_key))
        for metric_name in metric_names:
            numerator_key = f"{role}/{source}_{metric_name}_numerator"
            numerator = float(metrics.pop(numerator_key))
            metrics[f"{role}/{source}_{metric_name}"] = (
                numerator / token_count if token_count > 0.0 else float("nan")
            )
    return metrics
