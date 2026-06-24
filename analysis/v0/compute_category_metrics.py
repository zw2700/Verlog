#!/usr/bin/env python3
"""Compute category-level outcome metrics for the rollout analyses.

The logs only expose a professor's full utility vector after that professor
acts. These metrics are exact only for episodes where all three professors'
utility vectors are visible.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "logs" / "game_log_train_auton_12993.log"
FIRST_DIR = ROOT / "analysis" / "first10_base_policy_game_log"
FINAL_DIR = ROOT / "analysis" / "final10_train_steps_agent_model"
PROFESSORS = ("prof_1", "prof_2", "prof_3")
NUM_STUDENTS = 5


TURN_RE = re.compile(
    r"^=== (?P<ts>\S+) env=(?P<env>\d+) turn=(?P<turn>\d+) "
    r"agent=(?P<agent>prof_\d+) "
)
STUDENT_RE = re.compile(r"^\s*Student\s+(?P<student>\d+)\s+\|\s+(?P<utility>-?\d+(?:\.\d+)?)\s+\|")
DIAG_RE = re.compile(r"^=== EPISODE DIAGNOSIS \(env=(?P<env>\d+)\) ===")
REWARD_RE = re.compile(r"^\s*(?P<agent>prof_\d+): reward=(?P<reward>[+-]?\d+(?:\.\d+)?)")
CONSENSUS_YES_RE = re.compile(r"^\s*consensus: YES -> student (?P<student>\d+)")
CONSENSUS_NO_RE = re.compile(r"^\s*consensus: NO")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def rank_from_descending(values: list[float], idx: int) -> int:
    return 1 + sum(1 for value in values if value > values[idx])


def utility_matrix_from_turns(turns: list[dict[str, Any]]) -> dict[str, list[float]] | None:
    matrix: dict[str, list[float]] = {}
    for turn in turns:
        agent = turn.get("agent")
        utilities_raw = turn.get("utilities")
        if agent in PROFESSORS and isinstance(utilities_raw, dict) and agent not in matrix:
            utilities = [float(utilities_raw[str(i)]) for i in range(NUM_STUDENTS)]
            matrix[agent] = utilities
    if all(agent in matrix for agent in PROFESSORS):
        return matrix
    return None


def compute_episode_metrics(matrix: dict[str, list[float]] | None, consensus: bool, chosen_student: int | None) -> dict[str, Any]:
    if matrix is None:
        return {
            "metric_computable": False,
            "actual_total_utility": None,
            "optimal_total_utility": None,
            "optimal_student": None,
            "social_welfare_efficiency": None,
            "chosen_student_rank_global": None,
            "socially_optimal": None,
        }

    collective = [
        sum(matrix[agent][student] for agent in PROFESSORS)
        for student in range(NUM_STUDENTS)
    ]
    optimal_total = max(collective)
    optimal_student = collective.index(optimal_total)

    if consensus and chosen_student is not None:
        actual_total = collective[chosen_student]
        chosen_rank = rank_from_descending(collective, chosen_student)
        efficiency = actual_total / optimal_total if optimal_total > 0 else 0.0
        socially_optimal = chosen_rank == 1
    else:
        actual_total = 0.0
        chosen_rank = None
        efficiency = 0.0
        socially_optimal = False

    return {
        "metric_computable": True,
        "actual_total_utility": actual_total,
        "optimal_total_utility": optimal_total,
        "optimal_student": optimal_student,
        "social_welfare_efficiency": efficiency,
        "chosen_student_rank_global": chosen_rank,
        "socially_optimal": socially_optimal,
    }


def parse_first10_raw_log(line_limit_exclusive: int = 144892) -> dict[int, dict[str, Any]]:
    lines = LOG.read_text().splitlines()
    episodes: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    i = 0

    while i < min(line_limit_exclusive - 1, len(lines)):
        line_no = i + 1
        line = lines[i]
        turn_match = TURN_RE.match(line)
        if turn_match:
            if current is None:
                current = {
                    "episode_id": len(episodes) + 1,
                    "line_start": line_no,
                    "utilities_by_agent": {},
                }
            agent = turn_match.group("agent")
            utilities: list[float | None] = [None] * NUM_STUDENTS
            for j in range(i + 1, min(i + 24, len(lines))):
                student_match = STUDENT_RE.match(lines[j])
                if student_match:
                    student = int(student_match.group("student"))
                    if 0 <= student < NUM_STUDENTS:
                        utilities[student] = float(student_match.group("utility"))
            if all(value is not None for value in utilities):
                current["utilities_by_agent"].setdefault(agent, [float(value) for value in utilities])
            i += 1
            continue

        if DIAG_RE.match(line):
            if current is None:
                current = {
                    "episode_id": len(episodes) + 1,
                    "line_start": line_no,
                    "utilities_by_agent": {},
                }
            current["diagnosis_line"] = line_no
            rewards = {}
            consensus = False
            chosen_student = None
            for j in range(i + 1, min(i + 8, len(lines))):
                reward_match = REWARD_RE.match(lines[j])
                if reward_match:
                    rewards[reward_match.group("agent")] = float(reward_match.group("reward"))
                yes_match = CONSENSUS_YES_RE.match(lines[j])
                if yes_match:
                    consensus = True
                    chosen_student = int(yes_match.group("student"))
                if CONSENSUS_NO_RE.match(lines[j]):
                    consensus = False
                    chosen_student = None
            current["rewards"] = rewards
            current["consensus"] = consensus
            current["chosen_student"] = chosen_student
            episodes.append(current)
            current = None
            i += 1
            continue

        i += 1

    return {episode["episode_id"]: episode for episode in episodes}


def build_first10_episode_metrics() -> list[dict[str, Any]]:
    labels = read_jsonl(FIRST_DIR / "base_policy_episode_labels.jsonl")
    raw = parse_first10_raw_log()
    rows = []
    for label in labels:
        episode_id = int(label["episode_id"])
        raw_episode = raw.get(episode_id, {})
        matrix = raw_episode.get("utilities_by_agent")
        if not matrix or not all(agent in matrix for agent in PROFESSORS):
            matrix = None
        metrics = compute_episode_metrics(matrix, bool(label["consensus"]), label.get("chosen_student"))
        rows.append({**label, **metrics, "source": "first10_base_policy_game_log"})
    return rows


def build_final10_episode_metrics() -> list[dict[str, Any]]:
    labels = {
        int(row["complete_episode_id"]): row
        for row in read_jsonl(FINAL_DIR / "episode_labels.jsonl")
    }
    segments = read_jsonl(FINAL_DIR / "complete_episode_segments.jsonl")
    rows = []
    for segment in segments:
        episode_id = int(segment["complete_episode_id"])
        label = labels[episode_id]
        matrix = utility_matrix_from_turns(segment.get("turns", []))
        metrics = compute_episode_metrics(matrix, bool(label["consensus"]), label.get("chosen_student"))
        rows.append({**label, **metrics, "source": "final10_train_steps_agent_model"})
    rows.sort(key=lambda row: row["complete_episode_id"])
    return rows


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[row["primary_category"]].append(row)

    summary = []
    for category, category_rows in sorted(buckets.items(), key=lambda item: (-len(item[1]), item[0])):
        computable = [row for row in category_rows if row["metric_computable"]]
        consensus_computable = [row for row in computable if row["consensus"] and row.get("chosen_student") is not None]
        socially_optimal = [row for row in computable if row["socially_optimal"]]
        summary.append(
            {
                "category": category,
                "episodes": len(category_rows),
                "metric_episodes": len(computable),
                "metric_coverage": len(computable) / len(category_rows) if category_rows else 0.0,
                "consensus_metric_episodes": len(consensus_computable),
                "socially_optimal_rate": len(socially_optimal) / len(computable) if computable else None,
                "socially_optimal_given_consensus_rate": (
                    len(socially_optimal) / len(consensus_computable)
                    if consensus_computable
                    else None
                ),
                "avg_social_welfare_efficiency": (
                    sum(row["social_welfare_efficiency"] for row in computable) / len(computable)
                    if computable
                    else None
                ),
                "avg_chosen_student_rank_global_consensus_only": (
                    sum(row["chosen_student_rank_global"] for row in consensus_computable) / len(consensus_computable)
                    if consensus_computable
                    else None
                ),
            }
        )
    return summary


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def write_summary(folder: Path, title: str, rows: list[dict[str, Any]]) -> None:
    per_episode_path = folder / "category_outcome_metrics_by_episode.jsonl"
    summary_json_path = folder / "category_outcome_metrics_summary.json"
    summary_csv_path = folder / "category_outcome_metrics_summary.csv"
    summary_md_path = folder / "category_outcome_metrics.md"

    metric_keys = {
        "source",
        "episode_id",
        "complete_episode_id",
        "segment_id",
        "primary_category",
        "consensus",
        "chosen_student",
        "metric_computable",
        "actual_total_utility",
        "optimal_total_utility",
        "optimal_student",
        "social_welfare_efficiency",
        "chosen_student_rank_global",
        "socially_optimal",
    }
    write_jsonl(per_episode_path, [{k: row.get(k) for k in sorted(metric_keys) if k in row} for row in rows])

    summary = summarize(rows)
    summary_json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    with summary_csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()) if summary else [])
        writer.writeheader()
        writer.writerows(summary)

    total = len(rows)
    computable = sum(1 for row in rows if row["metric_computable"])
    consensus_computable = sum(1 for row in rows if row["metric_computable"] and row["consensus"] and row.get("chosen_student") is not None)
    lines = [
        f"# {title}",
        "",
        "Metrics follow the env definitions: social optimum means `outcome/chosen_student_rank_global == 1`; `social_welfare/efficiency` is actual total utility divided by optimal total utility, with no-consensus episodes counted as 0 when the full utility matrix is visible.",
        "",
        f"- total labeled episodes: {total}",
        f"- metric-computable episodes: {computable} ({fmt(computable / total if total else 0.0)})",
        f"- metric-computable consensus episodes: {consensus_computable}",
        "",
        "| Category | Episodes | Metric episodes | Coverage | Socially optimum rate | Socially optimum given consensus | Avg efficiency | Avg global rank, consensus only |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            "| {category} | {episodes} | {metric_episodes} | {coverage} | {opt_rate} | {opt_consensus} | {efficiency} | {rank} |".format(
                category=row["category"],
                episodes=row["episodes"],
                metric_episodes=row["metric_episodes"],
                coverage=fmt(row["metric_coverage"]),
                opt_rate=fmt(row["socially_optimal_rate"]),
                opt_consensus=fmt(row["socially_optimal_given_consensus_rate"]),
                efficiency=fmt(row["avg_social_welfare_efficiency"]),
                rank=fmt(row["avg_chosen_student_rank_global_consensus_only"]),
            )
        )
    lines.extend(
        [
            "",
            "Coverage caveat: rows marked non-computable are usually short episodes where one professor never acted, so their full utility vector was not printed in the log. The env could compute those metrics from hidden state, but the log artifact cannot reconstruct them exactly.",
            "",
        ]
    )
    summary_md_path.write_text("\n".join(lines))


def write_comparison(first_rows: list[dict[str, Any]], final_rows: list[dict[str, Any]]) -> None:
    first_table = (FIRST_DIR / "category_outcome_metrics.md").read_text().split("| Category |", 1)[1]
    final_table = (FINAL_DIR / "category_outcome_metrics.md").read_text().split("| Category |", 1)[1]
    lines = [
        "# Category Outcome Metrics Comparison",
        "",
        "These tables are computed only on episodes with a visible full utility matrix.",
        "",
        "## First 10 Base-Policy Steps",
        "",
        "| Category |" + first_table,
        "## Final 10 Train Steps",
        "",
        "| Category |" + final_table,
    ]
    (ROOT / "analysis" / "category_outcome_metrics_comparison.md").write_text("\n".join(lines))


def main() -> None:
    first_rows = build_first10_episode_metrics()
    final_rows = build_final10_episode_metrics()
    write_summary(FIRST_DIR, "First 10 Base-Policy Category Outcome Metrics", first_rows)
    write_summary(FINAL_DIR, "Final 10 Train-Step Category Outcome Metrics", final_rows)
    write_comparison(first_rows, final_rows)
    print(f"first10: {sum(row['metric_computable'] for row in first_rows)}/{len(first_rows)} computable")
    print(f"final10: {sum(row['metric_computable'] for row in final_rows)}/{len(final_rows)} computable")


if __name__ == "__main__":
    main()
