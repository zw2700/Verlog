#!/usr/bin/env python3
"""Plot scenario distributions for a sweep of preference-generation settings."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
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
    "all_three_share_top": "All 3 share",
    "only_prof_1_prof_2_share_top": "P1+P2",
    "only_prof_1_prof_3_share_top": "P1+P3",
    "only_prof_2_prof_3_share_top": "P2+P3",
    "multi_pair_without_all_three_common_top": "Multi-pair",
    "no_pair_shares_top": "No pair",
    "malformed_or_missing_preferences": "Missing",
}

SCENARIO_COLORS = {
    "all_three_share_top": "#15803d",
    "only_prof_1_prof_2_share_top": "#bfdbfe",
    "only_prof_1_prof_3_share_top": "#60a5fa",
    "only_prof_2_prof_3_share_top": "#2563eb",
    "multi_pair_without_all_three_common_top": "#1e40af",
    "no_pair_shares_top": "#f97316",
    "malformed_or_missing_preferences": "#9ca3af",
}

EXPERIMENT_LABELS = {
    "baseline_random_permutation": "Random permutation",
    "direct_distinct_top_feature": "Distinct top feature",
    "rejection_corr_le_0_3": "corr <= 0.3",
    "rejection_corr_le_0_0": "corr <= 0.0",
    "rejection_corr_le_neg_0_1": "corr <= -0.1",
    "rejection_corr_le_0_0_distinct_top": "corr <= 0.0 + distinct top",
}

EXPERIMENT_ORDER = [
    "baseline_random_permutation",
    "rejection_corr_le_0_3",
    "rejection_corr_le_0_0",
    "rejection_corr_le_neg_0_1",
]

EXCLUDED_EXPERIMENTS = {
    "direct_distinct_top_feature",
    "rejection_corr_le_0_0_distinct_top",
}


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


def read_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["count"] = int(row["count"])
        row["probability"] = float(row["probability"])
    return rows


def experiment_order(experiments: set[str]) -> list[str]:
    experiments = experiments - EXCLUDED_EXPERIMENTS
    ordered = [name for name in EXPERIMENT_ORDER if name in experiments]
    ordered.extend(sorted(experiments - set(ordered)))
    return ordered


def build_svg(rows: list[dict[str, Any]], title: str) -> str:
    by_experiment: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        by_experiment[row["experiment"]][row["scenario"]] = row

    experiments = experiment_order(set(by_experiment))
    width = 1220
    row_h = 58
    bar_h = 30
    margin_left = 250
    margin_right = 60
    margin_top = 82
    margin_bottom = 92
    bar_w = width - margin_left - margin_right
    height = margin_top + row_h * len(experiments) + margin_bottom

    nodes = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text_node(width / 2, 34, title, size=20, weight=700),
        text_node(width / 2, 58, "Each row is a 100k simulated preference-scenario distribution", size=12, fill="#4b5563"),
    ]

    for row_idx, experiment in enumerate(experiments):
        y = margin_top + row_idx * row_h
        label = EXPERIMENT_LABELS.get(experiment, experiment)
        nodes.append(text_node(margin_left - 18, y + bar_h / 2 + 5, label, size=12, anchor="end", weight=700))
        x = margin_left
        for scenario in SCENARIO_ORDER:
            row = by_experiment[experiment].get(scenario)
            if not row:
                continue
            p = row["probability"]
            w = p * bar_w
            if w <= 0:
                continue
            color = SCENARIO_COLORS.get(scenario, "#6b7280")
            nodes.append(
                f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{bar_h}" '
                f'fill="{color}" stroke="#ffffff" stroke-width="1.4"/>'
            )
            if w >= 52:
                fill = "#ffffff" if scenario in {"only_prof_2_prof_3_share_top", "multi_pair_without_all_three_common_top", "all_three_share_top"} else "#111827"
                nodes.append(
                    text_node(
                        x + w / 2,
                        y + bar_h / 2 + 4,
                        f"{p:.0%}",
                        size=11,
                        weight=700,
                        fill=fill,
                    )
                )
            x += w

    legend_y = height - 48
    legend_x = margin_left
    legend_items = [
        ("All 3 share top", SCENARIO_COLORS["all_three_share_top"]),
        ("Pair-sharing variants", SCENARIO_COLORS["only_prof_1_prof_3_share_top"]),
        ("No pair shares top", SCENARIO_COLORS["no_pair_shares_top"]),
        ("Missing prefs", SCENARIO_COLORS["malformed_or_missing_preferences"]),
    ]
    lx = legend_x
    for label, color in legend_items:
        nodes.append(f'<rect x="{lx:.1f}" y="{legend_y}" width="20" height="14" fill="{color}"/>')
        nodes.append(text_node(lx + 26, legend_y + 12, label, size=11, anchor="start", fill="#374151"))
        lx += 220

    nodes.append("</svg>")
    return "\n".join(nodes)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="preference_scenario_simulation_summary.csv")
    parser.add_argument("--output", type=Path, default=None, help="Output SVG path")
    parser.add_argument("--title", default="Preference Diversity Sweep Scenario Distribution", help="Plot title")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output or args.input.with_name("preference_scenario_sweep_distribution.svg")
    output.write_text(build_svg(read_rows(args.input), args.title))
    print(output)


if __name__ == "__main__":
    main()
