#!/usr/bin/env python3
"""Stand-up rate: how often does a responder hold its own favourite against prof_1?

An episode is a *conflict* episode for responder R when prof_1's first vote is
not R's own argmax -- i.e. R actually faces a choice. Within those, R "stands
up" if its own first vote goes to its own argmax, and "caves" if it goes to
prof_1's pick. Anything else (voting for a third student) is excluded.

Rates are broken out by *stakes*: the forgone utility R would give up by
caving, u_R(own argmax) - u_R(prof_1's pick).

The per-episode `turns` list is incomplete in the training logs (not every
turn produces a logged row), so the public transcript is reconstructed from
the `turn_context` field, which carries the full CONVERSATION HISTORY block.

Run from the repo root:
    python3 analysis/v1.6/compute_standup_rates.py
"""

from __future__ import annotations

import glob
import json
import math
import re

from compute_seat_reward_tables import md_table

HIST_RE = re.compile(r"\[(prof_\d) at t=(\d+)\]:\s*(.*)")
GROUP_RE = re.compile(r"<GROUP>(.*?)</GROUP>", re.S)
VOTE_RE = re.compile(r"<VOTE>\s*(\d+)\s*</VOTE>")

RL = ["logs/episode_log_train_auton_17323/*.jsonl"]
HAIKU = ["logs/episode_log_rollout_cmu-gateway_us.anthropic."
         "claude-haiku-4-5-20251001-v1_0_14263_no_all_voted_termination.jsonl"]

ERAS = [
    ("steps 1-10 (early)", RL, (1, 10)),
    ("steps 18-27 (mid)", RL, (18, 27)),
    ("steps 66-75 (late)", RL, (66, 75)),
    ("Haiku 4.5", HAIKU, None),
]
BINS = [(0.0, 0.5), (0.5, 1.0), (1.0, 1.5), (1.5, 99.0)]
SEATS = ("prof_2", "prof_3")


def utilities(row: dict) -> dict[str, dict[int, float]]:
    return {
        prof: {s["index"]: sum(p * v for p, v in zip(pref, s["profile_vector"]))
               for s in row["student_batch"]}
        for prof, pref in row["professor_interests"].items()
    }


def votes_by_agent(row: dict) -> dict[str, list[int]]:
    """First-to-last votes per professor, from the richest turn_context."""
    best = ""
    for turn in row["turns"]:
        ctx = turn.get("turn_context") or ""
        if "CONVERSATION HISTORY" in ctx and len(ctx) > len(best):
            best = ctx
    events: list[tuple[int, str, int]] = []
    if best:
        hist = best.split("CONVERSATION HISTORY", 1)[1]
        hist = hist.split("Your turn (remember", 1)[0]
        for line in hist.splitlines():
            m = HIST_RE.match(line.strip())
            if not m:
                continue
            for v in VOTE_RE.findall(m.group(3)):
                events.append((int(m.group(2)), m.group(1), int(v)))
    # A logged turn may post-date the richest context; append anything new.
    for turn in row["turns"]:
        for v in (turn.get("actions", {}).get("votes") or []):
            try:
                vi = int(v)
            except (TypeError, ValueError):
                continue
            if not any(p == turn["agent"] and x == vi for _, p, x in events):
                events.append((10**6 + turn.get("episode_turn_id", 0),
                               turn["agent"], vi))
    events.sort(key=lambda e: e[0])
    out: dict[str, list[int]] = {}
    for _, prof, v in events:
        out.setdefault(prof, []).append(v)
    return out


def load(paths: list[str], steps: tuple[int, int] | None):
    for pattern in paths:
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
                    yield row


def classify(paths, steps, who: str) -> list[tuple[bool, float]]:
    """(stood_up, forgone) for each conflict episode."""
    out = []
    for row in load(paths, steps):
        v = votes_by_agent(row)
        if "prof_1" not in v or who not in v:
            continue
        p1_first, r_first = v["prof_1"][0], v[who][0]
        u = utilities(row)[who]
        own = max(u, key=lambda s: u[s])
        if p1_first == own:            # no conflict: nothing to decide
            continue
        if r_first == own:
            out.append((True, u[own] - u[p1_first]))
        elif r_first == p1_first:
            out.append((False, u[own] - u[p1_first]))
    return out


def wilson_halfwidth(k: int, n: int) -> float:
    if n == 0:
        return float("nan")
    p, z = k / n, 1.96
    return z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)


def main() -> None:
    for who in SEATS:
        rows = []
        for label, paths, steps in ERAS:
            recs = classify(paths, steps, who)
            if not recs:
                continue
            k, n = sum(up for up, _ in recs), len(recs)
            cells = [label, str(n), f"{k / n:.1%} ±{wilson_halfwidth(k, n) * 100:.1f}"]
            for lo, hi in BINS:
                sub = [up for up, fg in recs if lo <= fg < hi]
                cells.append(f"{sum(sub) / len(sub):.1%} (n={len(sub)})"
                             if len(sub) >= 5 else "n<5")
            rows.append(cells)
        print(f"\n### {who}\n")
        print(md_table(
            ["era", "n conflict", "overall"]
            + [f"fg[{lo:g},{hi:g})" if hi < 99 else "fg[1.5,∞)" for lo, hi in BINS],
            "lrrrrrr", rows,
        ))


if __name__ == "__main__":
    main()
