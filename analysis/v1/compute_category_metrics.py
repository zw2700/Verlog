#!/usr/bin/env python3
"""Categorize episode_log JSONL rows and compute category-level metrics."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_VALID_STUDENTS = set(range(5))
STUDENT_RE = re.compile(r"\b[Ss]tudents?\s*(\d+)\b")


def natural_sort_key(path: Path) -> list[Any]:
    return [
        int(part) if part.isdigit() else part
        for part in re.split(r"(\d+)", str(path))
    ]


def episode_log_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        files = sorted(path.glob("*.worker*.jsonl"), key=natural_sort_key)
        if files:
            return files
        files = sorted(path.glob("**/*.worker*.jsonl"), key=natural_sort_key)
        if files:
            return files
        files = sorted(path.glob("*.jsonl"), key=natural_sort_key)
        if files:
            return files
        files = sorted(path.glob("**/*.jsonl"), key=natural_sort_key)
        if files:
            return files
        raise FileNotFoundError(f"No JSONL shards found under directory: {path}")
    raise FileNotFoundError(f"Episode log path does not exist: {path}")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for shard_path in episode_log_files(path):
        with shard_path.open() as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                row["_source_path"] = str(shard_path)
                row["_source_line"] = line_no
                rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def as_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        converted = int(value)
    except (TypeError, ValueError):
        return None
    return converted


def actions(turn: dict[str, Any]) -> dict[str, Any]:
    raw = turn.get("actions")
    return raw if isinstance(raw, dict) else {}


def group_messages(turn: dict[str, Any]) -> list[str]:
    raw = actions(turn).get("group_messages", [])
    return [str(message) for message in raw] if isinstance(raw, list) else []


def valid_students_for_episode(ep: dict[str, Any]) -> set[int]:
    student_batch = ep.get("student_batch")
    if not isinstance(student_batch, list) or not student_batch:
        return DEFAULT_VALID_STUDENTS

    valid = set()
    for fallback_idx, student in enumerate(student_batch):
        if isinstance(student, dict):
            idx = as_int(student.get("index"))
            valid.add(idx if idx is not None else fallback_idx)
        else:
            valid.add(fallback_idx)
    return valid


def votes(turn: dict[str, Any], valid_students: set[int]) -> list[int]:
    raw = actions(turn).get("votes", [])
    if not isinstance(raw, list):
        return []
    parsed = []
    for value in raw:
        vote = as_int(value)
        if vote is not None and vote in valid_students:
            parsed.append(vote)
    return parsed


def raw_votes(turn: dict[str, Any]) -> list[Any]:
    raw = actions(turn).get("votes", [])
    return raw if isinstance(raw, list) else []


def wait_count(turn: dict[str, Any]) -> int:
    return as_int(actions(turn).get("wait_count", 0)) or 0


def wait_for(turn: dict[str, Any]) -> list[str]:
    raw = actions(turn).get("wait_for", [])
    return [str(agent) for agent in raw] if isinstance(raw, list) else []


def candidates_in_text(text: str, valid_students: set[int]) -> set[int]:
    return {
        int(match)
        for match in STUDENT_RE.findall(text)
        if int(match) in valid_students
    }


def candidates_in_turn(turn: dict[str, Any], valid_students: set[int]) -> set[int]:
    candidates = set(votes(turn, valid_students))
    for message in group_messages(turn):
        candidates.update(candidates_in_text(message, valid_students))
    return candidates


def normalized_action(turn: dict[str, Any], valid_students: set[int]) -> tuple[Any, ...]:
    return (
        turn.get("agent"),
        tuple(message.strip().lower() for message in group_messages(turn)),
        tuple(votes(turn, valid_students)),
        tuple(wait_for(turn)),
        wait_count(turn),
    )


def is_malformed(ep: dict[str, Any]) -> str | None:
    valid_students = valid_students_for_episode(ep)
    tokens_used = ep.get("tokens_used")
    if isinstance(tokens_used, bool) or not isinstance(tokens_used, (int, float)):
        return "missing_or_invalid_tokens_used"

    turns = ep.get("turns")
    if not isinstance(turns, list):
        return "missing_or_invalid_turns"

    chosen = as_int(ep.get("chosen_student"))
    if ep.get("consensus") is True and chosen not in valid_students:
        return "consensus_without_valid_chosen_student"

    for turn in turns:
        if not isinstance(turn, dict):
            return "invalid_turn"
        raw_actions = turn.get("actions")
        if not isinstance(raw_actions, dict):
            return "missing_or_invalid_actions"
        for raw_vote in raw_votes(turn):
            vote = as_int(raw_vote)
            if vote not in valid_students:
                return "invalid_vote"

    return None


def episode_features(ep: dict[str, Any]) -> dict[str, Any]:
    turns = ep.get("turns", [])
    valid_students = valid_students_for_episode(ep)
    total_turns = len(turns)
    wait_like_turns = 0
    action_turns = 0
    public_speakers = set()
    acting_agents = set()
    candidates = set()
    vote_count = 0
    group_message_count = 0

    for turn in turns:
        turn_groups = group_messages(turn)
        turn_votes = votes(turn, valid_students)
        turn_wait_for = wait_for(turn)
        turn_wait_count = wait_count(turn)

        if (turn_wait_count or turn_wait_for) and not turn_groups and not turn_votes:
            wait_like_turns += 1
        if turn_groups or turn_votes:
            action_turns += 1
            acting_agents.add(turn.get("agent"))
        if turn_groups:
            public_speakers.add(turn.get("agent"))

        candidates.update(candidates_in_turn(turn, valid_students))
        vote_count += len(turn_votes)
        group_message_count += len(turn_groups)

    repeated_actions = Counter(normalized_action(turn, valid_students) for turn in turns)
    max_exact_repeated_action = repeated_actions.most_common(1)[0][1] if turns else 0

    last_turns = turns[-5:]
    last_action_speakers = {
        turn.get("agent")
        for turn in last_turns
        if group_messages(turn) or votes(turn, valid_students)
    }
    last_vote_count = sum(len(votes(turn, valid_students)) for turn in last_turns)
    recovered_into_consensus = bool(
        ep.get("consensus") is True
        and len(last_action_speakers) >= 2
        and last_vote_count >= 2
    )

    return {
        "total_turns": total_turns,
        "wait_like_turns": wait_like_turns,
        "wait_like_ratio": wait_like_turns / total_turns if total_turns else 0.0,
        "action_turns": action_turns,
        "public_speaker_count": len(public_speakers),
        "acting_agent_count": len(acting_agents),
        "candidate_count": len(candidates),
        "candidates": sorted(candidates),
        "vote_count": vote_count,
        "group_message_count": group_message_count,
        "max_exact_repeated_action": max_exact_repeated_action,
        "recovered_into_consensus": recovered_into_consensus,
    }


def stalled_reason(ep: dict[str, Any], features: dict[str, Any]) -> str | None:
    total_turns = features["total_turns"]
    consensus = bool(ep.get("consensus"))
    candidate_count = features["candidate_count"]

    if not consensus and candidate_count == 0:
        return "no_candidate_no_consensus"

    if total_turns <= 6:
        return None

    if features["max_exact_repeated_action"] >= 10:
        return "repeated_dominant_action"

    if features["recovered_into_consensus"]:
        return None

    if (
        features["wait_like_ratio"] >= 0.65
        and (not consensus or features["action_turns"] <= 3 or candidate_count <= 1)
    ):
        return "wait_like_loop"

    if total_turns >= 8 and features["action_turns"] <= 2:
        return "too_few_actions"

    if total_turns >= 10 and features["public_speaker_count"] <= 1:
        return "one_public_speaker"

    if not consensus and total_turns >= 10 and candidate_count <= 1:
        return "no_consensus_low_candidate_count"

    return None


def instant_decision_reason(ep: dict[str, Any], features: dict[str, Any]) -> str | None:
    tokens_used = ep.get("tokens_used")
    total_turns = features["total_turns"]
    if tokens_used <= 40:
        return "tokens_used_le_40"
    if total_turns <= 2:
        return "total_turns_le_2"
    if total_turns <= 3 and ep.get("consensus") is True and features["candidate_count"] <= 1:
        return "three_turn_single_candidate_consensus"
    return None


def categorize_episode(ep: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    malformed_reason = is_malformed(ep)
    if malformed_reason:
        return "malformed_or_other", malformed_reason, {}

    features = episode_features(ep)

    reason = stalled_reason(ep, features)
    if reason:
        return "stalled_coordination_failure", reason, features

    reason = instant_decision_reason(ep, features)
    if reason:
        return "instant_decision", reason, features

    return "negotiation", "default_non_stalled_non_instant", features


def in_step_range(ep: dict[str, Any], step_start: int | None, step_end: int | None) -> bool:
    step = as_int(ep.get("global_step"))
    if step is None:
        return False
    if step_start is not None and step < step_start:
        return False
    if step_end is not None and step > step_end:
        return False
    return True


def build_episode_rows(episodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for ep in episodes:
        category, reason, features = categorize_episode(ep)
        row = {
            "source_path": ep.get("_source_path"),
            "source_line": ep.get("_source_line"),
            "episode_uid": ep.get("episode_uid"),
            "global_step": ep.get("global_step"),
            "epoch": ep.get("epoch"),
            "env": ep.get("env"),
            "episode_index": ep.get("episode_index"),
            "category": category,
            "category_reason": reason,
            "consensus": bool(ep.get("consensus")),
            "chosen_student": ep.get("chosen_student"),
            "socially_optimal": ep.get("socially_optimal"),
            "social_welfare_efficiency": ep.get("social_welfare_efficiency"),
            "chosen_student_rank_global": ep.get("chosen_student_rank_global"),
            "tokens_used": ep.get("tokens_used"),
            "token_budget": ep.get("token_budget"),
            "total_turns": features.get("total_turns", len(ep.get("turns", []))),
            "optimal_student": ep.get("optimal_student"),
            "actual_total_utility": ep.get("actual_total_utility"),
            "optimal_total_utility": ep.get("optimal_total_utility"),
        }
        row.update(
            {
                "candidate_count": features.get("candidate_count"),
                "candidates": features.get("candidates"),
                "public_speaker_count": features.get("public_speaker_count"),
                "acting_agent_count": features.get("acting_agent_count"),
                "action_turns": features.get("action_turns"),
                "wait_like_turns": features.get("wait_like_turns"),
                "wait_like_ratio": features.get("wait_like_ratio"),
                "vote_count": features.get("vote_count"),
                "group_message_count": features.get("group_message_count"),
                "max_exact_repeated_action": features.get("max_exact_repeated_action"),
            }
        )
        rows.append(row)
    return rows


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[row["category"]].append(row)

    total = len(rows)
    summary = []
    for category, category_rows in sorted(buckets.items(), key=lambda item: (-len(item[1]), item[0])):
        consensus_rows = [row for row in category_rows if row["consensus"]]
        social_rows = [
            row for row in category_rows
            if isinstance(row.get("socially_optimal"), bool)
        ]
        so_rows = [row for row in social_rows if row["socially_optimal"]]
        consensus_social_rows = [
            row for row in consensus_rows
            if isinstance(row.get("socially_optimal"), bool)
        ]
        consensus_so_rows = [row for row in consensus_social_rows if row["socially_optimal"]]
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
        summary.append(
            {
                "category": category,
                "episodes": len(category_rows),
                "percent": len(category_rows) / total if total else None,
                "consensus_rate": len(consensus_rows) / len(category_rows) if category_rows else None,
                "socially_optimal_rate": len(so_rows) / len(social_rows) if social_rows else None,
                "socially_optimal_given_consensus_rate": (
                    len(consensus_so_rows) / len(consensus_social_rows)
                    if consensus_social_rows
                    else None
                ),
                "avg_social_welfare_efficiency": mean(efficiencies),
                "avg_chosen_student_rank_global_consensus_only": mean(ranks),
                "avg_tokens_used": mean(tokens),
                "avg_total_turns": mean(turns),
            }
        )
    return summary


def overall_metrics(rows: list[dict[str, Any]]) -> dict[str, float | None]:
    consensus_rows = [row for row in rows if row["consensus"]]
    social_rows = [
        row for row in rows
        if isinstance(row.get("socially_optimal"), bool)
    ]
    so_rows = [row for row in social_rows if row["socially_optimal"]]
    consensus_social_rows = [
        row for row in consensus_rows
        if isinstance(row.get("socially_optimal"), bool)
    ]
    consensus_so_rows = [row for row in consensus_social_rows if row["socially_optimal"]]

    return {
        "consensus_rate": len(consensus_rows) / len(rows) if rows else None,
        "socially_optimal_rate": len(so_rows) / len(social_rows) if social_rows else None,
        "socially_optimal_given_consensus_rate": (
            len(consensus_so_rows) / len(consensus_social_rows)
            if consensus_social_rows
            else None
        ),
    }


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def markdown_table(headers: list[str], rows: list[list[Any]], right_align: set[int] | None = None) -> list[str]:
    right_align = right_align or set()
    string_rows = [[str(cell) for cell in row] for row in rows]
    widths = [
        max(len(headers[idx]), *(len(row[idx]) for row in string_rows))
        if string_rows
        else len(headers[idx])
        for idx in range(len(headers))
    ]

    def format_row(row: list[str]) -> str:
        cells = []
        for idx, cell in enumerate(row):
            padded = cell.rjust(widths[idx]) if idx in right_align else cell.ljust(widths[idx])
            cells.append(f" {padded} ")
        return "|" + "|".join(cells) + "|"

    separator_cells = []
    for idx, width in enumerate(widths):
        if idx in right_align:
            separator_cells.append("-" * max(width, 3) + ":")
        else:
            separator_cells.append("-" * max(width, 3))

    return [
        format_row(headers),
        "|" + "|".join(f" {cell} " for cell in separator_cells) + "|",
        *(format_row(row) for row in string_rows),
    ]


def write_outputs(out_dir: Path, episode_rows: list[dict[str, Any]], summary: list[dict[str, Any]], args: argparse.Namespace) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(out_dir / "episode_category_labels.jsonl", episode_rows)

    with (out_dir / "category_metrics_summary.json").open("w") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")

    fieldnames = list(summary[0].keys()) if summary else [
        "category",
        "episodes",
        "percent",
        "consensus_rate",
        "socially_optimal_rate",
        "socially_optimal_given_consensus_rate",
        "avg_social_welfare_efficiency",
        "avg_chosen_student_rank_global_consensus_only",
        "avg_tokens_used",
        "avg_total_turns",
    ]
    with (out_dir / "category_metrics_summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary)

    overall = overall_metrics(episode_rows)
    source_files = episode_log_files(args.episode_log)
    lines = [
        "# Category Metrics Summary",
        "",
        f"- episode_log: `{args.episode_log}`",
        f"- episode_log files read: `{len(source_files)}`",
        f"- global_step range: `{args.step_start}` to `{args.step_end}`",
        f"- episodes analyzed: `{len(episode_rows)}`",
        f"- overall consensus rate: `{fmt(overall['consensus_rate'])}`",
        f"- overall SO rate: `{fmt(overall['socially_optimal_rate'])}`",
        f"- overall SO given consensus rate: `{fmt(overall['socially_optimal_given_consensus_rate'])}`",
        "",
    ]
    headers = ["Category", "Episodes", "%", "Consensus", "SO", "SO given cons", "Avg eff", "Avg rank", "Avg tokens", "Avg turns"]
    rows = [
        [
            row["category"],
            row["episodes"],
            fmt(row["percent"]),
            fmt(row["consensus_rate"]),
            fmt(row["socially_optimal_rate"]),
            fmt(row["socially_optimal_given_consensus_rate"]),
            fmt(row["avg_social_welfare_efficiency"]),
            fmt(row["avg_chosen_student_rank_global_consensus_only"]),
            fmt(row["avg_tokens_used"], 1),
            fmt(row["avg_total_turns"], 1),
        ]
        for row in summary
    ]
    lines.extend(markdown_table(headers, rows, right_align=set(range(1, len(headers)))))
    lines.append("")
    (out_dir / "category_metrics_summary.md").write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode-log", required=True, type=Path, help="Path to episode_log_*.jsonl or a sharded episode-log directory")
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
    summary = summarize(episode_rows)
    write_outputs(args.out_dir, episode_rows, summary, args)


if __name__ == "__main__":
    main()
