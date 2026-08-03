#!/usr/bin/env python3
"""Compare locked-seed rollout evaluations with paired uncertainty estimates."""

from __future__ import annotations

import argparse
import json
import math
import random
import re
from pathlib import Path
from statistics import mean
from typing import Any

from scripts.sft.evaluate_policy import summarize_evaluation
from scripts.sft.rollout_core import action_error_counts, iter_jsonl

LABEL_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def parse_labeled_path(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("expected LABEL=PATH")
    label, raw_path = value.split("=", 1)
    if not LABEL_PATTERN.fullmatch(label):
        raise argparse.ArgumentTypeError(f"invalid label: {label!r}")
    path = Path(raw_path).expanduser()
    if path.is_dir():
        path = path / "episodes.jsonl"
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"evaluation JSONL does not exist: {path}")
    return label, path.resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=parse_labeled_path, help="LABEL=episodes.jsonl")
    parser.add_argument(
        "--candidate", required=True, action="append", type=parse_labeled_path, help="repeat LABEL=episodes.jsonl"
    )
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--seed-base", type=int, default=0)
    parser.add_argument("--num-scenarios", type=int, default=None)
    parser.add_argument("--bootstrap-replicates", type=int, default=10_000)
    parser.add_argument("--bootstrap-seed", type=int, default=1)
    return parser.parse_args()


def load_rows(path: Path, *, seed_base: int, num_scenarios: int | None) -> dict[int, dict[str, Any]]:
    expected = set(range(seed_base, seed_base + num_scenarios)) if num_scenarios is not None else None
    rows: dict[int, dict[str, Any]] = {}
    for row in iter_jsonl([path]):
        if int(row.get("attempt", 0)) != 0:
            continue
        seed = int(row["scenario_seed"])
        if expected is not None and seed not in expected:
            continue
        if seed in rows:
            raise ValueError(f"{path} contains duplicate sample-0 row for seed {seed}")
        rows[seed] = row
    if expected is not None and set(rows) != expected:
        missing = sorted(expected - set(rows))
        raise ValueError(f"{path} is missing {len(missing)} requested seed(s), beginning with {missing[:5]}")
    if not rows:
        raise ValueError(f"{path} contains no evaluation rows")
    return rows


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def paired_bootstrap_interval(
    deltas: list[float],
    *,
    replicates: int,
    seed: int,
) -> tuple[float, float]:
    rng = random.Random(seed)
    sample_size = len(deltas)
    estimates = [mean(rng.choices(deltas, k=sample_size)) for _ in range(replicates)]
    return percentile(estimates, 0.025), percentile(estimates, 0.975)


def exact_mcnemar_pvalue(candidate_only: int, baseline_only: int) -> float:
    discordant = candidate_only + baseline_only
    if discordant == 0:
        return 1.0
    lower_tail = sum(math.comb(discordant, k) for k in range(min(candidate_only, baseline_only) + 1))
    return min(1.0, 2.0 * lower_tail / (2**discordant))


def valid_action_episode(row: dict[str, Any]) -> bool:
    format_errors, invalid_errors = action_error_counts(row)
    return format_errors == 0 and invalid_errors == 0


def row_metric(row: dict[str, Any], name: str) -> float:
    if name == "socially_optimal":
        return float(bool(row.get("socially_optimal")))
    if name == "consensus":
        return float(bool(row.get("consensus")))
    if name == "action_valid":
        return float(valid_action_episode(row))
    if name == "efficiency":
        return float(row.get("social_welfare_efficiency") or 0.0)
    if name == "llm_turns":
        return float(len(row.get("turns") or []))
    if name == "public_tokens":
        return float(row.get("tokens_used") or 0.0)
    if name == "output_tokens":
        return float(row.get("llm_output_tokens") or 0.0)
    raise KeyError(name)


def paired_mean_difference(
    baseline: dict[int, dict[str, Any]],
    candidate: dict[int, dict[str, Any]],
    metric: str,
) -> float:
    return mean(row_metric(candidate[seed], metric) - row_metric(baseline[seed], metric) for seed in sorted(baseline))


def paired_primary_report(
    baseline: dict[int, dict[str, Any]],
    candidate: dict[int, dict[str, Any]],
    *,
    bootstrap_replicates: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    deltas = []
    both_success = candidate_only = baseline_only = both_failure = 0
    for seed in sorted(baseline):
        base_success = bool(baseline[seed].get("socially_optimal"))
        candidate_success = bool(candidate[seed].get("socially_optimal"))
        deltas.append(float(candidate_success) - float(base_success))
        if base_success and candidate_success:
            both_success += 1
        elif candidate_success:
            candidate_only += 1
        elif base_success:
            baseline_only += 1
        else:
            both_failure += 1
    interval = paired_bootstrap_interval(
        deltas,
        replicates=bootstrap_replicates,
        seed=bootstrap_seed,
    )
    return {
        "paired_rate_difference": mean(deltas),
        "paired_rate_difference_95ci_bootstrap": list(interval),
        "bootstrap_replicates": bootstrap_replicates,
        "both_socially_optimal": both_success,
        "candidate_only_socially_optimal": candidate_only,
        "baseline_only_socially_optimal": baseline_only,
        "neither_socially_optimal": both_failure,
        "discordant_pairs": candidate_only + baseline_only,
        "exact_mcnemar_pvalue_two_sided": exact_mcnemar_pvalue(candidate_only, baseline_only),
    }


def model_report(rows: dict[int, dict[str, Any]], path: Path) -> dict[str, Any]:
    ordered = [rows[seed] for seed in sorted(rows)]
    summary = summarize_evaluation(ordered)
    first = ordered[0]
    return {
        "path": str(path),
        "model": first.get("teacher_model"),
        "provider": first.get("provider"),
        "temperature": first.get("teacher_temperature"),
        "target_tokenizer": first.get("target_tokenizer"),
        "env_config_hash": first.get("env_config_hash"),
        **summary,
    }


def assert_comparable(all_rows: dict[str, dict[int, dict[str, Any]]]) -> None:
    seed_sets = {label: set(rows) for label, rows in all_rows.items()}
    first_label, first_seeds = next(iter(seed_sets.items()))
    for label, seeds in seed_sets.items():
        if seeds != first_seeds:
            raise ValueError(f"seed set for {label} differs from {first_label}")
    for field in (
        "env_config_hash",
        "target_tokenizer",
        "teacher_temperature",
        "teacher_top_p",
        "teacher_top_k",
        "teacher_max_output_tokens",
    ):
        observed = {
            label: {row.get(field) for row in rows.values()}
            for label, rows in all_rows.items()
        }
        within_run_mismatch = any(len(values) != 1 for values in observed.values())
        across_run_mismatch = len({next(iter(values)) for values in observed.values()}) != 1
        if within_run_mismatch or across_run_mismatch:
            raise ValueError(f"evaluations are not comparable on {field}: {observed}")

    fingerprint_presence = {
        label: all(bool(row.get("scenario_fingerprint")) for row in rows.values())
        for label, rows in all_rows.items()
    }
    if any(fingerprint_presence.values()) and not all(fingerprint_presence.values()):
        raise ValueError(
            "scenario fingerprints are present for only some evaluations; rerun legacy evaluations "
            f"before treating them as paired: {fingerprint_presence}"
        )
    if all(fingerprint_presence.values()):
        for seed in first_seeds:
            fingerprints = {
                label: str(rows[seed]["scenario_fingerprint"])
                for label, rows in all_rows.items()
            }
            if len(set(fingerprints.values())) != 1:
                raise ValueError(f"realized scenario differs for seed {seed}: {fingerprints}")


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Paired SFT evaluation comparison",
        "",
        f"Locked scenarios: {report['num_scenarios']} (seeds {report['seed_min']}–{report['seed_max']}).",
        "",
        "| Model | SO rate (95% Wilson CI) | Consensus | Valid actions | Mean efficiency |",
        "|---|---:|---:|---:|---:|",
    ]
    for label, model in report["models"].items():
        low, high = model["socially_optimal_rate_95ci"]
        lines.append(
            f"| {label} | {model['socially_optimal_rate']:.3f} [{low:.3f}, {high:.3f}] | "
            f"{model['consensus_rate']:.3f} | {model['action_valid_episode_rate']:.3f} | "
            f"{model['mean_social_welfare_efficiency']:.3f} |"
        )
    lines.extend(
        [
            "",
            f"Paired comparisons are candidate minus `{report['baseline_label']}`.",
            "",
            "| Candidate | SO difference (95% paired bootstrap CI) | Candidate-only / baseline-only | McNemar p |",
            "|---|---:|---:|---:|",
        ]
    )
    for label, comparison in report["comparisons"].items():
        paired = comparison["socially_optimal"]
        low, high = paired["paired_rate_difference_95ci_bootstrap"]
        lines.append(
            f"| {label} | {paired['paired_rate_difference']:+.3f} [{low:+.3f}, {high:+.3f}] | "
            f"{paired['candidate_only_socially_optimal']} / {paired['baseline_only_socially_optimal']} | "
            f"{paired['exact_mcnemar_pvalue_two_sided']:.4g} |"
        )
    lines.extend(
        [
            "",
            "Secondary paired mean differences:",
            "",
            "| Candidate | Consensus | Valid actions | Efficiency | Turns | Public tokens | Output tokens |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for label, comparison in report["comparisons"].items():
        secondary = comparison["secondary_paired_mean_differences"]
        lines.append(
            f"| {label} | {secondary['consensus']:+.3f} | {secondary['action_valid']:+.3f} | "
            f"{secondary['efficiency']:+.3f} | {secondary['llm_turns']:+.2f} | "
            f"{secondary['public_tokens']:+.1f} | {secondary['output_tokens']:+.1f} |"
        )
    lines.extend(
        [
            "",
            "The p-value is descriptive for the locked paired screen; it is not corrected for selecting "
            "among sweep arms.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    if args.num_scenarios is not None and args.num_scenarios <= 0:
        raise SystemExit("--num-scenarios must be positive")
    if args.bootstrap_replicates < 100:
        raise SystemExit("--bootstrap-replicates must be at least 100")
    baseline_label, baseline_path = args.baseline
    labeled_paths = [(baseline_label, baseline_path), *args.candidate]
    labels = [label for label, _ in labeled_paths]
    if len(labels) != len(set(labels)):
        raise SystemExit("evaluation labels must be unique")

    all_rows = {
        label: load_rows(path, seed_base=args.seed_base, num_scenarios=args.num_scenarios)
        for label, path in labeled_paths
    }
    assert_comparable(all_rows)
    baseline = all_rows[baseline_label]
    models = {label: model_report(all_rows[label], path) for label, path in labeled_paths}
    comparisons = {}
    metrics = ("consensus", "action_valid", "efficiency", "llm_turns", "public_tokens", "output_tokens")
    for candidate_index, (label, _) in enumerate(args.candidate, start=1):
        candidate = all_rows[label]
        comparisons[label] = {
            "socially_optimal": paired_primary_report(
                baseline,
                candidate,
                bootstrap_replicates=args.bootstrap_replicates,
                bootstrap_seed=args.bootstrap_seed + candidate_index,
            ),
            "secondary_paired_mean_differences": {
                metric: paired_mean_difference(baseline, candidate, metric) for metric in metrics
            },
        }

    seeds = sorted(baseline)
    report = {
        "artifact_version": 1,
        "baseline_label": baseline_label,
        "num_scenarios": len(seeds),
        "seed_min": seeds[0],
        "seed_max": seeds[-1],
        "models": models,
        "comparisons": comparisons,
    }
    output_prefix = Path(args.output_prefix).expanduser()
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    output_prefix.with_suffix(".json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    output_prefix.with_suffix(".md").write_text(markdown_report(report), encoding="utf-8")
    print(markdown_report(report))


if __name__ == "__main__":
    main()
