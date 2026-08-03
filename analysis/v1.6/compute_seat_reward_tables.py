#!/usr/bin/env python3
"""Per-seat individual-reward tables for the hiring-committee runs.

Emits the three tables in seat_reward_asymmetry.md:
  1. mean individual reward by run (population average = social welfare / 3)
  2. mean individual reward by seat, per run
  3. per-seat delta from switching the converged RL policy to Haiku-style play

`terminal_rewards` holds each professor's own utility for the chosen student
(reward_mode="individual", the default in every run to date), so the three
seats sum to `actual_total_utility`.

Run from the repo root:
    python3 analysis/v1.6/compute_seat_reward_tables.py
"""

from __future__ import annotations

import glob
import json
import math
import statistics as st
from collections import defaultdict

RUNS = {
    "haiku_14263": dict(
        label="Haiku 4.5",
        paths=["logs/episode_log_rollout_cmu-gateway_us.anthropic."
               "claude-haiku-4-5-20251001-v1_0_14263_no_all_voted_termination.jsonl"],
    ),
    "qwen3_base_14988": dict(
        label="Qwen3-4B base",
        paths=["logs/episode_log_rollout_local-vllm_Qwen_Qwen3-4B_14988"
               "_qwen3_4b_no_think_no_all_voted_termination.jsonl"],
    ),
    "rl_17323_early": dict(
        label="RL 17323, steps 1-10",
        paths=["logs/episode_log_train_auton_17323/*.jsonl"],
        steps=(1, 10),
    ),
    "rl_17323_late": dict(
        label="RL 17323, steps 66-75",
        paths=["logs/episode_log_train_auton_17323/*.jsonl"],
        steps=(66, 75),
    ),
}

SEATS = ("prof_1", "prof_2", "prof_3")


def sem(xs: list[float]) -> float:
    return st.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else float("nan")


def load(spec: dict) -> list[dict]:
    steps = spec.get("steps")
    rows = []
    for pattern in spec["paths"]:
        for path in sorted(glob.glob(pattern)):
            with open(path) as fh:
                for line in fh:
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    if steps is not None:
                        gs = row.get("global_step")
                        if gs is None or not (steps[0] <= gs <= steps[1]):
                            continue
                    if not row.get("consensus"):
                        continue
                    rows.append(row)
    return rows


def summarize(rows: list[dict]) -> dict:
    per_seat: dict[str, list[float]] = defaultdict(list)
    ep_mean, so, eff = [], [], []
    for row in rows:
        rewards = row.get("terminal_rewards") or {}
        vals = [float(rewards[s]) for s in SEATS if s in rewards]
        if len(vals) != len(SEATS):
            continue
        for seat in SEATS:
            per_seat[seat].append(float(rewards[seat]))
        # Episode is the clustering unit: average the three seats within it.
        ep_mean.append(st.mean(vals))
        so.append(bool(row["socially_optimal"]))
        eff.append(float(row["social_welfare_efficiency"]))
    return dict(
        n=len(ep_mean),
        seat_mean={s: st.mean(per_seat[s]) for s in SEATS},
        seat_sem={s: sem(per_seat[s]) for s in SEATS},
        mean=st.mean(ep_mean),
        # Clustered by episode, since the three seats sum to total utility.
        sem=sem(ep_mean),
        so=st.mean(so),
        so_sem=math.sqrt(st.mean(so) * (1 - st.mean(so)) / len(so)),
        eff=st.mean(eff),
        spread=max(st.mean(per_seat[s]) for s in SEATS)
        - min(st.mean(per_seat[s]) for s in SEATS),
    )


def diff_sigma(a_mean, a_sem, b_mean, b_sem) -> tuple[float, float, float]:
    d = a_mean - b_mean
    se = math.sqrt(a_sem**2 + b_sem**2)
    return d, se, d / se


def md_table(headers: list[str], aligns: str, rows: list[list[str]]) -> str:
    """Render a GFM table with every column padded to a uniform width.

    `aligns` is one char per column: "l" left, "r" right. Cell strings are
    measured as written, so inline `**bold**` markers still pad correctly.
    """
    widths = [
        max([len(h)] + [len(r[i]) for r in rows]) for i, h in enumerate(headers)
    ]

    def line(cells: list[str]) -> str:
        padded = [
            c.ljust(w) if a == "l" else c.rjust(w)
            for c, w, a in zip(cells, widths, aligns)
        ]
        return "| " + " | ".join(padded) + " |"

    sep = "|" + "|".join(
        (":" + "-" * (w + 1)) if a == "l" else ("-" * (w + 1) + ":")
        for w, a in zip(widths, aligns)
    ) + "|"
    return "\n".join([line(headers), sep] + [line(r) for r in rows])


def val(mean: float, err: float, bold: bool = False) -> str:
    s = f"{mean:.4f} ± {err:.4f}"
    return f"**{s}**" if bold else s


def delta(d: float, se: float, z: float, bold: bool = False) -> str:
    s = f"{d:+.4f} ± {se:.4f} ({z:+.1f}σ)"
    return f"**{s}**" if bold else s


DISPLAY = {
    "haiku_14263": "Haiku 4.5 (`14263`)",
    "rl_17323_late": "RL `17323`, steps 66-75",
    "qwen3_base_14988": "Qwen3-4B base (`14988`)",
    "rl_17323_early": "RL `17323`, steps 1-10",
}
ORDER = ["haiku_14263", "rl_17323_late", "qwen3_base_14988", "rl_17323_early"]


def main() -> None:
    res = {k: summarize(load(v)) for k, v in RUNS.items()}
    h, l, e = res["haiku_14263"], res["rl_17323_late"], res["rl_17323_early"]

    print("## Table 1 — Mean individual reward by run\n")
    print(md_table(
        ["run", "n (consensus)", "social optimality", "welfare efficiency",
         "mean individual reward"],
        "lrrrr",
        [[DISPLAY[k], str(res[k]["n"]),
          f"{res[k]['so']:.3f} ± {res[k]['so_sem']:.3f}",
          f"{res[k]['eff']:.4f}",
          val(res[k]["mean"], res[k]["sem"], bold=(k == "haiku_14263"))]
         for k in ORDER],
    ))

    print("\n## Table 2 — Mean individual reward by seat\n")
    rows = []
    for k in ORDER:
        v = res[k]
        cells = [DISPLAY[k]]
        for s in SEATS:
            bold = k == "rl_17323_late" and s == "prof_1"
            cells.append(val(v["seat_mean"][s], v["seat_sem"][s], bold=bold))
        spread = f"{v['spread']:.4f}"
        if k in ("haiku_14263", "rl_17323_late"):
            spread = f"**{spread}**"
        cells += [f"{v['mean']:.4f}", spread]
        rows.append(cells)
    print(md_table(
        ["run", "prof_1", "prof_2", "prof_3", "average", "spread"],
        "lrrrrr", rows,
    ))

    print("\n## Table 3a — What training actually bought (RL early → late)\n")
    tot = sum(l["seat_mean"][s] - e["seat_mean"][s] for s in SEATS)
    rows = []
    for s in SEATS:
        d, se, z = diff_sigma(l["seat_mean"][s], l["seat_sem"][s],
                              e["seat_mean"][s], e["seat_sem"][s])
        bold = s == "prof_1"
        share = f"{d / tot:.1%}"
        rows.append([s, f"{e['seat_mean'][s]:.4f}", f"{l['seat_mean'][s]:.4f}",
                     delta(d, se, z, bold=bold),
                     f"**{share}**" if bold else share])
    d, se, z = diff_sigma(l["mean"], l["sem"], e["mean"], e["sem"])
    rows.append(["average", f"{e['mean']:.4f}", f"{l['mean']:.4f}",
                 delta(d, se, z), "—"])
    rows.append(["seat spread", f"{e['spread']:.4f}", f"{l['spread']:.4f}",
                 f"{l['spread'] - e['spread']:+.4f}", "—"])
    print(md_table(["seat", "steps 1-10", "steps 66-75", "Δ",
                    "share of average gain"], "lrrrr", rows))

    print("\n## Table 3b — Δ from cooperating (Haiku − RL late)\n")
    rows = []
    for s in SEATS:
        d, se, z = diff_sigma(h["seat_mean"][s], h["seat_sem"][s],
                              l["seat_mean"][s], l["seat_sem"][s])
        rows.append([s, f"{l['seat_mean'][s]:.4f}", f"{h['seat_mean'][s]:.4f}",
                     delta(d, se, z, bold=s in ("prof_1", "prof_3"))])
    d, se, z = diff_sigma(h["mean"], h["sem"], l["mean"], l["sem"])
    rows.append(["average", f"{l['mean']:.4f}", f"{h['mean']:.4f}",
                 f"{d:+.4f} ± {se:.4f} (**{z:+.1f}σ**)"])
    d, se, z = diff_sigma(h["so"], h["so_sem"], l["so"], l["so_sem"])
    rows.append(["social optimality", f"{l['so']:.4f}", f"{h['so']:.4f}",
                 delta(d, se, z)])
    rows.append(["seat spread", f"{l['spread']:.4f}", f"{h['spread']:.4f}",
                 f"{h['spread'] - l['spread']:+.4f}"])
    print(md_table(["seat", "RL late", "Haiku", "Δ from cooperating"],
                   "lrrr", rows))


if __name__ == "__main__":
    main()
