#!/usr/bin/env python3
"""Plot the frozen asymmetric-critic W&B learning curves."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import wandb


RUNS = {
    "Actor-visible": "zuz5ag7n",
    "All utilities": "fvagz4xj",
}

METRICS = [
    "training/global_step",
    "critic/v_s0_return_pearson",
    "critic/v_return_pearson",
    "critic/vf_explained_var",
    "critic/vf_loss",
    "critic/per_agent/prof_1/ev",
    "critic/per_agent/prof_2/ev",
    "critic/per_agent/prof_3/ev",
]

COLORS = {
    "Actor-visible": "#2563eb",
    "All utilities": "#d97706",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-prefix",
        default="analysis/figures/asymmetric_critic",
        help="Path prefix used for generated PNG files.",
    )
    parser.add_argument("--entity", default=os.environ.get("WANDB_ENTITY"))
    parser.add_argument("--project", default="unscripted")
    return parser.parse_args()


def fetch_histories(entity: str | None, project: str) -> tuple[dict[str, pd.DataFrame], dict[str, object]]:
    api = wandb.Api(timeout=90)
    entity = entity or api.default_entity
    project_path = project if "/" in project else f"{entity}/{project}"
    frames: dict[str, pd.DataFrame] = {}
    runs: dict[str, object] = {}

    for label, run_id in RUNS.items():
        run = api.run(f"{project_path}/{run_id}")
        rows = list(run.scan_history(keys=METRICS, page_size=1000))
        frame = pd.DataFrame(rows).dropna(subset=["training/global_step"])
        frame = frame.sort_values("training/global_step").drop_duplicates("training/global_step", keep="last")
        frame["training/global_step"] = frame["training/global_step"].astype(int)
        frames[label] = frame
        runs[label] = run

    return frames, runs


def style_axis(ax: plt.Axes) -> None:
    ax.grid(True, alpha=0.2, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.axvline(10.5, color="#991b1b", linestyle="--", linewidth=1.2, alpha=0.85)


def plot_learning_curves(frames: dict[str, pd.DataFrame], output: Path) -> None:
    panels = [
        ("critic/v_s0_return_pearson", "Start-state return Pearson", None),
        ("critic/v_return_pearson", "Token-level return Pearson", None),
        ("critic/vf_explained_var", "Explained variance (display clipped at -1)", "clip_ev"),
        ("critic/vf_loss", "Value loss (log scale)", "log"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
    for ax, (metric, title, mode) in zip(axes.flat, panels):
        for label, frame in frames.items():
            x = frame["training/global_step"]
            raw = frame[metric].astype(float)
            smooth = raw.rolling(5, min_periods=2).mean()
            if mode == "clip_ev":
                raw = raw.clip(lower=-1.0, upper=1.0)
                smooth = smooth.clip(lower=-1.0, upper=1.0)
            ax.plot(x, raw, color=COLORS[label], alpha=0.22, linewidth=1)
            ax.plot(x, smooth, color=COLORS[label], linewidth=2.2, label=f"{label} (5-step mean)")

        style_axis(ax)
        ax.set_title(title, fontsize=11, fontweight="semibold")
        ax.set_xlabel("Critic training step")
        if mode == "log":
            ax.set_yscale("log")
        elif mode == "clip_ev":
            ax.set_ylim(-1.05, 1.0)
        else:
            ax.set_ylim(-0.15, 1.0)

    axes[0, 0].legend(frameon=False, fontsize=9, loc="lower right")
    axes[0, 0].text(
        11.3,
        -0.09,
        "planned PPO actor start",
        color="#991b1b",
        fontsize=8,
        va="bottom",
    )
    fig.suptitle("Frozen-actor critic learning curves", fontsize=15, fontweight="bold")
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def window_mean(frame: pd.DataFrame, metric: str, low: int, high: int) -> float:
    selected = frame.loc[frame["training/global_step"].between(low, high), metric].dropna().astype(float)
    return float(selected.mean())


def first_sustained_step(frame: pd.DataFrame, metric: str, threshold: float, count: int = 3) -> int | None:
    values = frame[["training/global_step", metric]].dropna().reset_index(drop=True)
    for start in range(len(values) - count + 1):
        window = values.iloc[start : start + count]
        if bool((window[metric].astype(float) > threshold).all()):
            return int(window.iloc[0]["training/global_step"])
    return None


def plot_warmup_assessment(frame: pd.DataFrame, output: Path) -> None:
    early = (6, 10)
    mature = (61, 75)
    metrics = [
        ("critic/v_s0_return_pearson", "Start-state\nPearson"),
        ("critic/v_return_pearson", "Token-level\nPearson"),
        ("critic/vf_explained_var", "Explained\nvariance"),
    ]
    early_values = [window_mean(frame, metric, *early) for metric, _ in metrics]
    mature_values = [window_mean(frame, metric, *mature) for metric, _ in metrics]
    early_loss = window_mean(frame, "critic/vf_loss", *early)
    mature_loss = window_mean(frame, "critic/vf_loss", *mature)

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4), gridspec_kw={"width_ratios": [2.2, 1]})
    x = np.arange(len(metrics))
    width = 0.34
    axes[0].bar(x - width / 2, early_values, width, label="Steps 6–10", color="#94a3b8")
    axes[0].bar(x + width / 2, mature_values, width, label="Steps 61–75", color=COLORS["All utilities"])
    axes[0].axhline(0, color="#111827", linewidth=0.8)
    axes[0].set_xticks(x, [name for _, name in metrics])
    axes[0].set_ylim(-0.55, 0.9)
    axes[0].set_title("Fit at warmup cutoff vs mature critic", fontweight="semibold")
    axes[0].legend(frameon=False, fontsize=9)

    axes[1].bar([0, 1], [early_loss, mature_loss], color=["#94a3b8", COLORS["All utilities"]])
    axes[1].set_xticks([0, 1], ["Steps\n6–10", "Steps\n61–75"])
    axes[1].set_title("Value loss", fontweight="semibold")
    axes[1].set_ylim(0, max(early_loss, mature_loss) * 1.25)
    for index, value in enumerate([early_loss, mature_loss]):
        axes[1].text(index, value + 0.001, f"{value:.3f}", ha="center", fontsize=9)

    for ax in axes:
        ax.grid(True, axis="y", alpha=0.2)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    thresholds = {
        threshold: first_sustained_step(frame, "critic/vf_explained_var", threshold)
        for threshold in (0.0, 0.25, 0.5)
    }
    fig.suptitle("Ten critic steps do not produce a mature value model", fontsize=14, fontweight="bold")
    fig.text(
        0.5,
        -0.01,
        "All-utilities explained variance stays above 0 / 0.25 / 0.5 for three steps starting at "
        f"steps {thresholds[0.0]} / {thresholds[0.25]} / {thresholds[0.5]}.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.92))
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_window_comparison(frames: dict[str, pd.DataFrame], output: Path) -> None:
    windows = [(6, 10, "Steps 6–10"), (21, 40, "Steps 21–40"), (61, 75, "Steps 61–75")]
    panels = [
        ("critic/v_s0_return_pearson", "Start-state return Pearson", "higher is better"),
        ("critic/v_return_pearson", "Token-level return Pearson", "higher is better"),
        ("critic/vf_explained_var", "Explained variance", "higher is better"),
        ("critic/vf_loss", "Value loss", "lower is better"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
    x = np.arange(len(windows))
    width = 0.36
    for ax, (metric, title, direction) in zip(axes.flat, panels):
        for offset, (label, frame) in zip((-width / 2, width / 2), frames.items()):
            values = [window_mean(frame, metric, low, high) for low, high, _ in windows]
            bars = ax.bar(x + offset, values, width, label=label, color=COLORS[label])
            for bar, value in zip(bars, values):
                va = "bottom" if value >= 0 else "top"
                delta = 0.012 if metric != "critic/vf_loss" else 0.0012
                y = value + delta if value >= 0 else value - delta
                ax.text(bar.get_x() + bar.get_width() / 2, y, f"{value:.3f}", ha="center", va=va, fontsize=8)

        ax.set_xticks(x, [name for _, _, name in windows])
        ax.axhline(0, color="#111827", linewidth=0.8)
        ax.grid(True, axis="y", alpha=0.2)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_title(f"{title}\n{direction}", fontsize=11, fontweight="semibold")
        if metric == "critic/vf_loss":
            ax.set_ylim(0, 0.1)
        elif metric == "critic/vf_explained_var":
            ax.set_ylim(-1.65, 0.8)
        else:
            ax.set_ylim(0, 0.9)

    axes[0, 0].legend(frameon=False, fontsize=9, loc="upper left")
    fig.suptitle(
        "Privileged state improves mid-training fit, not the mature critic",
        fontsize=15,
        fontweight="bold",
    )
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_per_agent(frame: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    series = [
        ("critic/vf_explained_var", "Overall", "#111827"),
        ("critic/per_agent/prof_1/ev", "Professor 1", "#2563eb"),
        ("critic/per_agent/prof_2/ev", "Professor 2", "#059669"),
        ("critic/per_agent/prof_3/ev", "Professor 3", "#dc2626"),
    ]
    for metric, label, color in series:
        smooth = frame[metric].astype(float).rolling(5, min_periods=2).mean().clip(lower=-1.0, upper=1.0)
        ax.plot(frame["training/global_step"], smooth, label=label, color=color, linewidth=2)

    style_axis(ax)
    ax.set_ylim(-1.05, 1.0)
    ax.set_xlabel("Critic training step")
    ax.set_ylabel("Explained variance (5-step mean; clipped at -1)")
    ax.set_title("All-utilities fit improves across all professors", fontsize=13, fontweight="bold")
    ax.legend(frameon=False, ncol=4, fontsize=9, loc="lower right")
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def print_summary(frames: dict[str, pd.DataFrame], runs: dict[str, object]) -> None:
    for label, frame in frames.items():
        run = runs[label]
        print("RUN", label, run.id, run.state, int(frame["training/global_step"].max()), run.url, sep="\t")
        for low, high in ((6, 10), (11, 20), (21, 40), (61, 75)):
            if int(frame["training/global_step"].max()) < low:
                continue
            values = [
                window_mean(frame, metric, low, min(high, int(frame["training/global_step"].max())))
                for metric in (
                    "critic/v_s0_return_pearson",
                    "critic/v_return_pearson",
                    "critic/vf_explained_var",
                    "critic/vf_loss",
                )
            ]
            print("WINDOW", label, f"{low}-{min(high, int(frame['training/global_step'].max()))}", *values, sep="\t")

    treatment = frames["All utilities"]
    for threshold in (0.0, 0.25, 0.5):
        step = first_sustained_step(treatment, "critic/vf_explained_var", threshold)
        print("SUSTAINED_EV", threshold, step, sep="\t")
    for professor in (1, 2, 3):
        metric = f"critic/per_agent/prof_{professor}/ev"
        print("FINAL15_AGENT_EV", professor, window_mean(treatment, metric, 61, 75), sep="\t")


def main() -> None:
    args = parse_args()
    prefix = Path(args.output_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    frames, runs = fetch_histories(args.entity, args.project)
    plot_learning_curves(frames, prefix.with_name(prefix.name + "_learning_curves.png"))
    plot_warmup_assessment(
        frames["All utilities"], prefix.with_name(prefix.name + "_warmup_assessment.png")
    )
    plot_window_comparison(frames, prefix.with_name(prefix.name + "_window_comparison.png"))
    plot_per_agent(frames["All utilities"], prefix.with_name(prefix.name + "_per_agent_ev.png"))
    print_summary(frames, runs)


if __name__ == "__main__":
    main()
