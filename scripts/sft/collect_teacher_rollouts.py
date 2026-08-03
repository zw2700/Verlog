#!/usr/bin/env python3
"""Collect repeated teacher self-play attempts for fixed hiring scenarios."""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from scripts.sft.rollout_core import (
    add_provider_arguments,
    add_rollout_environment_arguments,
    append_jsonl,
    bootstrap_env_file,
    env_config_hash,
    is_clean_socially_optimal,
    iter_jsonl,
    load_env_config,
    load_target_tokenizer,
    make_client,
    resolve_seeds,
    run_captured_episode,
)


def parse_args() -> argparse.Namespace:
    bootstrap_env_file()
    parser = argparse.ArgumentParser(description=__doc__)
    add_provider_arguments(parser)
    add_rollout_environment_arguments(parser)
    parser.add_argument("--output-jsonl", required=True)
    parser.add_argument("--summary-json", default=None)
    parser.add_argument("--seed-base", type=int, default=10000)
    parser.add_argument("--num-scenarios", type=int, default=2000)
    parser.add_argument("--seeds-file", default=None)
    parser.add_argument("--max-attempts-per-scenario", type=int, default=4)
    parser.add_argument(
        "--num-workers",
        type=int,
        default=8,
        help="Number of scenarios collected concurrently. Lower this if the provider rate-limits requests.",
    )
    parser.add_argument(
        "--stop-on-socially-optimal",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Stop retrying a scenario after a clean socially optimal attempt; all attempted episodes are still saved.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Continue an existing output file, skipping already-recorded scenario/attempt pairs.",
    )
    return parser.parse_args()


def load_existing_attempts(path: Path) -> tuple[dict[int, set[int]], set[int], list[dict[str, Any]]]:
    attempts: dict[int, set[int]] = {}
    successful_seeds: set[int] = set()
    rows = list(iter_jsonl([path]))
    for row in rows:
        seed = row.get("scenario_seed")
        attempt = row.get("attempt")
        if not isinstance(seed, int) or not isinstance(attempt, int):
            raise ValueError(f"Existing row lacks integer scenario_seed/attempt: {row.get('episode_uid')}")
        if attempt in attempts.setdefault(seed, set()):
            raise ValueError(f"Existing output contains duplicate seed/attempt pair: seed={seed}, attempt={attempt}")
        attempts[seed].add(attempt)
        if is_clean_socially_optimal(row):
            successful_seeds.add(seed)
    assert_scenario_fingerprints(rows)
    return attempts, successful_seeds, rows


def assert_scenario_fingerprints(rows: list[dict[str, Any]]) -> None:
    """Reject seeded scenarios whose realized environment changed across attempts."""
    by_seed: dict[int, set[str]] = {}
    for row in rows:
        fingerprint = row.get("scenario_fingerprint")
        seed = row.get("scenario_seed")
        if isinstance(seed, int) and fingerprint:
            by_seed.setdefault(seed, set()).add(str(fingerprint))
    mismatched = {seed: values for seed, values in by_seed.items() if len(values) > 1}
    if mismatched:
        examples = "; ".join(
            f"seed={seed}: {sorted(values)}" for seed, values in sorted(mismatched.items())[:3]
        )
        raise ValueError(f"Scenario fingerprint changed across attempts: {examples}")


def collection_summary(rows: list[dict[str, Any]], requested_seeds: list[int]) -> dict[str, Any]:
    requested = set(requested_seeds)
    relevant = [row for row in rows if row.get("scenario_seed") in requested]
    attempted_seeds = {int(row["scenario_seed"]) for row in relevant}
    successful_seeds = {int(row["scenario_seed"]) for row in relevant if is_clean_socially_optimal(row)}
    return {
        "requested_scenarios": len(requested_seeds),
        "attempted_scenarios": len(attempted_seeds),
        "successful_scenarios": len(successful_seeds),
        "scenario_success_rate": len(successful_seeds) / len(requested_seeds) if requested_seeds else None,
        "raw_attempts": len(relevant),
        "socially_optimal_attempts": sum(bool(row.get("socially_optimal")) for row in relevant),
        "clean_socially_optimal_attempts": sum(is_clean_socially_optimal(row) for row in relevant),
        "consensus_attempts": sum(bool(row.get("consensus")) for row in relevant),
        "llm_input_tokens": sum(int(row.get("llm_input_tokens") or 0) for row in relevant),
        "llm_output_tokens": sum(int(row.get("llm_output_tokens") or 0) for row in relevant),
    }


def collect_scenario_attempts(
    *,
    args: argparse.Namespace,
    client,
    env_config: dict[str, Any],
    scenario_index: int,
    scenario_seed: int,
    recorded_attempts: set[int],
    already_successful: bool,
    target_tokenizer,
) -> list[dict[str, Any]]:
    """Collect the missing attempts for one scenario inside a worker thread."""
    if args.stop_on_socially_optimal and already_successful:
        return []

    episodes: list[dict[str, Any]] = []
    for attempt in range(args.max_attempts_per_scenario):
        if attempt in recorded_attempts:
            continue
        episode = run_captured_episode(
            client=client,
            env_config=env_config,
            scenario_seed=scenario_seed,
            attempt=attempt,
            target_tokenizer=target_tokenizer,
            target_tokenizer_name=args.target_tokenizer,
            target_enable_thinking=args.target_enable_thinking,
            provider_name=args.provider,
            model_name=args.model,
            temperature=args.temperature,
            top_p=args.top_p,
            top_k=args.top_k,
            max_output_tokens=args.max_output_tokens,
            scenario_index=scenario_index,
            include_raw_response=args.include_raw_response,
        )
        episodes.append(episode)
        if args.stop_on_socially_optimal and is_clean_socially_optimal(episode):
            break
    return episodes


def main() -> None:
    args = parse_args()
    if args.max_attempts_per_scenario <= 0:
        raise SystemExit("--max-attempts-per-scenario must be positive")
    if args.num_workers <= 0:
        raise SystemExit("--num-workers must be positive")

    output_path = Path(args.output_jsonl).expanduser()
    env_config = load_env_config(args.env_config)
    config_hash = env_config_hash(env_config)
    seeds = resolve_seeds(
        seed_base=args.seed_base,
        num_scenarios=args.num_scenarios,
        seeds_file=args.seeds_file,
    )

    existing_attempts: dict[int, set[int]] = {}
    successful_seeds: set[int] = set()
    all_rows: list[dict[str, Any]] = []
    if output_path.exists() and output_path.stat().st_size > 0:
        if not args.resume:
            raise SystemExit(f"Output already exists: {output_path}. Pass --resume to continue it.")
        existing_attempts, successful_seeds, all_rows = load_existing_attempts(output_path)
        mismatched = {
            str(row.get("env_config_hash"))
            for row in all_rows
            if row.get("env_config_hash") is not None and row.get("env_config_hash") != config_hash
        }
        if mismatched:
            raise SystemExit(
                f"Existing output contains environment hashes {sorted(mismatched)}, expected only {config_hash}"
            )
        expected_rollout_fields = {
            "provider": args.provider,
            "teacher_model": args.model,
            "target_tokenizer": args.target_tokenizer,
            "target_enable_thinking": args.target_enable_thinking,
            "teacher_temperature": args.temperature,
            "teacher_top_p": args.top_p,
            "teacher_top_k": args.top_k,
            "teacher_max_output_tokens": args.max_output_tokens,
        }
        for field, expected in expected_rollout_fields.items():
            observed = {row.get(field) for row in all_rows if field in row}
            if observed and observed != {expected}:
                raise SystemExit(
                    f"Existing output has {field} values {sorted(map(str, observed))}, expected only {expected!r}"
                )

    target_tokenizer = load_target_tokenizer(
        args.target_tokenizer,
        trust_remote_code=args.target_tokenizer_trust_remote_code,
    )
    client = make_client(args)

    print(
        f"Collecting {len(seeds)} scenarios x <= {args.max_attempts_per_scenario} attempts "
        f"with {args.num_workers} workers provider={args.provider} model={args.model} env_hash={config_hash}",
        flush=True,
    )
    new_attempts = 0
    errors: list[tuple[int, Exception]] = []
    completed_scenarios = 0
    with ThreadPoolExecutor(max_workers=min(args.num_workers, len(seeds))) as executor:
        futures = {
            executor.submit(
                collect_scenario_attempts,
                args=args,
                client=client,
                env_config=env_config,
                scenario_index=scenario_index,
                scenario_seed=scenario_seed,
                recorded_attempts=set(existing_attempts.get(scenario_seed, set())),
                already_successful=scenario_seed in successful_seeds,
                target_tokenizer=target_tokenizer,
            ): (scenario_index, scenario_seed)
            for scenario_index, scenario_seed in enumerate(seeds)
        }
        for future in as_completed(futures):
            scenario_index, scenario_seed = futures[future]
            completed_scenarios += 1
            try:
                episodes = future.result()
            except Exception as exc:  # finish and persist other completed scenarios before failing
                errors.append((scenario_seed, exc))
                print(
                    f"[{completed_scenarios}/{len(seeds)}] seed={scenario_seed} ERROR: {exc}",
                    flush=True,
                )
                continue

            if not episodes:
                state = "already complete" if scenario_seed in successful_seeds else "no missing attempts"
                print(
                    f"[{completed_scenarios}/{len(seeds)}] seed={scenario_seed} {state}",
                    flush=True,
                )
                continue

            for episode in episodes:
                assert_scenario_fingerprints(
                    [
                        row
                        for row in all_rows
                        if row.get("scenario_seed") == episode.get("scenario_seed")
                    ]
                    + [episode]
                )
                append_jsonl(output_path, episode)
                all_rows.append(episode)
                existing_attempts.setdefault(scenario_seed, set()).add(int(episode["attempt"]))
                new_attempts += 1
                clean_optimal = is_clean_socially_optimal(episode)
                if clean_optimal:
                    successful_seeds.add(scenario_seed)
                print(
                    f"[{completed_scenarios}/{len(seeds)}] seed={scenario_seed} "
                    f"attempt={episode['attempt']} turns={len(episode.get('turns') or [])} "
                    f"consensus={episode.get('consensus')} SO={episode.get('socially_optimal')} "
                    f"clean_SO={clean_optimal} eff={episode.get('social_welfare_efficiency')}",
                    flush=True,
                )

    if errors:
        examples = "; ".join(f"seed={seed}: {exc}" for seed, exc in errors[:3])
        raise RuntimeError(
            f"Collection failed for {len(errors)} scenario(s); completed rows were saved and can be resumed. {examples}"
        )

    summary = collection_summary(all_rows, seeds)
    summary.update(
        {
            "new_attempts_this_run": new_attempts,
            "env_config_hash": config_hash,
            "env_config": env_config,
            "provider": args.provider,
            "teacher_model": args.model,
            "temperature": args.temperature,
            "top_p": args.top_p,
            "top_k": args.top_k,
            "max_output_tokens": args.max_output_tokens,
            "target_tokenizer": args.target_tokenizer,
            "max_attempts_per_scenario": args.max_attempts_per_scenario,
            "num_workers": args.num_workers,
            "stop_on_socially_optimal": args.stop_on_socially_optimal,
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
