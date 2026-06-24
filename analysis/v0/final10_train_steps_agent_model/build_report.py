#!/usr/bin/env python3
"""Build final-10 trained-policy categorization report."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


OUT_DIR = Path("analysis/final10_train_steps_agent_model")
LABEL_FILES = [
    OUT_DIR / "labels_ep001_179.jsonl",
    OUT_DIR / "labels_ep180_358.jsonl",
    OUT_DIR / "labels_ep359_537.jsonl",
    OUT_DIR / "labels_ep538_716.jsonl",
]

MERGED_JSONL = OUT_DIR / "episode_labels.jsonl"
SUMMARY_MD = OUT_DIR / "episode_summary.md"
CATEGORY_SVG = OUT_DIR / "category_counts.svg"
OUTCOME_SVG = OUT_DIR / "category_by_outcome.svg"
COMPARISON_MD = OUT_DIR / "base_vs_final10_comparison.md"

CATEGORY_ORDER = [
    "negotiation_like",
    "proposal_following",
    "thin_candidate_discussion",
    "instant_consensus",
    "coordination_theater",
    "stalled_waiting_loop",
    "execution_breakdown",
]

BASE_COUNTS = {
    "negotiation_like": 65,
    "proposal_following": 54,
    "thin_candidate_discussion": 50,
    "instant_consensus": 30,
    "coordination_theater": 18,
    "stalled_waiting_loop": 14,
    "execution_breakdown": 1,
}
BASE_TOTAL = 232


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_records() -> list[dict]:
    records = []
    for path in LABEL_FILES:
        records.extend(load_jsonl(path))
    return sorted(records, key=lambda row: row["complete_episode_id"])


def pct(count: int, total: int) -> str:
    return f"{100 * count / total:.1f}%"


def esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_merged(records: list[dict]) -> None:
    with MERGED_JSONL.open("w") as f:
        for record in records:
            f.write(json.dumps(record, sort_keys=True) + "\n")


def make_bar_svg(path: Path, title: str, counts: Counter) -> None:
    cats = [cat for cat in CATEGORY_ORDER if counts[cat]]
    vals = [counts[cat] for cat in cats]
    width, height = 980, 520
    ml, mt, pw, ph = 80, 55, 850, 330
    gap = 22
    bw = (pw - gap * (len(cats) - 1)) / max(1, len(cats))
    maxv = max(vals) if vals else 1
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="490" y="30" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700">{esc(title)}</text>',
        f'<line x1="{ml}" y1="{mt + ph}" x2="{ml + pw}" y2="{mt + ph}" stroke="#333"/>',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt + ph}" stroke="#333"/>',
    ]
    for i, cat in enumerate(cats):
        x = ml + i * (bw + gap)
        h = vals[i] / maxv * ph
        y = mt + ph - h
        svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="#4c78a8"/>')
        svg.append(f'<text x="{x + bw / 2:.1f}" y="{y - 7:.1f}" text-anchor="middle" font-family="Arial" font-size="13">{vals[i]}</text>')
        svg.append(f'<text x="{x + bw / 2:.1f}" y="{mt + ph + 24}" text-anchor="end" transform="rotate(-30 {x + bw / 2:.1f} {mt + ph + 24})" font-family="Arial" font-size="12">{esc(cat)}</text>')
    svg.append('<text x="25" y="220" text-anchor="middle" transform="rotate(-90 25 220)" font-family="Arial" font-size="14">Episode count</text>')
    svg.append("</svg>")
    path.write_text("\n".join(svg))


def make_outcome_svg(records: list[dict]) -> None:
    counts = Counter(row["primary_category"] for row in records)
    cats = [cat for cat in CATEGORY_ORDER if counts[cat]]
    yes = Counter(row["primary_category"] for row in records if row["consensus"])
    no = Counter(row["primary_category"] for row in records if not row["consensus"])
    width, height = 980, 520
    ml, mt, pw, ph = 80, 55, 850, 330
    gap = 22
    bw = (pw - gap * (len(cats) - 1)) / max(1, len(cats))
    maxv = max(counts[cat] for cat in cats) if cats else 1
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="490" y="30" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700">Consensus outcome by category</text>',
        f'<line x1="{ml}" y1="{mt + ph}" x2="{ml + pw}" y2="{mt + ph}" stroke="#333"/>',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{mt + ph}" stroke="#333"/>',
        '<rect x="735" y="50" width="14" height="14" fill="#59a14f"/><text x="756" y="62" font-family="Arial" font-size="13">Consensus yes</text>',
        '<rect x="735" y="72" width="14" height="14" fill="#e15759"/><text x="756" y="84" font-family="Arial" font-size="13">Consensus no</text>',
    ]
    for i, cat in enumerate(cats):
        x = ml + i * (bw + gap)
        yh = yes[cat] / maxv * ph
        nh = no[cat] / maxv * ph
        yy = mt + ph - yh
        ny = yy - nh
        if yh:
            svg.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{bw:.1f}" height="{yh:.1f}" fill="#59a14f"/>')
        if nh:
            svg.append(f'<rect x="{x:.1f}" y="{ny:.1f}" width="{bw:.1f}" height="{nh:.1f}" fill="#e15759"/>')
        svg.append(f'<text x="{x + bw / 2:.1f}" y="{ny - 7:.1f}" text-anchor="middle" font-family="Arial" font-size="13">{counts[cat]}</text>')
        svg.append(f'<text x="{x + bw / 2:.1f}" y="{mt + ph + 24}" text-anchor="end" transform="rotate(-30 {x + bw / 2:.1f} {mt + ph + 24})" font-family="Arial" font-size="12">{esc(cat)}</text>')
    svg.append('<text x="25" y="220" text-anchor="middle" transform="rotate(-90 25 220)" font-family="Arial" font-size="14">Episode count</text>')
    svg.append("</svg>")
    OUTCOME_SVG.write_text("\n".join(svg))


def make_summary(records: list[dict]) -> None:
    total = len(records)
    counts = Counter(row["primary_category"] for row in records)
    confidence = Counter(row["confidence"] for row in records)
    tags = Counter(tag for row in records for tag in row["secondary_tags"])
    by_cat = defaultdict(list)
    for row in records:
        by_cat[row["primary_category"]].append(row)

    lines = [
        "# Final 10 Training Steps Behavior Analysis",
        "",
        "## Scope",
        "",
        "- Source: `logs/agent_model_train_auton_12993.log`",
        "- Training steps: `global_steps=66..75`",
        "- Episodes labeled: `716` complete bounded episodes",
        "- Boundary fragments are excluded from category percentages.",
        "",
        "## Category Summary",
        "",
        "| Primary category | Count | Percent | Consensus yes | Consensus rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for cat in CATEGORY_ORDER:
        rows = by_cat.get(cat, [])
        if not rows:
            continue
        yes = sum(1 for row in rows if row["consensus"])
        lines.append(f"| `{cat}` | {len(rows)} | {pct(len(rows), total)} | {yes} | {pct(yes, len(rows))} |")

    lines.extend([
        "",
        "## Main Readout",
        "",
        f"`negotiation_like` appears in {counts['negotiation_like']}/{total} episodes ({pct(counts['negotiation_like'], total)}).",
        f"`instant_consensus` and `proposal_following` together account for {counts['instant_consensus'] + counts['proposal_following']}/{total} episodes ({pct(counts['instant_consensus'] + counts['proposal_following'], total)}).",
        f"`vote_only` appears in {tags['vote_only']} episodes and `no_public_messages` appears in {tags['no_public_messages']} episodes.",
        "",
        "## Confidence",
        "",
        "| Confidence | Count | Percent |",
        "|---|---:|---:|",
    ])
    for conf in ["high", "medium", "low"]:
        lines.append(f"| `{conf}` | {confidence[conf]} | {pct(confidence[conf], total)} |")

    lines.extend(["", "## Representative Episodes", ""])
    for cat in CATEGORY_ORDER:
        rows = by_cat.get(cat, [])
        if not rows:
            continue
        lines.append(f"### `{cat}`")
        lines.append("")
        for row in rows[:3]:
            chosen = "none" if row["chosen_student"] is None else row["chosen_student"]
            lines.append(
                f"- Episode {row['complete_episode_id']} segment {row['segment_id']}: "
                f"consensus={row['consensus']}, chosen={chosen}, confidence={row['confidence']}. {row['rationale']}"
            )
            if row.get("notable_excerpt"):
                lines.append(f"  Excerpt: \"{row['notable_excerpt']}\"")
        lines.append("")

    lines.extend(["## Full Episode Appendix", ""])
    for row in records:
        chosen = "none" if row["chosen_student"] is None else row["chosen_student"]
        tag_str = ", ".join(f"`{tag}`" for tag in row["secondary_tags"])
        lines.append(f"### Complete Episode {row['complete_episode_id']}")
        lines.append("")
        lines.append(f"- Segment/env: `{row['segment_id']}` / `{row['env']}`")
        lines.append(f"- Lines: `{row['start_line']}-{row['end_line']}`")
        lines.append(f"- Steps: `{row['start_global_step']}-{row['end_global_step']}`")
        lines.append(f"- Category: `{row['primary_category']}`")
        lines.append(f"- Tags: {tag_str}")
        lines.append(f"- Consensus: `{row['consensus']}`")
        lines.append(f"- Chosen student: `{chosen}`")
        lines.append(f"- Turns/messages/votes: `{row['total_turns']}` / `{row['public_message_count']}` / `{row['vote_count']}`")
        lines.append(f"- Waits/wait_for: `{row['wait_count']}` / `{row['wait_for_count']}`")
        lines.append(f"- Confidence: `{row['confidence']}`")
        lines.append(f"- Rationale: {row['rationale']}")
        if row.get("notable_excerpt"):
            lines.append(f"- Excerpt: \"{row['notable_excerpt']}\"")
        lines.append("")

    SUMMARY_MD.write_text("\n".join(lines))


def make_comparison(records: list[dict]) -> None:
    final_total = len(records)
    final_counts = Counter(row["primary_category"] for row in records)
    lines = [
        "# Base Policy vs Final 10 Training Steps",
        "",
        "| Category | Base count | Base percent | Final10 count | Final10 percent | Change pp |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for cat in CATEGORY_ORDER:
        base_pct = 100 * BASE_COUNTS.get(cat, 0) / BASE_TOTAL
        final_pct = 100 * final_counts.get(cat, 0) / final_total
        lines.append(
            f"| `{cat}` | {BASE_COUNTS.get(cat, 0)} | {base_pct:.1f}% | "
            f"{final_counts.get(cat, 0)} | {final_pct:.1f}% | {final_pct - base_pct:+.1f} |"
        )
    lines.append("")
    lines.append(
        "Note: base-policy labels came from `analysis/first10_base_policy_game_log/`, using compact env=0 "
        "diagnosis episodes before line 144892; final10 labels come from all-env complete bounded episodes "
        "reconstructed from the agent-model log. "
        "The comparison is behaviorally useful but the sampling/logging sources differ."
    )
    COMPARISON_MD.write_text("\n".join(lines))


def main() -> int:
    records = load_records()
    write_merged(records)
    counts = Counter(row["primary_category"] for row in records)
    make_bar_svg(CATEGORY_SVG, "Final-10 trained-policy episode categories", counts)
    make_outcome_svg(records)
    make_summary(records)
    make_comparison(records)
    print(f"wrote {MERGED_JSONL}")
    print(f"wrote {SUMMARY_MD}")
    print(f"wrote {CATEGORY_SVG}")
    print(f"wrote {OUTCOME_SVG}")
    print(f"wrote {COMPARISON_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
