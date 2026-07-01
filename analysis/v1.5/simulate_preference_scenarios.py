#!/usr/bin/env python3
"""Estimate preference-scenario probabilities from environment construction.

By default this mirrors the current hiring environment reset process:
professor preference vectors are independent random permutations and student
ability vectors are sampled from the existing discrete simplex. The optional
sampler flags let us test candidate construction changes before modifying the
environment itself.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any


CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parents[1]
sys.path.insert(0, str(CURRENT_DIR))
sys.path.insert(0, str(REPO_ROOT))

from compute_preference_scenario_metrics import SCENARIO_ORDER, preference_scenario  # noqa: E402


DEFAULT_ENV_CONFIG = {
    "professor_ids": ["prof_1", "prof_2", "prof_3"],
    "students_per_batch": 5,
    "token_budget": 500,
    "feature_dim": 5,
    "vote_threshold": 0.5,
    "max_steps": 50,
    "student_profile_mode": "discrete_simplex",
    "student_specialization_min_top": 0.7,
    "professor_preference_mode": "random_permutation",
    "preference_correlation_threshold": 0.0,
    "preference_rejection_max_attempts": 1000,
}


def load_env_config(args: argparse.Namespace) -> dict[str, Any]:
    config = dict(DEFAULT_ENV_CONFIG)
    config.update(
        {
            "students_per_batch": args.students_per_batch,
            "token_budget": args.token_budget,
            "feature_dim": args.feature_dim,
            "vote_threshold": args.vote_threshold,
            "max_steps": args.max_steps,
            "student_profile_mode": args.student_profile_mode,
            "student_specialization_min_top": args.student_specialization_min_top,
            "professor_preference_mode": args.professor_preference_mode,
            "preference_correlation_threshold": args.preference_correlation_threshold,
            "preference_rejection_max_attempts": args.preference_rejection_max_attempts,
        }
    )
    if args.env_config_json:
        path = Path(args.env_config_json)
        overrides = json.loads(path.read_text()) if path.exists() else json.loads(args.env_config_json)
        config.update(overrides)
    return config


def sample_integer_composition(total: int, parts: int) -> list[int]:
    if parts <= 0:
        return []
    cuts = sorted(random.randrange(total + 1) for _ in range(parts - 1))
    boundaries = [0, *cuts, total]
    return [right - left for left, right in zip(boundaries, boundaries[1:])]


def sample_discrete_simplex(n: int) -> list[float]:
    counts = sample_integer_composition(total=10, parts=n)
    return [count / 10.0 for count in counts]


def sample_specialized_discrete_simplex(n: int, min_top_mass: float) -> list[float]:
    min_top_count = max(1, min(10, math.ceil(min_top_mass * 10)))
    primary_feature = random.randrange(n)
    primary_count = random.randrange(min_top_count, 11)
    remaining_counts = sample_integer_composition(total=10 - primary_count, parts=n - 1)

    counts = []
    remaining_idx = 0
    for feature_idx in range(n):
        if feature_idx == primary_feature:
            counts.append(primary_count)
        else:
            counts.append(remaining_counts[remaining_idx])
            remaining_idx += 1
    return [count / 10.0 for count in counts]


def sample_student_profile(env_config: dict[str, Any]) -> list[float]:
    feature_dim = int(env_config["feature_dim"])
    mode = env_config.get("student_profile_mode", "discrete_simplex")
    if mode == "discrete_simplex":
        return sample_discrete_simplex(feature_dim)
    if mode == "specialized_discrete_simplex":
        return sample_specialized_discrete_simplex(
            feature_dim,
            float(env_config.get("student_specialization_min_top", 0.7)),
        )
    raise ValueError(f"Unknown student_profile_mode: {mode}")


def sample_random_permutation_preferences(professor_ids: list[str], feature_dim: int) -> dict[str, list[int]]:
    feature_indices = list(range(feature_dim))
    return {
        prof_id: random.sample(feature_indices, k=feature_dim)
        for prof_id in professor_ids
    }


def sample_diverse_top_feature_preferences(professor_ids: list[str], feature_dim: int) -> dict[str, list[int]]:
    if len(professor_ids) > feature_dim:
        raise ValueError("diverse_top_feature requires feature_dim >= number of professors")

    top_features = random.sample(range(feature_dim), k=len(professor_ids))
    professor_interests = {}
    for prof_id, top_feature in zip(professor_ids, top_features):
        preference_vector = [0] * feature_dim
        preference_vector[top_feature] = feature_dim - 1
        lower_weights = list(range(feature_dim - 1))
        random.shuffle(lower_weights)
        lower_features = [feature for feature in range(feature_dim) if feature != top_feature]
        for feature, weight in zip(lower_features, lower_weights):
            preference_vector[feature] = weight
        professor_interests[prof_id] = preference_vector
    return professor_interests


def pearson_corr(xs: list[int], ys: list[int]) -> float:
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_denominator = math.sqrt(sum((x - x_mean) ** 2 for x in xs))
    y_denominator = math.sqrt(sum((y - y_mean) ** 2 for y in ys))
    if x_denominator == 0.0 or y_denominator == 0.0:
        return 0.0
    return numerator / (x_denominator * y_denominator)


def max_pairwise_pearson_corr(professor_interests: dict[str, list[int]]) -> float:
    agents = sorted(professor_interests)
    max_corr = -1.0
    for i, agent_a in enumerate(agents):
        for agent_b in agents[i + 1:]:
            max_corr = max(max_corr, pearson_corr(professor_interests[agent_a], professor_interests[agent_b]))
    return max_corr


def has_distinct_top_features(professor_interests: dict[str, list[int]]) -> bool:
    top_features = [values.index(max(values)) for values in professor_interests.values()]
    return len(set(top_features)) == len(top_features)


def sample_rejection_low_correlation_preferences(
    professor_ids: list[str],
    feature_dim: int,
    threshold: float,
    max_attempts: int,
    require_distinct_top: bool,
) -> dict[str, list[int]]:
    for _attempt in range(max_attempts):
        professor_interests = sample_random_permutation_preferences(professor_ids, feature_dim)
        if require_distinct_top and not has_distinct_top_features(professor_interests):
            continue
        if max_pairwise_pearson_corr(professor_interests) <= threshold:
            return professor_interests
    constraint = f"max pairwise Pearson <= {threshold}"
    if require_distinct_top:
        constraint += " and distinct top features"
    raise RuntimeError(f"Could not sample professor preferences satisfying {constraint} after {max_attempts} attempts")


def sample_professor_preferences(env_config: dict[str, Any]) -> dict[str, list[int]]:
    professor_ids = list(env_config["professor_ids"])
    feature_dim = int(env_config["feature_dim"])
    mode = env_config.get("professor_preference_mode", "random_permutation")
    if mode == "random_permutation":
        return sample_random_permutation_preferences(professor_ids, feature_dim)
    if mode == "diverse_top_feature":
        return sample_diverse_top_feature_preferences(professor_ids, feature_dim)
    if mode in {"rejection_low_correlation", "rejection_low_correlation_distinct_top"}:
        return sample_rejection_low_correlation_preferences(
            professor_ids,
            feature_dim,
            float(env_config.get("preference_correlation_threshold", 0.0)),
            int(env_config.get("preference_rejection_max_attempts", 1000)),
            require_distinct_top=(mode == "rejection_low_correlation_distinct_top"),
        )
    raise ValueError(f"Unknown professor_preference_mode: {mode}")


def sample_episode_construction(env_config: dict[str, Any]) -> dict[str, Any]:
    students_per_batch = int(env_config["students_per_batch"])
    professor_interests = sample_professor_preferences(env_config)
    student_batch = []
    for idx in range(students_per_batch):
        student_batch.append(
            {
                "index": idx,
                "id": f"student_{idx}",
                "name": f"Student {idx}",
                "profile_vector": sample_student_profile(env_config),
            }
        )
    return {
        "professor_interests": professor_interests,
        "student_batch": student_batch,
    }


def scenario_rows(counts: Counter[str], samples: int) -> list[dict[str, Any]]:
    rows = []
    for scenario in SCENARIO_ORDER:
        count = counts.get(scenario, 0)
        rows.append(
            {
                "scenario": scenario,
                "count": count,
                "probability": count / samples if samples else None,
            }
        )
    for scenario in sorted(set(counts) - set(SCENARIO_ORDER)):
        count = counts[scenario]
        rows.append(
            {
                "scenario": scenario,
                "count": count,
                "probability": count / samples if samples else None,
            }
        )
    return rows


def run_simulation(samples: int, seed: int, env_config: dict[str, Any]) -> list[dict[str, Any]]:
    random.seed(seed)
    counts: Counter[str] = Counter()
    for _ in range(samples):
        ep = sample_episode_construction(env_config)
        scenario, _features = preference_scenario(ep)
        counts[scenario] += 1
    return scenario_rows(counts, samples)


def ablation_configs(base_config: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    cells = [
        ("baseline", "discrete_simplex", "random_permutation"),
        ("specialized_students", "specialized_discrete_simplex", "random_permutation"),
        ("diverse_preferences", "discrete_simplex", "diverse_top_feature"),
        ("specialized_students_and_diverse_preferences", "specialized_discrete_simplex", "diverse_top_feature"),
    ]
    configs = []
    for name, student_mode, professor_mode in cells:
        config = dict(base_config)
        config["student_profile_mode"] = student_mode
        config["professor_preference_mode"] = professor_mode
        configs.append((name, config))
    return configs


def preference_diversity_sweep_configs(base_config: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    cells: list[tuple[str, str, float | None]] = [
        ("baseline_random_permutation", "random_permutation", None),
        ("direct_distinct_top_feature", "diverse_top_feature", None),
        ("rejection_corr_le_0_3", "rejection_low_correlation", 0.3),
        ("rejection_corr_le_0_0", "rejection_low_correlation", 0.0),
        ("rejection_corr_le_neg_0_1", "rejection_low_correlation", -0.1),
        ("rejection_corr_le_0_0_distinct_top", "rejection_low_correlation_distinct_top", 0.0),
    ]
    configs = []
    for name, professor_mode, threshold in cells:
        config = dict(base_config)
        config["professor_preference_mode"] = professor_mode
        if threshold is not None:
            config["preference_correlation_threshold"] = threshold
        configs.append((name, config))
    return configs


def flattened_rows(experiment_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for result in experiment_results:
        for row in result["scenarios"]:
            rows.append(
                {
                    "experiment": result["experiment"],
                    "scenario": row["scenario"],
                    "count": row["count"],
                    "probability": row["probability"],
                }
            )
    return rows


def print_result(experiment: str, samples: int, seed: int, env_config: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    print(f"[{experiment}] samples={samples} seed={seed}")
    print(f"[{experiment}] env_config={json.dumps(env_config, sort_keys=True)}")
    for row in rows:
        print(f"[{experiment}] {row['scenario']}: {row['count']} ({row['probability']:.4f})")
    print()


def write_outputs(out_dir: Path, experiment_results: list[dict[str, Any]]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    with (out_dir / "preference_scenario_simulation_summary.json").open("w") as f:
        json.dump({"experiments": experiment_results}, f, indent=2, sort_keys=True)
        f.write("\n")

    with (out_dir / "preference_scenario_simulation_summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["experiment", "scenario", "count", "probability"])
        writer.writeheader()
        writer.writerows(flattened_rows(experiment_results))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=100_000, help="Number of env resets to sample")
    parser.add_argument("--seed", type=int, default=0, help="Random seed for the environment RNG")
    parser.add_argument("--out-dir", type=Path, default=None, help="Optional directory for JSON/CSV outputs")
    parser.add_argument("--ablation-grid", action="store_true", help="Run the 2x2 student specialization x preference diversity grid")
    parser.add_argument("--preference-diversity-sweep", action="store_true", help="Run several professor preference diversity samplers")
    parser.add_argument("--students-per-batch", type=int, default=5)
    parser.add_argument("--token-budget", type=int, default=500)
    parser.add_argument("--feature-dim", type=int, default=5)
    parser.add_argument("--vote-threshold", type=float, default=0.5)
    parser.add_argument("--max-steps", type=int, default=50)
    parser.add_argument(
        "--student-profile-mode",
        choices=["discrete_simplex", "specialized_discrete_simplex"],
        default="discrete_simplex",
    )
    parser.add_argument("--student-specialization-min-top", type=float, default=0.7)
    parser.add_argument(
        "--professor-preference-mode",
        choices=[
            "random_permutation",
            "diverse_top_feature",
            "rejection_low_correlation",
            "rejection_low_correlation_distinct_top",
        ],
        default="random_permutation",
    )
    parser.add_argument("--preference-correlation-threshold", type=float, default=0.0)
    parser.add_argument("--preference-rejection-max-attempts", type=int, default=1000)
    parser.add_argument("--env-config-json", default=None, help="JSON string or path to a JSON object of env config overrides")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.samples <= 0:
        raise SystemExit("--samples must be positive")

    base_config = load_env_config(args)
    if args.ablation_grid and args.preference_diversity_sweep:
        raise SystemExit("--ablation-grid and --preference-diversity-sweep are mutually exclusive")
    if args.ablation_grid:
        experiments = ablation_configs(base_config)
    elif args.preference_diversity_sweep:
        experiments = preference_diversity_sweep_configs(base_config)
    else:
        experiments = [("single", base_config)]
    experiment_results = []

    for experiment, env_config in experiments:
        rows = run_simulation(args.samples, args.seed, env_config)
        print_result(experiment, args.samples, args.seed, env_config, rows)
        experiment_results.append(
            {
                "experiment": experiment,
                "samples": args.samples,
                "seed": args.seed,
                "env_config": env_config,
                "scenarios": rows,
            }
        )

    if args.out_dir is not None:
        write_outputs(args.out_dir, experiment_results)


if __name__ == "__main__":
    main()
