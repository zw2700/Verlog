#!/usr/bin/env python3
"""Create deterministic nested raw-data arms and a compact-target ablation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from scripts.sft.build_dataset import compact_teacher_output
from scripts.sft.rollout_core import count_chat_tokens, load_target_tokenizer
from verl.envs import hiring_episode_logging as episode_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, help="Raw dataset containing train/validation Parquet files")
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--target-tokenizer", default="Qwen/Qwen3-4B")
    parser.add_argument("--target-tokenizer-trust-remote-code", action="store_true")
    parser.add_argument("--subset-seed", type=int, default=1)
    parser.add_argument("--max-think-tokens", type=int, default=64)
    parser.add_argument("--global-batch-size", type=int, default=32)
    parser.add_argument("--audit-samples", type=int, default=20)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rank_scenarios(scenario_ids: Iterable[str], *, subset_seed: int) -> list[str]:
    unique = set(map(str, scenario_ids))
    return sorted(unique, key=lambda scenario_id: hashlib.sha256(f"{subset_seed}:{scenario_id}".encode()).digest())


def subset_scenario_ids(ranked_ids: list[str], fraction: float) -> set[str]:
    if not 0 < fraction <= 1:
        raise ValueError("subset fractions must be in (0, 1]")
    count = max(1, min(round(fraction * len(ranked_ids)), len(ranked_ids)))
    return set(ranked_ids[:count])


def numeric_summary(values: Iterable[int | float]) -> dict[str, float | int | None]:
    numbers = sorted(float(value) for value in values)
    if not numbers:
        return {"count": 0, "min": None, "mean": None, "p50": None, "p90": None, "p99": None, "max": None}

    def percentile(fraction: float) -> float:
        return numbers[min(round(fraction * (len(numbers) - 1)), len(numbers) - 1)]

    return {
        "count": len(numbers),
        "min": numbers[0],
        "mean": sum(numbers) / len(numbers),
        "p50": percentile(0.50),
        "p90": percentile(0.90),
        "p99": percentile(0.99),
        "max": numbers[-1],
    }


def validate_source(train: pd.DataFrame, validation: pd.DataFrame) -> None:
    required = {
        "messages",
        "enable_thinking",
        "scenario_id",
        "scenario_seed",
        "target_format",
        "prompt_tokens",
        "response_tokens",
        "sequence_tokens",
    }
    for split, frame in (("train", train), ("validation", validation)):
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"{split} dataset lacks columns: {sorted(missing)}")
        if set(frame["target_format"].unique()) != {"raw"}:
            raise ValueError(f"{split} source must contain only raw targets")
        if frame.empty:
            raise ValueError(f"{split} dataset is empty")
    overlap = set(train["scenario_id"]) & set(validation["scenario_id"])
    if overlap:
        raise ValueError(f"train/validation scenario overlap: {sorted(overlap)[:3]}")


def compact_frame(
    frame: pd.DataFrame,
    tokenizer,
    *,
    max_think_tokens: int,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    compacted = frame.copy(deep=True)
    audits: list[dict[str, Any]] = []
    for index in compacted.index:
        messages = episode_logging.json_safe(compacted.at[index, "messages"])
        if not messages or messages[-1].get("role") != "assistant":
            raise ValueError(f"row {index} does not end with an assistant target")
        raw_output = str(messages[-1].get("content") or "")
        compact_output = compact_teacher_output(raw_output, tokenizer, max_think_tokens=max_think_tokens)
        raw_action = episode_logging.extract_action_text(raw_output)
        compact_action = episode_logging.extract_action_text(compact_output)
        if compact_action != raw_action:
            raise AssertionError(f"row {index} compacting changed the action suffix")

        messages[-1] = {**messages[-1], "content": compact_output}
        response_tokens = len(tokenizer.encode(compact_output, add_special_tokens=False))
        sequence_tokens = count_chat_tokens(
            tokenizer,
            messages,
            add_generation_prompt=False,
            enable_thinking=bool(compacted.at[index, "enable_thinking"]),
        )
        if response_tokens > 512 or sequence_tokens > 4608:
            raise ValueError(
                f"row {index} exceeds training limits after compaction: "
                f"response={response_tokens}, sequence={sequence_tokens}"
            )
        raw_response_tokens = int(compacted.at[index, "response_tokens"])
        compacted.at[index, "messages"] = messages
        compacted.at[index, "target_format"] = "compact-think"
        compacted.at[index, "response_tokens"] = response_tokens
        compacted.at[index, "sequence_tokens"] = sequence_tokens
        audits.append(
            {
                "scenario_id": str(compacted.at[index, "scenario_id"]),
                "scenario_seed": int(compacted.at[index, "scenario_seed"]),
                "turn_index": int(compacted.at[index, "turn_index"]),
                "agent": str(compacted.at[index, "agent"]),
                "raw_response_tokens": raw_response_tokens,
                "compact_response_tokens": response_tokens,
                "tokens_removed": raw_response_tokens - response_tokens,
                "action_preserved": True,
                "raw_output": raw_output,
                "compact_output": compact_output,
            }
        )
    return compacted, audits


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(episode_logging.json_safe(row), sort_keys=True) + "\n")


def write_compaction_markdown(path: Path, audits: list[dict[str, Any]], *, count: int) -> None:
    examples = sorted(audits, key=lambda row: (row["tokens_removed"], row["scenario_id"]), reverse=True)[:count]
    lines = [
        "# Compact-target audit",
        "",
        "These are the examples with the largest target-token reductions. "
        "The action suffix is checked programmatically.",
        "",
    ]
    for number, row in enumerate(examples, start=1):
        lines.extend(
            [
                f"## Example {number}: {row['scenario_id']} turn {row['turn_index']} ({row['agent']})",
                "",
                f"Raw {row['raw_response_tokens']} tokens; compact {row['compact_response_tokens']} tokens; "
                f"removed {row['tokens_removed']}.",
                "",
                "### Before",
                "",
                "```text",
                row["raw_output"],
                "```",
                "",
                "### After",
                "",
                "```text",
                row["compact_output"],
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def dataset_report(
    *,
    name: str,
    train: pd.DataFrame,
    validation: pd.DataFrame,
    source_hashes: dict[str, str],
    subset_seed: int,
    global_batch_size: int,
    compact_target_only: bool,
) -> dict[str, Any]:
    all_rows = pd.concat([train, validation], ignore_index=True)
    scenario_ids = sorted(map(str, train["scenario_id"].unique()))
    return {
        "artifact_version": 1,
        "arm": name,
        "source_sha256": source_hashes,
        "subset_seed": subset_seed,
        "train_scenarios": int(train["scenario_id"].nunique()),
        "validation_scenarios": int(validation["scenario_id"].nunique()),
        "train_decision_rows": len(train),
        "validation_decision_rows": len(validation),
        "expected_optimizer_steps_per_epoch_global_batch_32": math.floor(len(train) / global_batch_size),
        "global_batch_size_for_step_estimate": global_batch_size,
        "target_format": str(train["target_format"].iloc[0]),
        "target_enable_thinking": bool(train["enable_thinking"].iloc[0]),
        "compact_target_only": compact_target_only,
        "trajectory_consistent": not compact_target_only,
        "prompt_history_format": "raw-teacher-trajectory",
        "train_scenario_ids_sha256": hashlib.sha256("\n".join(scenario_ids).encode()).hexdigest(),
        "response_tokens": numeric_summary(all_rows["response_tokens"]),
        "sequence_tokens": numeric_summary(all_rows["sequence_tokens"]),
    }


def main() -> None:
    args = parse_args()
    if args.max_think_tokens <= 0 or args.global_batch_size <= 0 or args.audit_samples < 0:
        raise SystemExit("token, batch, and audit settings must be nonnegative (positive except audit samples)")

    source_dir = Path(args.source_dir).expanduser().resolve()
    output_root = Path(args.output_root).expanduser().resolve()
    train_path = source_dir / "train.parquet"
    validation_path = source_dir / "validation.parquet"
    selected_path = source_dir / "selected_episodes.jsonl"
    for path in (train_path, validation_path, selected_path):
        if not path.is_file():
            raise SystemExit(f"Missing source artifact: {path}")

    arm_names = ("raw25", "raw50", "raw100", "compact100")
    existing = [str(output_root / name) for name in arm_names if (output_root / name).exists()]
    if existing:
        raise SystemExit(f"Refusing to overwrite existing sweep datasets: {existing}")
    output_root.mkdir(parents=True, exist_ok=True)

    train = pd.read_parquet(train_path)
    validation = pd.read_parquet(validation_path)
    validate_source(train, validation)
    source_hashes = {
        "train.parquet": sha256_file(train_path),
        "validation.parquet": sha256_file(validation_path),
        "selected_episodes.jsonl": sha256_file(selected_path),
    }
    selected_rows = [json.loads(line) for line in selected_path.read_text(encoding="utf-8").splitlines() if line]
    ranked = rank_scenarios(train["scenario_id"], subset_seed=args.subset_seed)
    subset_specs = (("raw25", 0.25), ("raw50", 0.50), ("raw100", 1.0))

    tokenizer = load_target_tokenizer(
        args.target_tokenizer,
        trust_remote_code=args.target_tokenizer_trust_remote_code,
    )
    temp_root = Path(tempfile.mkdtemp(prefix=".sweep-build-", dir=output_root))
    reports: dict[str, dict[str, Any]] = {}
    try:
        raw100_train: pd.DataFrame | None = None
        for name, fraction in subset_specs:
            scenario_ids = subset_scenario_ids(ranked, fraction)
            arm_train = train[train["scenario_id"].isin(scenario_ids)].copy()
            arm_validation = validation.copy()
            if name == "raw100":
                raw100_train = arm_train.copy()
            arm_dir = temp_root / name
            arm_dir.mkdir()
            arm_train.to_parquet(arm_dir / "train.parquet", index=False)
            arm_validation.to_parquet(arm_dir / "validation.parquet", index=False)
            manifest_rows = [
                row
                for row in selected_rows
                if row.get("split") == "validation" or str(row.get("scenario_id")) in scenario_ids
            ]
            write_jsonl(arm_dir / "selected_episodes.jsonl", manifest_rows)
            report = dataset_report(
                name=name,
                train=arm_train,
                validation=arm_validation,
                source_hashes=source_hashes,
                subset_seed=args.subset_seed,
                global_batch_size=args.global_batch_size,
                compact_target_only=False,
            )
            (arm_dir / "dataset_report.json").write_text(
                json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            reports[name] = report

        assert raw100_train is not None
        compact_train, train_audits = compact_frame(
            raw100_train,
            tokenizer,
            max_think_tokens=args.max_think_tokens,
        )
        compact_validation, validation_audits = compact_frame(
            validation,
            tokenizer,
            max_think_tokens=args.max_think_tokens,
        )
        compact_dir = temp_root / "compact100"
        compact_dir.mkdir()
        compact_train.to_parquet(compact_dir / "train.parquet", index=False)
        compact_validation.to_parquet(compact_dir / "validation.parquet", index=False)
        write_jsonl(compact_dir / "selected_episodes.jsonl", selected_rows)
        all_audits = train_audits + validation_audits
        write_jsonl(compact_dir / "compaction_audit.jsonl", all_audits)
        write_compaction_markdown(compact_dir / "compaction_examples.md", all_audits, count=args.audit_samples)
        compact_report = dataset_report(
            name="compact100",
            train=compact_train,
            validation=compact_validation,
            source_hashes=source_hashes,
            subset_seed=args.subset_seed,
            global_batch_size=args.global_batch_size,
            compact_target_only=True,
        )
        compact_report.update(
            {
                "max_think_tokens": args.max_think_tokens,
                "action_suffixes_checked": len(all_audits),
                "action_suffixes_changed": sum(not row["action_preserved"] for row in all_audits),
                "raw_response_tokens_total": sum(row["raw_response_tokens"] for row in all_audits),
                "compact_response_tokens_total": sum(row["compact_response_tokens"] for row in all_audits),
            }
        )
        (compact_dir / "dataset_report.json").write_text(
            json.dumps(compact_report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        reports["compact100"] = compact_report

        for name in arm_names:
            os.rename(temp_root / name, output_root / name)
        temp_root.rmdir()
    except BaseException:
        shutil.rmtree(temp_root, ignore_errors=True)
        raise

    sweep_manifest = {
        "artifact_version": 1,
        "source_dir": str(source_dir),
        "output_root": str(output_root),
        "target_tokenizer": args.target_tokenizer,
        "subset_seed": args.subset_seed,
        "nested_train_scenarios": {
            "raw25_subset_of_raw50": subset_scenario_ids(ranked, 0.25) <= subset_scenario_ids(ranked, 0.50),
            "raw50_subset_of_raw100": subset_scenario_ids(ranked, 0.50) <= subset_scenario_ids(ranked, 1.0),
        },
        "arms": reports,
    }
    manifest_path = output_root / "sweep_manifest.json"
    manifest_path.write_text(json.dumps(sweep_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(sweep_manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
