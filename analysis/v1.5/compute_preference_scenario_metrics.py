#!/usr/bin/env python3
"""Compute metrics by professor top-preference sharing scenario.

This script is intentionally parallel to analysis/v1/compute_category_metrics.py:
it reads raw episode_log JSONL rows, recomputes the v1 process category, adds a
preference-structure scenario, and writes JSONL/CSV/Markdown artifacts.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


V1_DIR = Path(__file__).resolve().parents[1] / "v1"
sys.path.insert(0, str(V1_DIR))

from compute_category_metrics import as_int, categorize_episode, in_step_range  # noqa: E402


PROFESSOR_PAIRS = (
    ("prof_1", "prof_2"),
    ("prof_1", "prof_3"),
    ("prof_2", "prof_3"),
)

SCENARIO_ORDER = [
    "all_three_share_top",
    "only_prof_1_prof_2_share_top",
    "only_prof_1_prof_3_share_top",
    "only_prof_2_prof_3_share_top",
    "no_pair_shares_top",
    "multi_pair_without_all_three_common_top",
    "malformed_or_missing_preferences",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            row["_source_line"] = line_no
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def utility(preference_vector: list[Any], profile_vector: list[Any]) -> float:
    return sum(float(pref) * float(profile) for pref, profile in zip(preference_vector, profile_vector))


def top_set(values: list[float]) -> set[int]:
    if not values:
        return set()
    max_value = max(values)
    return {idx for idx, value in enumerate(values) if value == max_value}


def preference_scenario(ep: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    professor_interests = ep.get("professor_interests")
    student_batch = ep.get("student_batch")
    if not isinstance(professor_interests, dict) or not isinstance(student_batch, list):
        return "malformed_or_missing_preferences", {}

    agents = sorted(professor_interests)
    if len(agents) != 3:
        return "malformed_or_missing_preferences", {"agents": agents}

    try:
        top_students_by_agent = {
            agent: sorted(
                top_set(
                    [
                        utility(professor_interests[agent], student["profile_vector"])
                        for student in student_batch
                    ]
                )
            )
            for agent in agents
        }
    except (KeyError, TypeError, ValueError):
        return "malformed_or_missing_preferences", {"agents": agents}

    common_top_students = sorted(
        set(top_students_by_agent[agents[0]])
        & set(top_students_by_agent[agents[1]])
        & set(top_students_by_agent[agents[2]])
    )
    pair_shared_top = {
        f"{a}_{b}": sorted(set(top_students_by_agent[a]) & set(top_students_by_agent[b]))
        for a, b in PROFESSOR_PAIRS
    }
    shared_pairs = [pair for pair, shared in pair_shared_top.items() if shared]

    if common_top_students:
        scenario = "all_three_share_top"
    elif len(shared_pairs) == 0:
        scenario = "no_pair_shares_top"
    elif shared_pairs == ["prof_1_prof_2"]:
        scenario = "only_prof_1_prof_2_share_top"
    elif shared_pairs == ["prof_1_prof_3"]:
        scenario = "only_prof_1_prof_3_share_top"
    elif shared_pairs == ["prof_2_prof_3"]:
        scenario = "only_prof_2_prof_3_share_top"
    else:
        scenario = "multi_pair_without_all_three_common_top"

    return scenario, {
        "agents": agents,
        "top_students_by_agent": top_students_by_agent,
        "common_top_students": common_top_students,
        "pair_shared_top": pair_shared_top,
        "shared_pairs": shared_pairs,
    }


def category_counts(rows: list[dict[str, Any]]) -> str:
    counts = Counter(row["category"] for row in rows)
    if not counts:
        return ""
    return ", ".join(f"{category}={count}" for category, count in sorted(counts.items()))


def rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def build_episode_rows(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for ep in episodes:
        category, category_reason, features = categorize_episode(ep)
        scenario, scenario_features = preference_scenario(ep)
        row = {
            "source_line": ep.get("_source_line"),
            "episode_uid": ep.get("episode_uid"),
            "global_step": ep.get("global_step"),
            "epoch": ep.get("epoch"),
            "env": ep.get("env"),
            "episode_index": ep.get("episode_index"),
            "scenario": scenario,
            "category": category,
            "category_reason": category_reason,
            "consensus": bool(ep.get("consensus")),
            "chosen_student": ep.get("chosen_student"),
            "optimal_student": ep.get("optimal_student"),
            "socially_optimal": ep.get("socially_optimal"),
            "social_welfare_efficiency": ep.get("social_welfare_efficiency"),
            "chosen_student_rank_global": ep.get("chosen_student_rank_global"),
            "tokens_used": ep.get("tokens_used"),
            "token_budget": ep.get("token_budget"),
            "total_turns": features.get("total_turns", len(ep.get("turns", []))),
        }
        row.update(scenario_features)
        rows.append(row)
    return rows


def summarize_by_scenario(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[row["scenario"]].append(row)

    total = len(rows)
    summary = []
    for scenario in SCENARIO_ORDER:
        scenario_rows = buckets.get(scenario, [])
        if not scenario_rows:
            continue

        consensus_rows = [row for row in scenario_rows if row["consensus"]]
        social_rows = [row for row in scenario_rows if isinstance(row.get("socially_optimal"), bool)]
        socially_optimal_rows = [row for row in social_rows if row["socially_optimal"]]
        consensus_social_rows = [
            row for row in consensus_rows
            if isinstance(row.get("socially_optimal"), bool)
        ]
        consensus_socially_optimal_rows = [
            row for row in consensus_social_rows
            if row["socially_optimal"]
        ]
        efficiencies = [
            float(row["social_welfare_efficiency"])
            for row in scenario_rows
            if isinstance(row.get("social_welfare_efficiency"), (int, float))
        ]
        turns = [
            float(row["total_turns"])
            for row in scenario_rows
            if isinstance(row.get("total_turns"), (int, float))
        ]
        tokens = [
            float(row["tokens_used"])
            for row in scenario_rows
            if isinstance(row.get("tokens_used"), (int, float))
        ]
        summary.append(
            {
                "scenario": scenario,
                "episodes": len(scenario_rows),
                "percent": rate(len(scenario_rows), total),
                "category_counts": category_counts(scenario_rows),
                "consensus_rate": rate(len(consensus_rows), len(scenario_rows)),
                "socially_optimal_rate": rate(len(socially_optimal_rows), len(social_rows)),
                "socially_optimal_given_consensus_rate": rate(
                    len(consensus_socially_optimal_rows),
                    len(consensus_social_rows),
                ),
                "avg_social_welfare_efficiency": mean(efficiencies),
                "avg_tokens_used": mean(tokens),
                "avg_total_turns": mean(turns),
            }
        )

    return summary


def summarize_by_scenario_and_category(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[(row["scenario"], row["category"])].append(row)

    summary = []
    for scenario in SCENARIO_ORDER:
        scenario_total = sum(len(items) for (bucket_scenario, _), items in buckets.items() if bucket_scenario == scenario)
        if scenario_total == 0:
            continue
        categories = sorted(
            category
            for bucket_scenario, category in buckets
            if bucket_scenario == scenario
        )
        for category in categories:
            category_rows = buckets[(scenario, category)]
            consensus_rows = [row for row in category_rows if row["consensus"]]
            social_rows = [row for row in category_rows if isinstance(row.get("socially_optimal"), bool)]
            socially_optimal_rows = [row for row in social_rows if row["socially_optimal"]]
            consensus_social_rows = [
                row for row in consensus_rows
                if isinstance(row.get("socially_optimal"), bool)
            ]
            consensus_socially_optimal_rows = [
                row for row in consensus_social_rows
                if row["socially_optimal"]
            ]
            summary.append(
                {
                    "scenario": scenario,
                    "category": category,
                    "episodes": len(category_rows),
                    "percent_of_scenario": rate(len(category_rows), scenario_total),
                    "consensus_rate": rate(len(consensus_rows), len(category_rows)),
                    "socially_optimal_rate": rate(len(socially_optimal_rows), len(social_rows)),
                    "socially_optimal_given_consensus_rate": rate(
                        len(consensus_socially_optimal_rows),
                        len(consensus_social_rows),
                    ),
                }
            )

    return summary


def scenario_category_tables(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    scenario_rows_by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        scenario_rows_by_name[row["scenario"]].append(row)

    tables = {}
    for scenario in SCENARIO_ORDER:
        scenario_rows = scenario_rows_by_name.get(scenario, [])
        if not scenario_rows:
            continue

        category_rows_by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in scenario_rows:
            category_rows_by_name[row["category"]].append(row)

        table = []
        total = len(scenario_rows)
        for category, category_rows in sorted(
            category_rows_by_name.items(),
            key=lambda item: (-len(item[1]), item[0]),
        ):
            consensus_rows = [row for row in category_rows if row["consensus"]]
            social_rows = [row for row in category_rows if isinstance(row.get("socially_optimal"), bool)]
            socially_optimal_rows = [row for row in social_rows if row["socially_optimal"]]
            consensus_social_rows = [
                row for row in consensus_rows
                if isinstance(row.get("socially_optimal"), bool)
            ]
            consensus_socially_optimal_rows = [
                row for row in consensus_social_rows
                if row["socially_optimal"]
            ]
            efficiencies = [
                float(row["social_welfare_efficiency"])
                for row in category_rows
                if isinstance(row.get("social_welfare_efficiency"), (int, float))
            ]
            ranks = [
                float(row["chosen_student_rank_global"])
                for row in consensus_rows
                if isinstance(row.get("chosen_student_rank_global"), (int, float))
            ]
            tokens = [
                float(row["tokens_used"])
                for row in category_rows
                if isinstance(row.get("tokens_used"), (int, float))
            ]
            turns = [
                float(row["total_turns"])
                for row in category_rows
                if isinstance(row.get("total_turns"), (int, float))
            ]
            table.append(
                {
                    "category": category,
                    "episodes": len(category_rows),
                    "percent": rate(len(category_rows), total),
                    "consensus_rate": rate(len(consensus_rows), len(category_rows)),
                    "socially_optimal_rate": rate(len(socially_optimal_rows), len(social_rows)),
                    "socially_optimal_given_consensus_rate": rate(
                        len(consensus_socially_optimal_rows),
                        len(consensus_social_rows),
                    ),
                    "avg_social_welfare_efficiency": mean(efficiencies),
                    "avg_chosen_student_rank_global_consensus_only": mean(ranks),
                    "avg_tokens_used": mean(tokens),
                    "avg_total_turns": mean(turns),
                }
            )
        tables[scenario] = table

    return tables


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if fieldnames:
            writer.writeheader()
            writer.writerows(rows)


def write_outputs(
    out_dir: Path,
    episode_rows: list[dict[str, Any]],
    scenario_summary: list[dict[str, Any]],
    scenario_category_summary: list[dict[str, Any]],
    args: argparse.Namespace,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(out_dir / "episode_preference_scenario_labels.jsonl", episode_rows)

    with (out_dir / "preference_scenario_metrics_summary.json").open("w") as f:
        json.dump(scenario_summary, f, indent=2, sort_keys=True)
        f.write("\n")
    write_csv(out_dir / "preference_scenario_metrics_summary.csv", scenario_summary)
    write_csv(out_dir / "preference_scenario_category_breakdown.csv", scenario_category_summary)

    lines = [
        "# Preference Scenario Metrics Summary",
        "",
        f"- episode_log: `{args.episode_log}`",
        f"- global_step range: `{args.step_start}` to `{args.step_end}`",
        f"- episodes analyzed: `{len(episode_rows)}`",
        "",
        "Scenario definitions use each professor's top-ranked student set. Ties are allowed.",
        "",
    ]

    scenario_summary_by_name = {row["scenario"]: row for row in scenario_summary}
    tables = scenario_category_tables(episode_rows)
    for scenario in SCENARIO_ORDER:
        table = tables.get(scenario)
        if not table:
            continue
        summary = scenario_summary_by_name[scenario]
        lines.extend(
            [
                f"## {scenario}",
                "",
                f"- episodes: `{summary['episodes']}`",
                f"- percent of analyzed episodes: `{fmt(summary['percent'])}`",
                f"- consensus rate: `{fmt(summary['consensus_rate'])}`",
                f"- SO rate: `{fmt(summary['socially_optimal_rate'])}`",
                f"- SO|cons rate: `{fmt(summary['socially_optimal_given_consensus_rate'])}`",
                "",
                "| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in table:
            lines.append(
                "| {category} | {episodes} | {percent} | {consensus} | {so} | {so_cons} | {eff} | {rank} | {tokens} | {turns} |".format(
                    category=row["category"],
                    episodes=row["episodes"],
                    percent=fmt(row["percent"]),
                    consensus=fmt(row["consensus_rate"]),
                    so=fmt(row["socially_optimal_rate"]),
                    so_cons=fmt(row["socially_optimal_given_consensus_rate"]),
                    eff=fmt(row["avg_social_welfare_efficiency"]),
                    rank=fmt(row["avg_chosen_student_rank_global_consensus_only"]),
                    tokens=fmt(row["avg_tokens_used"], 1),
                    turns=fmt(row["avg_total_turns"], 1),
                )
            )
        lines.append("")

    lines.append("")
    (out_dir / "preference_scenario_metrics_summary.md").write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode-log", required=True, type=Path, help="Path to episode_log_*.jsonl")
    parser.add_argument("--step-start", type=int, default=None, help="Inclusive global_step lower bound")
    parser.add_argument("--step-end", type=int, default=None, help="Inclusive global_step upper bound")
    parser.add_argument("--out-dir", required=True, type=Path, help="Directory for output artifacts")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    episodes = [
        ep for ep in read_jsonl(args.episode_log)
        if in_step_range(ep, args.step_start, args.step_end)
    ]
    episode_rows = build_episode_rows(episodes)
    scenario_summary = summarize_by_scenario(episode_rows)
    scenario_category_summary = summarize_by_scenario_and_category(episode_rows)
    write_outputs(
        args.out_dir,
        episode_rows,
        scenario_summary,
        scenario_category_summary,
        args,
    )


if __name__ == "__main__":
    main()
