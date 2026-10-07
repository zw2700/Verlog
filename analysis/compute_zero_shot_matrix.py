#!/usr/bin/env python3
"""Compare all cells in a zero-shot thinking x temperature manifest."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CATEGORY = _load_module(
    "compute_category_metrics", ROOT / "analysis/v1/compute_category_metrics.py"
)
SCENARIO = _load_module(
    "compute_preference_scenario_metrics",
    ROOT / "analysis/v1.5/compute_preference_scenario_metrics.py",
)

CATEGORIES = (
    "instant_decision",
    "negotiation",
    "stalled_coordination_failure",
    "malformed_or_other",
)
FOCUS_SCENARIOS = ("all", "all_three_share_top", "no_pair_shares_top")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            row["_source_line"] = line_number
            rows.append(row)
    return rows


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def action_error_counts(episode: dict[str, Any]) -> tuple[int, int, int]:
    turns = format_errors = invalid_errors = 0
    for stats in (episode.get("agent_turn_stats") or {}).values():
        if not isinstance(stats, dict):
            continue
        turns += int(stats.get("turns") or 0)
        format_errors += int(stats.get("format_errors") or 0)
        invalid_errors += int(stats.get("invalid_errors") or 0)
    return turns, format_errors, invalid_errors


def episode_record(cell: dict[str, Any], episode: dict[str, Any]) -> dict[str, Any]:
    category, category_reason, features = CATEGORY.categorize_episode(episode)
    scenario, _ = SCENARIO.preference_scenario(episode)
    action_turns, format_errors, invalid_errors = action_error_counts(episode)
    logged_turns = episode.get("turns") or []
    reasoning_entries = [
        turn.get("native_reasoning") or {}
        for turn in logged_turns
        if (turn.get("native_reasoning") or {}).get("present")
    ]
    return {
        "cell": cell["slug"],
        "reasoning_mode": cell["reasoning_mode"],
        "temperature": cell["temperature"],
        "seed": episode.get("seed"),
        "source_line": episode.get("_source_line"),
        "category": category,
        "category_reason": category_reason,
        "scenario": scenario,
        "consensus": bool(episode.get("consensus")),
        "socially_optimal": bool(episode.get("socially_optimal")),
        "social_welfare_efficiency": episode.get("social_welfare_efficiency"),
        "total_turns": features.get("total_turns", episode.get("total_turns")),
        "tokens_used": episode.get("tokens_used"),
        "action_turns": action_turns,
        "format_errors": format_errors,
        "invalid_errors": invalid_errors,
        "logged_turns": len(logged_turns),
        "truncated_responses": sum(
            1 for turn in logged_turns if turn.get("response_truncated")
        ),
        "missing_visible_actions": sum(
            1 for turn in logged_turns if turn.get("visible_action_missing")
        ),
        "group_message_turns": sum(
            1 for turn in logged_turns if (turn.get("actions") or {}).get("group_messages")
        ),
        "vote_turns": sum(
            1 for turn in logged_turns if (turn.get("actions") or {}).get("votes")
        ),
        "wait_turns": sum(
            1
            for turn in logged_turns
            if (turn.get("actions") or {}).get("wait_count")
            or (turn.get("actions") or {}).get("wait_for")
        ),
        "reasoning_turns": len(reasoning_entries),
        "reasoning_characters": sum(int(entry.get("characters") or 0) for entry in reasoning_entries),
        "episode": episode,
    }


def summarize(cell: dict[str, Any], scenario: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(record["category"] for record in records)
    consensus = [record for record in records if record["consensus"]]
    socially_optimal = [record for record in records if record["socially_optimal"]]
    consensus_so = [record for record in consensus if record["socially_optimal"]]
    efficiencies = [
        float(record["social_welfare_efficiency"])
        for record in records
        if isinstance(record.get("social_welfare_efficiency"), (int, float))
    ]
    turns = [
        float(record["total_turns"])
        for record in records
        if isinstance(record.get("total_turns"), (int, float))
    ]
    tokens = [
        float(record["tokens_used"])
        for record in records
        if isinstance(record.get("tokens_used"), (int, float))
    ]
    action_turns = sum(record["action_turns"] for record in records)
    logged_turns = sum(record["logged_turns"] for record in records)
    reasoning_turns = sum(record["reasoning_turns"] for record in records)
    row = {
        "cell": cell["slug"],
        "reasoning_mode": cell["reasoning_mode"],
        "temperature": cell["temperature"],
        "scenario": scenario,
        "episode_count": len(records),
        "consensus_rate": rate(len(consensus), len(records)),
        "social_optimality_rate": rate(len(socially_optimal), len(records)),
        "social_optimality_given_consensus": rate(len(consensus_so), len(consensus)),
        "avg_social_welfare_efficiency": mean(efficiencies),
        "avg_total_turns": mean(turns),
        "avg_shared_tokens_used": mean(tokens),
        "format_error_rate": rate(sum(record["format_errors"] for record in records), action_turns),
        "invalid_action_rate": rate(sum(record["invalid_errors"] for record in records), action_turns),
        "truncated_response_rate": rate(
            sum(record["truncated_responses"] for record in records), logged_turns
        ),
        "missing_visible_action_rate": rate(
            sum(record["missing_visible_actions"] for record in records), logged_turns
        ),
        "group_message_turn_rate": rate(
            sum(record["group_message_turns"] for record in records), logged_turns
        ),
        "vote_turn_rate": rate(sum(record["vote_turns"] for record in records), logged_turns),
        "wait_turn_rate": rate(sum(record["wait_turns"] for record in records), logged_turns),
        "avg_reasoning_characters": rate(
            sum(record["reasoning_characters"] for record in records), reasoning_turns
        ),
    }
    for category in CATEGORIES:
        row[f"{category}_count"] = counts[category]
        row[f"{category}_rate"] = rate(counts[category], len(records))
    return row


def private_reasoning(turn: dict[str, Any]) -> str | None:
    reasoning = turn.get("native_reasoning") or {}
    if reasoning.get("text"):
        return str(reasoning["text"])
    match = re.search(
        r"<think>(.*?)</think>",
        str(turn.get("output") or ""),
        flags=re.DOTALL | re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def qualitative_trace_pairs(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pairs = []
    selectors = (
        (
            "conflicting_success",
            lambda record: record["scenario"] == "no_pair_shares_top"
            and record["consensus"]
            and record["socially_optimal"],
        ),
        (
            "conflicting_instant_decision",
            lambda record: record["scenario"] == "no_pair_shares_top"
            and record["category"] == "instant_decision",
        ),
        (
            "long_ineffective_discussion",
            lambda record: record["category"] == "negotiation"
            and not record["socially_optimal"],
        ),
    )
    for label, selector in selectors:
        matches = [record for record in records if selector(record)]
        matches.sort(key=lambda record: float(record.get("total_turns") or 0), reverse=True)
        if not matches:
            continue
        selected = matches[0]
        same_seed = [record for record in records if record["seed"] == selected["seed"]]
        same_seed.sort(key=lambda record: record["cell"])
        pairs.append(
            {
                "trace_type": label,
                "seed": selected["seed"],
                "selected_from_cell": selected["cell"],
                "cells": [
                    {
                        "cell": record["cell"],
                        "reasoning_mode": record["reasoning_mode"],
                        "temperature": record["temperature"],
                        "source_line": record["source_line"],
                        "scenario": record["scenario"],
                        "category": record["category"],
                        "consensus": record["consensus"],
                        "socially_optimal": record["socially_optimal"],
                        "social_welfare_efficiency": record["social_welfare_efficiency"],
                        "total_turns": record["total_turns"],
                        "turns": [
                            {
                                "agent": turn.get("agent"),
                                "private_reasoning": private_reasoning(turn),
                                "visible_action": turn.get("action_text"),
                                "actions": turn.get("actions"),
                                "finish_reason": turn.get("provider_finish_reason"),
                                "response_truncated": bool(turn.get("response_truncated")),
                                "visible_action_missing": bool(
                                    turn.get("visible_action_missing")
                                ),
                            }
                            for turn in (record["episode"].get("turns") or [])
                        ],
                    }
                    for record in same_seed
                ],
            }
        )
    return pairs


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def markdown(rows: list[dict[str, Any]], manifest: dict[str, Any]) -> str:
    lines = [
        "# Zero-shot thinking × temperature matrix",
        "",
        f"- Run: `{manifest['run_id']}`",
        f"- Seeds: `{manifest['shared']['episode_seeds'][0]}`–`{manifest['shared']['episode_seeds'][-1]}`",
        f"- Model: `{manifest['shared']['model']}`",
        "",
        "## Reasoning-mode signature (all episodes)",
        "",
        (
            "| Cell | N | Instant | Negotiate | Group/turn | Vote/turn | Wait/turn | "
            "Reason chars | Truncated | Missing action |"
        ),
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        if row["scenario"] != "all":
            continue
        lines.append(
            "| {cell} | {episode_count} | {instant_decision_rate} | {negotiation_rate} | "
            "{group_message_turn_rate} | {vote_turn_rate} | {wait_turn_rate} | "
            "{avg_reasoning_characters} | {truncated_response_rate} | "
            "{missing_visible_action_rate} |".format(
                **{key: fmt(value) for key, value in row.items()}
            )
        )
    lines.append("")
    for scenario in FOCUS_SCENARIOS:
        lines.extend(
            [
                f"## {scenario}",
                "",
                (
                    "| Cell | N | Instant | Negotiate | Stalled | Consensus | SO | SO|cons | "
                    "Eff | Turns | Tokens | Format err | Invalid |"
                    " Truncated | Missing action |"
                ),
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in rows:
            if row["scenario"] != scenario:
                continue
            lines.append(
                "| {cell} | {episode_count} | {instant_decision_rate} | {negotiation_rate} | "
                "{stalled_coordination_failure_rate} | {consensus_rate} | {social_optimality_rate} | "
                "{social_optimality_given_consensus} | {avg_social_welfare_efficiency} | "
                "{avg_total_turns} | {avg_shared_tokens_used} | {format_error_rate} | "
                "{invalid_action_rate} | {truncated_response_rate} | "
                "{missing_visible_action_rate} |".format(
                    **{key: fmt(value) for key, value in row.items()}
                )
            )
        lines.append("")
    return "\n".join(lines)


def run(manifest_path: Path, output_dir: Path | None = None) -> list[dict[str, Any]]:
    manifest = json.loads(manifest_path.read_text())
    output_dir = output_dir or manifest_path.parent / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    all_records = []
    by_cell: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cell in manifest["cells"]:
        episodes = read_jsonl(Path(cell["episode_jsonl"]))
        for episode in episodes:
            record = episode_record(cell, episode)
            all_records.append(record)
            by_cell[cell["slug"]].append(record)

    summary = []
    for cell in manifest["cells"]:
        records = by_cell[cell["slug"]]
        summary.append(summarize(cell, "all", records))
        for scenario in SCENARIO.SCENARIO_ORDER:
            scenario_records = [record for record in records if record["scenario"] == scenario]
            if scenario_records:
                summary.append(summarize(cell, scenario, scenario_records))

    traces = qualitative_trace_pairs(all_records)
    write_csv(output_dir / "matrix_summary.csv", summary)
    (output_dir / "matrix_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    (output_dir / "matrix_summary.md").write_text(markdown(summary, manifest) + "\n")
    (output_dir / "qualitative_trace_pairs.json").write_text(
        json.dumps(traces, indent=2, sort_keys=True) + "\n"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    run(args.manifest, args.output_dir)


if __name__ == "__main__":
    main()
