#!/usr/bin/env python3
"""Validate final-10 trained-policy episode label files."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


OUT_DIR = Path("analysis/final10_train_steps_agent_model")

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
    "complete_episode_id",
    "segment_id",
    "env",
    "start_line",
    "end_line",
    "start_global_step",
    "end_global_step",
    "primary_category",
    "secondary_tags",
    "consensus",
    "chosen_student",
    "total_turns",
    "public_message_count",
    "vote_count",
    "wait_count",
    "wait_for_count",
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

    if record.get("primary_category") not in PRIMARY_CATEGORIES:
        errors.append(f"{label}: invalid primary_category: {record.get('primary_category')!r}")

    if record.get("confidence") not in CONFIDENCE:
        errors.append(f"{label}: invalid confidence: {record.get('confidence')!r}")

    if not isinstance(record.get("secondary_tags"), list):
        errors.append(f"{label}: secondary_tags must be a list")

    if not isinstance(record.get("complete_episode_id"), int):
        errors.append(f"{label}: complete_episode_id must be an integer")

    if record.get("suggested_new_category") and not record.get("why_existing_categories_fail"):
        errors.append(f"{label}: suggested_new_category requires why_existing_categories_fail")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", type=Path, default=sorted(OUT_DIR.glob("labels_ep*.jsonl")))
    parser.add_argument("--expected-count", type=int, default=716)
    args = parser.parse_args()

    all_records = []
    errors = []
    for path in args.files:
        records = load_jsonl(path)
        all_records.extend(records)
        for idx, record in enumerate(records, 1):
            errors.extend(validate_record(record, path, idx))

    ids = [row.get("complete_episode_id") for row in all_records]
    counts = Counter(ids)
    duplicates = sorted(eid for eid, count in counts.items() if count > 1)
    if duplicates:
        errors.append(f"duplicate complete_episode_id values: {duplicates}")

    valid_ids = [eid for eid in ids if isinstance(eid, int)]
    missing = sorted(set(range(1, args.expected_count + 1)) - set(valid_ids))
    if missing:
        errors.append(f"missing complete_episode_id values: {missing}")

    extra = sorted(eid for eid in valid_ids if eid < 1 or eid > args.expected_count)
    if extra:
        errors.append(f"out-of-range complete_episode_id values: {extra}")

    category_counts = Counter(row.get("primary_category") for row in all_records)
    confidence_counts = Counter(row.get("confidence") for row in all_records)

    print(f"files: {len(args.files)}")
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
