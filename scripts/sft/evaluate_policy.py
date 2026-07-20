#!/usr/bin/env python3
"""Evaluate a policy on locked hiring scenarios without best-of-N selection."""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from statistics import mean
from typing import Any

from scripts.sft.rollout_core import (
    action_error_counts,
    add_provider_arguments,
    add_rollout_environment_arguments,
    append_jsonl,
    bootstrap_env_file,
    env_config_hash,
    iter_jsonl,
    load_env_config,
    load_target_tokenizer,
    make_client,
    resolve_seeds,
    run_captured_episode,
    wilson_interval,
)


def parse_args() -> argparse.Namespace:
    bootstrap_env_file()
    parser = argparse.ArgumentParser(description=__doc__)
    add_provider_arguments(parser)
    add_rollout_environment_arguments(parser, tokenizer_required=False)
    parser.add_argument("--output-jsonl", required=True)
    parser.add_argument("--summary-json", default=None)
    parser.add_argument("--seed-base", type=int, default=0)
    parser.add_argument("--num-scenarios", type=int, default=500)
    parser.add_argument("--seeds-file", default=None)
    parser.add_argument("--samples-per-scenario", type=int, default=1)
    parser.add_argument("--num-workers", type=int, default=8)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def summarize_evaluation(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    consensus = sum(bool(row.get("consensus")) for row in rows)
    socially_optimal = sum(bool(row.get("socially_optimal")) for row in rows)
    consensus_socially_optimal = sum(bool(row.get("consensus")) and bool(row.get("socially_optimal")) for row in rows)
    valid = 0
    for row in rows:
        format_errors, invalid_errors = action_error_counts(row)
        valid += format_errors == 0 and invalid_errors == 0
    efficiencies = [
        float(row["social_welfare_efficiency"])
        for row in rows
        if isinstance(row.get("social_welfare_efficiency"), int | float)
    ]
    so_low, so_high = wilson_interval(socially_optimal, total)
    consensus_low, consensus_high = wilson_interval(consensus, total)
    return {
        "episodes": total,
        "unique_scenarios": len({row.get("scenario_id") for row in rows}),
        "consensus_rate": consensus / total if total else None,
        "consensus_rate_95ci": [consensus_low, consensus_high],
        "socially_optimal_rate": socially_optimal / total if total else None,
        "socially_optimal_rate_95ci": [so_low, so_high],
        "socially_optimal_given_consensus_rate": consensus_socially_optimal / consensus if consensus else None,
        "action_valid_episode_rate": valid / total if total else None,
        "mean_social_welfare_efficiency": mean(efficiencies) if efficiencies else None,
        "mean_llm_turns": mean(len(row.get("turns") or []) for row in rows) if rows else None,
        "mean_public_tokens": mean(float(row.get("tokens_used") or 0) for row in rows) if rows else None,
        "mean_llm_output_tokens": mean(float(row.get("llm_output_tokens") or 0) for row in rows) if rows else None,
        "llm_input_tokens": sum(int(row.get("llm_input_tokens") or 0) for row in rows),
        "llm_output_tokens": sum(int(row.get("llm_output_tokens") or 0) for row in rows),
    }


def main() -> None:
    args = parse_args()
    if args.samples_per_scenario <= 0:
        raise SystemExit("--samples-per-scenario must be positive")
    if args.num_workers <= 0:
        raise SystemExit("--num-workers must be positive")
    output_path = Path(args.output_jsonl).expanduser()
    env_config = load_env_config(args.env_config)
    expected_config_hash = env_config_hash(env_config)
    seeds = resolve_seeds(
        seed_base=args.seed_base,
        num_scenarios=args.num_scenarios,
        seeds_file=args.seeds_file,
    )
    tokenizer_name = args.target_tokenizer or args.model
    target_tokenizer = load_target_tokenizer(
        tokenizer_name,
        trust_remote_code=args.target_tokenizer_trust_remote_code,
    )

    rows: list[dict[str, Any]] = []
    recorded: set[tuple[int, int]] = set()
    if output_path.exists() and output_path.stat().st_size > 0:
        if not args.resume:
            raise SystemExit(f"Output already exists: {output_path}. Pass --resume to continue it.")
        rows = list(iter_jsonl([output_path]))
        for row in rows:
            if row.get("env_config_hash") != expected_config_hash:
                raise SystemExit(
                    f"Existing evaluation row has env hash {row.get('env_config_hash')}, "
                    f"expected {expected_config_hash}"
                )
            pair = (int(row["scenario_seed"]), int(row["attempt"]))
            if pair in recorded:
                raise SystemExit(f"Existing evaluation output contains duplicate seed/sample pair: {pair}")
            recorded.add(pair)
        expected_rollout_fields = {
            "provider": args.provider,
            "teacher_model": args.model,
            "target_tokenizer": tokenizer_name,
            "target_enable_thinking": args.target_enable_thinking,
            "teacher_temperature": args.temperature,
        }
        for field, expected in expected_rollout_fields.items():
            observed = {row.get(field) for row in rows if field in row}
            if observed and observed != {expected}:
                raise SystemExit(
                    f"Existing evaluation has {field} values {sorted(map(str, observed))}, expected only {expected!r}"
                )

    client = make_client(args)
    print(
        f"Evaluating {args.model} on {len(seeds)} scenarios x {args.samples_per_scenario} samples "
        f"with {args.num_workers} workers env_hash={expected_config_hash}",
        flush=True,
    )
    new_episodes = 0
    jobs = [
        (scenario_index, scenario_seed, sample_index)
        for scenario_index, scenario_seed in enumerate(seeds)
        for sample_index in range(args.samples_per_scenario)
        if (scenario_seed, sample_index) not in recorded
    ]
    errors: list[tuple[int, int, Exception]] = []
    with ThreadPoolExecutor(max_workers=min(args.num_workers, max(len(jobs), 1))) as executor:
        futures = {
            executor.submit(
                run_captured_episode,
                client=client,
                env_config=env_config,
                scenario_seed=scenario_seed,
                attempt=sample_index,
                target_tokenizer=target_tokenizer,
                target_tokenizer_name=tokenizer_name,
                target_enable_thinking=args.target_enable_thinking,
                provider_name=args.provider,
                model_name=args.model,
                temperature=args.temperature,
                scenario_index=scenario_index,
                include_raw_response=args.include_raw_response,
            ): (scenario_seed, sample_index)
            for scenario_index, scenario_seed, sample_index in jobs
        }
        for completed_index, future in enumerate(as_completed(futures), start=1):
            scenario_seed, sample_index = futures[future]
            try:
                episode = future.result()
            except Exception as exc:  # finish and persist other completed episodes before failing
                errors.append((scenario_seed, sample_index, exc))
                print(
                    f"[{completed_index}/{len(jobs)}] seed={scenario_seed} sample={sample_index} ERROR: {exc}",
                    flush=True,
                )
                continue
            episode["rollout_purpose"] = "evaluation"
            append_jsonl(output_path, episode)
            rows.append(episode)
            recorded.add((scenario_seed, sample_index))
            new_episodes += 1
            print(
                f"[{completed_index}/{len(jobs)}] seed={scenario_seed} sample={sample_index} "
                f"consensus={episode.get('consensus')} SO={episode.get('socially_optimal')} "
                f"eff={episode.get('social_welfare_efficiency')} turns={len(episode.get('turns') or [])}",
                flush=True,
            )

    if errors:
        examples = "; ".join(f"seed={seed}/sample={sample}: {exc}" for seed, sample, exc in errors[:3])
        raise RuntimeError(
            f"Evaluation failed for {len(errors)} episode(s); completed rows were saved and can be resumed. {examples}"
        )

    requested_pairs = {(seed, sample) for seed in seeds for sample in range(args.samples_per_scenario)}
    relevant_rows = [
        row for row in rows if (int(row.get("scenario_seed", -1)), int(row.get("attempt", -1))) in requested_pairs
    ]
    summary = summarize_evaluation(relevant_rows)
    summary.update(
        {
            "model": args.model,
            "provider": args.provider,
            "temperature": args.temperature,
            "target_tokenizer": tokenizer_name,
            "env_config": env_config,
            "env_config_hash": expected_config_hash,
            "samples_per_scenario": args.samples_per_scenario,
            "num_workers": args.num_workers,
            "new_episodes_this_run": new_episodes,
        }
    )
    summary_path = (
        Path(args.summary_json).expanduser() if args.summary_json else output_path.with_suffix(".summary.json")
    )
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
