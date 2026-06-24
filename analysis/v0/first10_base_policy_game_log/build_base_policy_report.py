#!/usr/bin/env python3
"""Build merged artifacts for base-policy episode categorization."""

from __future__ import annotations

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path


OUT_DIR = Path("analysis/first10_base_policy_game_log")

LABEL_FILES = [
    OUT_DIR / "base_policy_labels_ep001_058.jsonl",
    OUT_DIR / "base_policy_labels_ep059_116.jsonl",
    OUT_DIR / "base_policy_labels_ep117_174.jsonl",
    OUT_DIR / "base_policy_labels_ep175_232.jsonl",
]

MERGED_JSONL = OUT_DIR / "base_policy_episode_labels.jsonl"
SUMMARY_MD = OUT_DIR / "base_policy_episode_summary.md"
CATEGORY_SVG = OUT_DIR / "base_policy_category_counts.svg"
OUTCOME_SVG = OUT_DIR / "base_policy_category_by_outcome.svg"
METRICS_CSV = OUT_DIR / "category_outcome_metrics_summary.csv"

CATEGORY_ORDER = [
    "negotiation_like",
    "proposal_following",
    "thin_candidate_discussion",
    "instant_consensus",
    "coordination_theater",
    "stalled_waiting_loop",
    "execution_breakdown",
]


def load_records() -> list[dict]:
    records = []
    for path in LABEL_FILES:
        with path.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return sorted(records, key=lambda row: row["episode_id"])


def pct(count: int, total: int) -> str:
    return f"{100 * count / total:.1f}%"


def write_merged(records: list[dict]) -> None:
    with MERGED_JSONL.open("w") as f:
        for record in records:
            f.write(json.dumps(record, sort_keys=True) + "\n")


def make_plots(records: list[dict]) -> None:
    counts = Counter(row["primary_category"] for row in records)
    categories = [cat for cat in CATEGORY_ORDER if counts[cat]]
    values = [counts[cat] for cat in categories]

    def label(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def fmt_metric(value: str) -> str:
        if value == "" or value is None:
            return "NA"
        return f"{float(value):.3f}"

    def load_metrics() -> dict[str, dict[str, str]]:
        if not METRICS_CSV.exists():
            return {}
        with METRICS_CSV.open(newline="") as f:
            return {row["category"]: row for row in csv.DictReader(f)}

    yes_by_cat = Counter()
    no_by_cat = Counter()
    for row in records:
        if row["consensus"]:
            yes_by_cat[row["primary_category"]] += 1
        else:
            no_by_cat[row["primary_category"]] += 1

    yes_values = [yes_by_cat[cat] for cat in categories]
    no_values = [no_by_cat[cat] for cat in categories]

    width = 980
    height = 520
    margin_left = 80
    margin_top = 55
    plot_width = 850
    plot_height = 330
    bar_gap = 22
    bar_width = (plot_width - bar_gap * (len(categories) - 1)) / len(categories)
    max_value = max(values) if values else 1

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="490" y="30" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700">Base-policy episode categories</text>',
        f'<line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}" stroke="#333"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}" stroke="#333"/>',
    ]
    for i, category in enumerate(categories):
        x = margin_left + i * (bar_width + bar_gap)
        h = values[i] / max_value * plot_height
        y = margin_top + plot_height - h
        svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{h:.1f}" fill="#4c78a8"/>')
        svg.append(f'<text x="{x + bar_width / 2:.1f}" y="{y - 7:.1f}" text-anchor="middle" font-family="Arial" font-size="13">{values[i]}</text>')
        svg.append(f'<text x="{x + bar_width / 2:.1f}" y="{margin_top + plot_height + 24}" text-anchor="end" transform="rotate(-30 {x + bar_width / 2:.1f} {margin_top + plot_height + 24})" font-family="Arial" font-size="12">{label(category)}</text>')
    svg.append('<text x="25" y="220" text-anchor="middle" transform="rotate(-90 25 220)" font-family="Arial" font-size="14">Episode count</text>')
    svg.append("</svg>")
    CATEGORY_SVG.write_text("\n".join(svg))

    outcome_height = 720
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{outcome_height}" viewBox="0 0 {width} {outcome_height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="490" y="30" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700">Consensus outcome by category</text>',
        f'<line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}" stroke="#333"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}" stroke="#333"/>',
        '<rect x="735" y="50" width="14" height="14" fill="#59a14f"/><text x="756" y="62" font-family="Arial" font-size="13">Consensus yes</text>',
        '<rect x="735" y="72" width="14" height="14" fill="#e15759"/><text x="756" y="84" font-family="Arial" font-size="13">Consensus no</text>',
    ]
    max_total = max(y + n for y, n in zip(yes_values, no_values)) if categories else 1
    for i, category in enumerate(categories):
        x = margin_left + i * (bar_width + bar_gap)
        yes_h = yes_values[i] / max_total * plot_height
        no_h = no_values[i] / max_total * plot_height
        yes_y = margin_top + plot_height - yes_h
        no_y = yes_y - no_h
        if yes_h:
            svg.append(f'<rect x="{x:.1f}" y="{yes_y:.1f}" width="{bar_width:.1f}" height="{yes_h:.1f}" fill="#59a14f"/>')
        if no_h:
            svg.append(f'<rect x="{x:.1f}" y="{no_y:.1f}" width="{bar_width:.1f}" height="{no_h:.1f}" fill="#e15759"/>')
        total_value = yes_values[i] + no_values[i]
        svg.append(f'<text x="{x + bar_width / 2:.1f}" y="{no_y - 7:.1f}" text-anchor="middle" font-family="Arial" font-size="13">{total_value}</text>')
        svg.append(f'<text x="{x + bar_width / 2:.1f}" y="{margin_top + plot_height + 24}" text-anchor="end" transform="rotate(-30 {x + bar_width / 2:.1f} {margin_top + plot_height + 24})" font-family="Arial" font-size="12">{label(category)}</text>')
    svg.append('<text x="25" y="220" text-anchor="middle" transform="rotate(-90 25 220)" font-family="Arial" font-size="14">Episode count</text>')

    metrics = load_metrics()
    if metrics:
        table_x = 80
        table_y = 520
        row_h = 22
        columns = [
            ("Category", 0, "start"),
            ("Cov", 245, "end"),
            ("SO rate", 345, "end"),
            ("SO|cons", 455, "end"),
            ("Avg eff", 565, "end"),
            ("Avg rank", 675, "end"),
        ]
        svg.append(f'<text x="{table_x}" y="{table_y - 24}" font-family="Arial" font-size="13" font-weight="700">Outcome metrics by category</text>')
        svg.append(f'<text x="{table_x}" y="{table_y - 7}" font-family="Arial" font-size="11" fill="#555">SO = socially optimal; SO|cons = socially optimal given consensus; rank averages consensus episodes only.</text>')
        for header, offset, anchor in columns:
            svg.append(f'<text x="{table_x + offset}" y="{table_y + 12}" text-anchor="{anchor}" font-family="Arial" font-size="12" font-weight="700">{header}</text>')
        svg.append(f'<line x1="{table_x}" y1="{table_y + 18}" x2="{table_x + 675}" y2="{table_y + 18}" stroke="#999"/>')
        for row_idx, category in enumerate(categories, 1):
            row = metrics.get(category)
            if not row:
                continue
            y = table_y + 18 + row_idx * row_h
            if row_idx % 2 == 1:
                svg.append(f'<rect x="{table_x - 6}" y="{y - 15}" width="690" height="{row_h}" fill="#f7f7f7"/>')
            values = [
                label(category),
                fmt_metric(row["metric_coverage"]),
                fmt_metric(row["socially_optimal_rate"]),
                fmt_metric(row["socially_optimal_given_consensus_rate"]),
                fmt_metric(row["avg_social_welfare_efficiency"]),
                fmt_metric(row["avg_chosen_student_rank_global_consensus_only"]),
            ]
            for value, (_, offset, anchor) in zip(values, columns):
                svg.append(f'<text x="{table_x + offset}" y="{y}" text-anchor="{anchor}" font-family="Arial" font-size="12">{value}</text>')
    svg.append("</svg>")
    OUTCOME_SVG.write_text("\n".join(svg))


def make_summary(records: list[dict]) -> None:
    total = len(records)
    category_counts = Counter(row["primary_category"] for row in records)
    confidence_counts = Counter(row["confidence"] for row in records)
    tag_counts = Counter(tag for row in records for tag in row["secondary_tags"])

    by_category = defaultdict(list)
    for row in records:
        by_category[row["primary_category"]].append(row)

    lines = []
    lines.append("# Base Policy Rollout Behavior Analysis")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Log: `logs/game_log_train_auton_12993.log`")
    lines.append("- Slice: lines `1-144891` only, before the base-policy cutoff at line `144892`")
    lines.append(f"- Episodes labeled: `{total}`")
    lines.append("- Episode IDs are 1-indexed by `EPISODE DIAGNOSIS` blocks before the cutoff.")
    lines.append("")

    lines.append("## Category Summary")
    lines.append("")
    lines.append("| Primary category | Count | Percent | Consensus yes | Consensus rate |")
    lines.append("|---|---:|---:|---:|---:|")
    for category in CATEGORY_ORDER:
        rows = by_category.get(category, [])
        if not rows:
            continue
        yes = sum(1 for row in rows if row["consensus"])
        lines.append(
            f"| `{category}` | {len(rows)} | {pct(len(rows), total)} | {yes} | {pct(yes, len(rows))} |"
        )
    lines.append("")

    lines.append("## Main Readout")
    lines.append("")
    negotiation_count = category_counts["negotiation_like"]
    theater_count = category_counts["coordination_theater"]
    thin_count = category_counts["thin_candidate_discussion"]
    proposal_count = category_counts["proposal_following"]
    instant_count = category_counts["instant_consensus"]
    lines.append(
        f"`negotiation_like` appears in {negotiation_count}/{total} episodes ({pct(negotiation_count, total)}), "
        "so the base policy does explore negotiation-shaped behavior in a nontrivial minority of rollouts. "
        "However, many episodes are still shallow: "
        f"`proposal_following`, `thin_candidate_discussion`, and `coordination_theater` together account for "
        f"{proposal_count + thin_count + theater_count}/{total} episodes "
        f"({pct(proposal_count + thin_count + theater_count, total)}). "
        f"`instant_consensus` accounts for {instant_count}/{total} episodes ({pct(instant_count, total)})."
    )
    lines.append("")
    lines.append(
        "This pattern suggests the desired phenomenon is present in exploration, but it is mixed with a large amount "
        "of superficial coordination and proposal-following. That points less toward a total exploration failure and "
        "more toward a learning or prompting problem around making negotiation reliable and payoff-relevant."
    )
    lines.append("")

    lines.append("## Quality Flags")
    lines.append("")
    for tag in [
        "format_error_heavy",
        "format_error_light",
        "invalid_action",
        "prompt_leak",
        "placeholder_output",
        "malformed_tags",
        "semantically_incoherent",
    ]:
        if tag_counts[tag]:
            lines.append(f"- `{tag}`: {tag_counts[tag]} episodes")
    lines.append("")

    lines.append("## Confidence")
    lines.append("")
    lines.append("| Confidence | Count | Percent |")
    lines.append("|---|---:|---:|")
    for confidence in ["high", "medium", "low"]:
        count = confidence_counts[confidence]
        lines.append(f"| `{confidence}` | {count} | {pct(count, total)} |")
    lines.append("")

    lines.append("## Representative Episodes")
    lines.append("")
    for category in CATEGORY_ORDER:
        rows = by_category.get(category, [])
        if not rows:
            continue
        lines.append(f"### `{category}`")
        lines.append("")
        for row in rows[:3]:
            chosen = "none" if row["chosen_student"] is None else row["chosen_student"]
            lines.append(
                f"- Episode {row['episode_id']}: consensus={row['consensus']}, chosen={chosen}, "
                f"confidence={row['confidence']}. {row['rationale']}"
            )
            if row.get("notable_excerpt"):
                lines.append(f"  Excerpt: \"{row['notable_excerpt']}\"")
        lines.append("")

    lines.append("## Full Episode Appendix")
    lines.append("")
    for row in records:
        chosen = "none" if row["chosen_student"] is None else row["chosen_student"]
        tags = ", ".join(f"`{tag}`" for tag in row["secondary_tags"])
        lines.append(f"### Episode {row['episode_id']}")
        lines.append("")
        lines.append(f"- Diagnosis line: `{row['diagnosis_line']}`")
        lines.append(f"- Category: `{row['primary_category']}`")
        lines.append(f"- Tags: {tags}")
        lines.append(f"- Consensus: `{row['consensus']}`")
        lines.append(f"- Chosen student: `{chosen}`")
        lines.append(f"- Turns/messages/votes: `{row['total_turns']}` / `{row['public_message_count']}` / `{row['vote_count']}`")
        lines.append(f"- Waits/wait_for: `{row['wait_count']}` / `{row['wait_for_count']}`")
        lines.append(f"- Format error rate: `{row['format_error_rate']:.2f}`")
        lines.append(f"- Confidence: `{row['confidence']}`")
        lines.append(f"- Rationale: {row['rationale']}")
        if row.get("notable_excerpt"):
            lines.append(f"- Excerpt: \"{row['notable_excerpt']}\"")
        if row.get("suggested_new_category"):
            lines.append(f"- Suggested new category: `{row['suggested_new_category']}`")
            lines.append(f"- Why existing categories fail: {row['why_existing_categories_fail']}")
        lines.append("")

    SUMMARY_MD.write_text("\n".join(lines))


def main() -> int:
    records = load_records()
    write_merged(records)
    make_summary(records)
    make_plots(records)
    print(f"wrote {MERGED_JSONL}")
    print(f"wrote {SUMMARY_MD}")
    print(f"wrote {CATEGORY_SVG}")
    print(f"wrote {OUTCOME_SVG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
