#!/usr/bin/env python3
"""Validate and summarize base-policy episode label JSONL files."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


PRIMARY_CATEGORIES = {
    "instant_consensus",
    "proposal_following",
    "coordination_theater",
    "thin_candidate_discussion",
    "negotiation_like",
    "stalled_waiting_loop",
    "execution_breakdown",
}

CONFIDENCE = {"high", "medium", "low"}

REQUIRED_FIELDS = {
    "episode_id",
    "line_start",
    "diagnosis_line",
    "primary_category",
    "secondary_tags",
    "consensus",
    "chosen_student",
    "total_turns",
    "public_message_count",
    "vote_count",
    "wait_count",
    "wait_for_count",
    "format_error_rate",
    "invalid_error_count",
    "confidence",
    "rationale",
    "notable_excerpt",
    "suggested_new_category",
    "why_existing_categories_fail",
}


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open() as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{lineno}: invalid JSON: {exc}") from exc
    return records


def validate_record(record: dict, source: Path, index: int) -> list[str]:
    label = f"{source}:{index}"
    errors = []

    missing = REQUIRED_FIELDS - set(record)
    if missing:
        errors.append(f"{label}: missing fields: {sorted(missing)}")

    category = record.get("primary_category")
    if category not in PRIMARY_CATEGORIES:
        errors.append(f"{label}: invalid primary_category: {category!r}")

    confidence = record.get("confidence")
    if confidence not in CONFIDENCE:
        errors.append(f"{label}: invalid confidence: {confidence!r}")

    tags = record.get("secondary_tags")
    if not isinstance(tags, list):
        errors.append(f"{label}: secondary_tags must be a list")

    episode_id = record.get("episode_id")
    if not isinstance(episode_id, int):
        errors.append(f"{label}: episode_id must be an integer")

    suggested = record.get("suggested_new_category")
    why = record.get("why_existing_categories_fail")
    if suggested and not why:
        errors.append(f"{label}: suggested_new_category requires why_existing_categories_fail")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "files",
        nargs="*",
        type=Path,
        default=sorted(Path("analysis/first10_base_policy_game_log").glob("base_policy_labels_ep*.jsonl")),
    )
    parser.add_argument("--expected-count", type=int, default=232)
    args = parser.parse_args()

    records_by_file = []
    errors = []

    for path in args.files:
        records = load_jsonl(path)
        records_by_file.append((path, records))
        for index, record in enumerate(records, 1):
            errors.extend(validate_record(record, path, index))

    all_records = [record for _, records in records_by_file for record in records]
    episode_ids = [record.get("episode_id") for record in all_records]
    id_counts = Counter(episode_ids)
    duplicates = sorted(eid for eid, count in id_counts.items() if count > 1)
    if duplicates:
        errors.append(f"duplicate episode_id values: {duplicates}")

    valid_ids = [eid for eid in episode_ids if isinstance(eid, int)]
    missing_ids = sorted(set(range(1, args.expected_count + 1)) - set(valid_ids))
    if missing_ids:
        errors.append(f"missing episode_id values: {missing_ids}")

    extra_ids = sorted(eid for eid in valid_ids if eid < 1 or eid > args.expected_count)
    if extra_ids:
        errors.append(f"out-of-range episode_id values: {extra_ids}")

    category_counts = Counter(record.get("primary_category") for record in all_records)
    confidence_counts = Counter(record.get("confidence") for record in all_records)

    print(f"files: {len(records_by_file)}")
    print(f"records: {len(all_records)}")
    print("category_counts:")
    for category, count in category_counts.most_common():
        print(f"  {category}: {count}")
    print("confidence_counts:")
    for confidence, count in confidence_counts.most_common():
        print(f"  {confidence}: {count}")

    if errors:
        print("errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("validation: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
