#!/usr/bin/env python3
"""Plot preference-scenario distribution as a single stacked horizontal bar."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


SCENARIO_ORDER = [
    "all_three_share_top",
    "only_prof_1_prof_2_share_top",
    "only_prof_1_prof_3_share_top",
    "only_prof_2_prof_3_share_top",
    "multi_pair_without_all_three_common_top",
    "no_pair_shares_top",
    "malformed_or_missing_preferences",
]

SCENARIO_LABELS = {
    "all_three_share_top": "All 3 share top",
    "only_prof_1_prof_2_share_top": "Prof 1+2 share",
    "only_prof_1_prof_3_share_top": "Prof 1+3 share",
    "only_prof_2_prof_3_share_top": "Prof 2+3 share",
    "multi_pair_without_all_three_common_top": "Multi-pair share",
    "no_pair_shares_top": "No pair shares",
    "malformed_or_missing_preferences": "Missing prefs",
}

SCENARIO_COLORS = {
    "all_three_share_top": "#15803d",  # green
    "only_prof_1_prof_2_share_top": "#bfdbfe",  # pair-family blues
    "only_prof_1_prof_3_share_top": "#60a5fa",
    "only_prof_2_prof_3_share_top": "#2563eb",
    "multi_pair_without_all_three_common_top": "#1e40af",
    "no_pair_shares_top": "#f97316",  # orange
    "malformed_or_missing_preferences": "#9ca3af",
}


def read_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["episodes"] = int(row["episodes"])
        row["percent"] = float(row["percent"])
    return rows


def esc(text: Any) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def text_node(
    x: float,
    y: float,
    text: str,
    *,
    size: int = 12,
    anchor: str = "middle",
    weight: int = 400,
    fill: str = "#111827",
) -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="Arial, sans-serif" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}">{esc(text)}</text>'
    )


def multiline_text(
    x: float,
    y: float,
    lines: list[str],
    *,
    size: int = 11,
    anchor: str = "middle",
    weight: int = 400,
    fill: str = "#111827",
    line_gap: int = 14,
) -> list[str]:
    return [
        text_node(
            x,
            y + idx * line_gap,
            line,
            size=size,
            anchor=anchor,
            weight=weight if idx == 0 else 400,
            fill=fill,
        )
        for idx, line in enumerate(lines)
    ]


def ordered_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_scenario = {row["scenario"]: row for row in rows}
    ordered = [by_scenario[name] for name in SCENARIO_ORDER if name in by_scenario]
    ordered.extend(
        row for row in sorted(rows, key=lambda item: item["scenario"])
        if row["scenario"] not in SCENARIO_ORDER
    )
    return ordered


def build_svg(rows: list[dict[str, Any]], title: str) -> str:
    rows = ordered_rows(rows)
    total = sum(row["episodes"] for row in rows) or 1

    width = 1180
    height = 390
    margin_left = 70
    margin_right = 70
    bar_x = margin_left
    bar_y = 105
    bar_w = width - margin_left - margin_right
    bar_h = 58

    nodes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text_node(width / 2, 34, title, size=20, weight=700),
        text_node(width / 2, 58, "Scenario distribution by episode count", size=12, fill="#4b5563"),
    ]

    x = bar_x
    bottom_label_rows = [bar_y + bar_h + 44, bar_y + bar_h + 88]
    for idx, row in enumerate(rows):
        scenario = row["scenario"]
        episodes = row["episodes"]
        pct = episodes / total
        w = pct * bar_w
        color = SCENARIO_COLORS.get(scenario, "#6b7280")
        nodes.append(
            f'<rect x="{x:.1f}" y="{bar_y}" width="{w:.1f}" height="{bar_h}" '
            f'fill="{color}" stroke="#ffffff" stroke-width="2"/>'
        )

        cx = x + w / 2
        label = SCENARIO_LABELS.get(scenario, scenario)
        label_lines = [label, f"{episodes} eps", f"{pct:.0%}"]
        if w >= 145:
            nodes.extend(
                multiline_text(
                    cx,
                    bar_y + 21,
                    label_lines,
                    size=11,
                    weight=700,
                    fill="#111827",
                    line_gap=15,
                )
            )
        else:
            y = bottom_label_rows[idx % len(bottom_label_rows)]
            nodes.append(
                f'<line x1="{cx:.1f}" y1="{bar_y + bar_h}" x2="{cx:.1f}" '
                f'y2="{y - 31:.1f}" stroke="#9ca3af" stroke-width="1"/>'
            )
            nodes.extend(
                multiline_text(
                    cx,
                    y - 16,
                    label_lines,
                    size=10,
                    weight=700,
                    fill="#374151",
                    line_gap=12,
                )
            )
        x += w

    # Total.
    axis_y = bar_y + bar_h + 130
    nodes.append(text_node(width / 2, axis_y, f"total episodes: {total}", size=12, weight=700, fill="#374151"))

    nodes.append("</svg>")
    return "\n".join(nodes)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="preference_scenario_metrics_summary.csv")
    parser.add_argument("--output", type=Path, default=None, help="Output SVG path")
    parser.add_argument("--title", default="Preference Scenario Distribution", help="Plot title")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output or args.input.with_name("preference_scenario_distribution.svg")
    rows = read_rows(args.input)
    output.write_text(build_svg(rows, args.title))
    print(output)


if __name__ == "__main__":
    main()
