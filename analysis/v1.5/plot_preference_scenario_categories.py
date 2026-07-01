#!/usr/bin/env python3
"""Plot preference-scenario category counts shaded by socially optimal rate."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


SCENARIO_LABELS = {
    "all_three_share_top": "All 3\nshare top",
    "only_prof_1_prof_2_share_top": "Prof 1+2\nshare top",
    "only_prof_1_prof_3_share_top": "Prof 1+3\nshare top",
    "only_prof_2_prof_3_share_top": "Prof 2+3\nshare top",
    "no_pair_shares_top": "No pair\nshares top",
    "multi_pair_without_all_three_common_top": "Multi-pair\nno common top",
    "malformed_or_missing_preferences": "Missing\nprefs",
}

CATEGORY_ORDER = [
    "instant_decision",
    "negotiation",
    "stalled_coordination_failure",
    "malformed_or_other",
]

CATEGORY_LABELS = {
    "instant_decision": "Instant",
    "negotiation": "Negotiation",
    "stalled_coordination_failure": "Stalled",
    "malformed_or_other": "Malformed",
}

CATEGORY_GRADIENTS = {
    "instant_decision": ((254, 226, 226), (153, 27, 27)),  # red
    "negotiation": ((219, 234, 254), (30, 64, 175)),  # blue
    "stalled_coordination_failure": ((254, 243, 199), (180, 83, 9)),  # amber
    "malformed_or_other": ((229, 231, 235), (75, 85, 99)),  # gray
}


def read_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["episodes"] = int(row["episodes"])
        row["socially_optimal_rate"] = (
            float(row["socially_optimal_rate"])
            if row.get("socially_optimal_rate") not in ("", "NA", None)
            else None
        )
    return rows


def color_for_rate(category: str, rate: float | None) -> str:
    if rate is None:
        return "#d1d5db"
    rate = max(0.0, min(1.0, rate))
    lo, hi = CATEGORY_GRADIENTS.get(category, ((229, 231, 235), (31, 41, 55)))
    rgb = tuple(round(lo[i] + (hi[i] - lo[i]) * rate) for i in range(3))
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def fmt_rate(rate: float | None) -> str:
    return "NA" if rate is None else f"{rate:.2f}"


def scenario_order(rows: list[dict[str, Any]]) -> list[str]:
    present = {row["scenario"] for row in rows}
    ordered = [name for name in SCENARIO_LABELS if name in present]
    ordered.extend(sorted(present - set(ordered)))
    return ordered


def category_order(rows: list[dict[str, Any]]) -> list[str]:
    present = {row["category"] for row in rows}
    ordered = [name for name in CATEGORY_ORDER if name in present]
    ordered.extend(sorted(present - set(ordered)))
    return ordered


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
    transform: str | None = None,
) -> str:
    transform_attr = f' transform="{esc(transform)}"' if transform else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="Arial, sans-serif" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}"{transform_attr}>{esc(text)}</text>'
    )


def multiline_label(x: float, y: float, label: str, *, size: int = 12) -> list[str]:
    lines = label.split("\n")
    nodes = []
    for i, line in enumerate(lines):
        nodes.append(text_node(x, y + i * (size + 3), line, size=size))
    return nodes


def build_svg(rows: list[dict[str, Any]], title: str) -> str:
    scenarios = scenario_order(rows)
    categories = category_order(rows)
    by_key = {(row["scenario"], row["category"]): row for row in rows}
    totals = {
        scenario: sum(row["episodes"] for row in rows if row["scenario"] == scenario)
        for scenario in scenarios
    }
    max_total = max(totals.values()) if totals else 1

    width = max(1180, 165 * len(scenarios) + 360)
    height = 650
    margin_left = 85
    margin_right = 290
    margin_top = 82
    margin_bottom = 112
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    bar_w = min(76, plot_w / max(1, len(scenarios)) * 0.48)
    step = plot_w / max(1, len(scenarios))

    nodes: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<defs>",
        '<linearGradient id="instantGradient" x1="0" y1="1" x2="0" y2="0">',
        f'<stop offset="0%" stop-color="{color_for_rate("instant_decision", 0.0)}"/>',
        f'<stop offset="100%" stop-color="{color_for_rate("instant_decision", 1.0)}"/>',
        "</linearGradient>",
        '<linearGradient id="negotiationGradient" x1="0" y1="1" x2="0" y2="0">',
        f'<stop offset="0%" stop-color="{color_for_rate("negotiation", 0.0)}"/>',
        f'<stop offset="100%" stop-color="{color_for_rate("negotiation", 1.0)}"/>',
        "</linearGradient>",
        "</defs>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text_node(width / 2, 34, title, size=20, weight=700),
        text_node(width / 2, 57, "Bar height = episode count; hue = category; shade intensity = socially optimal rate", size=12, fill="#4b5563"),
    ]

    # Axes and y grid.
    x0 = margin_left
    y0 = margin_top + plot_h
    nodes.append(f'<line x1="{x0}" y1="{margin_top}" x2="{x0}" y2="{y0}" stroke="#111827" stroke-width="1"/>')
    nodes.append(f'<line x1="{x0}" y1="{y0}" x2="{margin_left + plot_w}" y2="{y0}" stroke="#111827" stroke-width="1"/>')
    for tick in range(0, max_total + 1, max(1, round(max_total / 5))):
        y = y0 - (tick / max_total) * plot_h
        nodes.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{margin_left + plot_w}" y2="{y:.1f}" stroke="#e5e7eb" stroke-width="1"/>')
        nodes.append(text_node(x0 - 10, y + 4, str(tick), size=11, anchor="end", fill="#4b5563"))
    y_label_center = margin_top + plot_h / 2
    nodes.append(
        text_node(
            22,
            y_label_center,
            "Episodes",
            size=12,
            anchor="middle",
            fill="#374151",
            transform=f"rotate(-90 22 {y_label_center:.1f})",
        )
    )

    # Bars.
    for idx, scenario in enumerate(scenarios):
        cx = margin_left + step * (idx + 0.5)
        x = cx - bar_w / 2
        y_cursor = y0
        for category in categories:
            row = by_key.get((scenario, category))
            if not row:
                continue
            episodes = row["episodes"]
            rate = row["socially_optimal_rate"]
            h = (episodes / max_total) * plot_h
            y = y_cursor - h
            fill = color_for_rate(category, rate)
            nodes.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" '
                f'fill="{fill}" stroke="#ffffff" stroke-width="1.4"/>'
            )
            # Keep interior labels sparse: only show counts where segments have room.
            if h >= 24:
                nodes.append(text_node(cx, y + h / 2 + 4, str(episodes), size=12, weight=700, fill="#111827"))
            y_cursor = y

        total = totals[scenario]
        nodes.append(text_node(cx, y_cursor - 8, f"n={total}", size=12, weight=700))
        nodes.extend(multiline_label(cx, y0 + 22, SCENARIO_LABELS.get(scenario, scenario), size=11))

    # Category and shade legend.
    legend_x = width - margin_right + 48
    legend_y = margin_top + 12
    nodes.append(text_node(legend_x, legend_y - 18, "Category", size=12, weight=700, anchor="start"))
    for i, category in enumerate(categories):
        y = legend_y + i * 30
        nodes.append(f'<rect x="{legend_x}" y="{y - 15}" width="19" height="22" fill="{color_for_rate(category, 0.25)}" stroke="#ffffff"/>')
        nodes.append(f'<rect x="{legend_x + 19}" y="{y - 15}" width="19" height="22" fill="{color_for_rate(category, 0.75)}" stroke="#ffffff"/>')
        nodes.append(text_node(legend_x + 48, y + 2, CATEGORY_LABELS.get(category, category), size=13, anchor="start"))
    scale_y = legend_y + len(categories) * 30 + 36
    nodes.append(text_node(legend_x, scale_y - 18, "SO rate scale", size=12, weight=700, anchor="start"))
    scale_h = 128
    scale_w = 28
    nodes.append(f'<rect x="{legend_x}" y="{scale_y}" width="{scale_w}" height="{scale_h}" fill="url(#instantGradient)" stroke="#d1d5db"/>')
    nodes.append(text_node(legend_x + scale_w + 10, scale_y + 5, "1.0", size=12, anchor="start", fill="#4b5563"))
    nodes.append(text_node(legend_x + scale_w + 10, scale_y + scale_h, "0.0", size=12, anchor="start", fill="#4b5563"))
    nodes.append(text_node(legend_x + scale_w / 2, scale_y + scale_h + 21, "Instant", size=12, anchor="middle", fill="#4b5563"))

    scale2_x = legend_x + 120
    nodes.append(f'<rect x="{scale2_x}" y="{scale_y}" width="{scale_w}" height="{scale_h}" fill="url(#negotiationGradient)" stroke="#d1d5db"/>')
    nodes.append(text_node(scale2_x + scale_w / 2, scale_y + scale_h + 21, "Negotiation", size=12, anchor="middle", fill="#4b5563"))

    # Compact numeric table under bars: SO rates by scenario/category.
    table_y = height - 38
    nodes.append(text_node(margin_left, table_y, "Segment labels show counts when space allows; exact SO rates are in the CSV.", size=11, anchor="start", fill="#6b7280"))

    nodes.append("</svg>")
    return "\n".join(nodes)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="preference_scenario_category_breakdown.csv")
    parser.add_argument("--output", type=Path, default=None, help="Output SVG path")
    parser.add_argument("--title", default="Preference Scenarios by Category", help="Plot title")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output or args.input.with_name("preference_scenario_category_breakdown.svg")
    rows = read_rows(args.input)
    output.write_text(build_svg(rows, args.title))
    print(output)


if __name__ == "__main__":
    main()
