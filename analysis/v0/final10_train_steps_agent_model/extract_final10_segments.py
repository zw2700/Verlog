#!/usr/bin/env python3
"""Extract final-10-training-step episode segments from the agent-model log.

The compact game log only contains env=0, but the agent-model log contains all
32 rollout envs. This script uses timestamp-aligned cluster line bounds for
global_steps 66..75 and segments episodes by per-env reset signatures.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AGENT_LOG = ROOT / "logs/agent_model_train_auton_12993.log"
OUT_DIR = ROOT / "analysis/final10_train_steps_agent_model"

SEGMENTS_JSONL = OUT_DIR / "episode_segments.jsonl"
COMPLETE_SEGMENTS_JSONL = OUT_DIR / "complete_episode_segments.jsonl"
SUMMARY_MD = OUT_DIR / "segmentation_summary.md"
SAMPLE_MD = OUT_DIR / "episode_sample.md"

# Agent-model clusters aligned to game_log global_steps=66..75.
# The final bound is cluster 78 start, intentionally excluded.
STEP_CLUSTER_BOUNDS = [
    {"global_step": 66, "cluster": 68, "start_line": 12887502, "start_ts": "2026-06-16T18:20:37"},
    {"global_step": 67, "cluster": 69, "start_line": 12914247, "start_ts": "2026-06-16T18:29:20"},
    {"global_step": 68, "cluster": 70, "start_line": 12940767, "start_ts": "2026-06-16T18:38:10"},
    {"global_step": 69, "cluster": 71, "start_line": 12967779, "start_ts": "2026-06-16T18:47:20"},
    {"global_step": 70, "cluster": 72, "start_line": 12994339, "start_ts": "2026-06-16T18:56:21"},
    {"global_step": 71, "cluster": 73, "start_line": 13020137, "start_ts": "2026-06-16T19:04:38"},
    {"global_step": 72, "cluster": 74, "start_line": 13045952, "start_ts": "2026-06-16T19:13:00"},
    {"global_step": 73, "cluster": 75, "start_line": 13071599, "start_ts": "2026-06-16T19:20:49"},
    {"global_step": 74, "cluster": 76, "start_line": 13097167, "start_ts": "2026-06-16T19:28:45"},
    {"global_step": 75, "cluster": 77, "start_line": 13122687, "start_ts": "2026-06-16T19:36:42"},
]
SLICE_START = STEP_CLUSTER_BOUNDS[0]["start_line"]
SLICE_END_EXCLUSIVE = 13148261

HEADER_RE = re.compile(
    r"^=== (?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z "
    r"env=(?P<env>\d+) turn=(?P<turn>\d+) agent=(?P<agent>prof_\d+) "
    r"prompt_tokens=(?P<prompt_tokens>\d+) response_tokens=(?P<response_tokens>\d+) ===$"
)
GROUP_RE = re.compile(r"<GROUP>(.*?)</GROUP>", re.S | re.I)
VOTE_RE = re.compile(r"<VOTE>\s*([0-4])\s*</VOTE>", re.I)
WAIT_RE = re.compile(r"<WAIT>", re.I)
WAIT_FOR_RE = re.compile(r"<WAIT_FOR>\s*(prof_\d+)\s*</WAIT_FOR>", re.I)
UTILITY_ROW_RE = re.compile(
    r"Student\s+(?P<student>\d)\s+\|\s+(?P<utility>-?\d+(?:\.\d+)?)\s+\|"
)


def global_step_for_line(line_no: int) -> int | None:
    for index, item in enumerate(STEP_CLUSTER_BOUNDS):
        start = item["start_line"]
        end = (
            STEP_CLUSTER_BOUNDS[index + 1]["start_line"]
            if index + 1 < len(STEP_CLUSTER_BOUNDS)
            else SLICE_END_EXCLUSIVE
        )
        if start <= line_no < end:
            return int(item["global_step"])
    return None


def normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_output(block: str) -> str:
    marker = "[OUTPUT]"
    idx = block.find(marker)
    if idx < 0:
        return ""
    return block[idx + len(marker) :].strip().replace("<|im_end|>", "").strip()


def extract_action_text(output: str) -> str:
    """Return the part of output where executable action tags should appear."""
    lower = output.lower()
    idx = lower.rfind("</think>")
    if idx >= 0:
        return output[idx + len("</think>") :].strip()
    return output


def parse_turns() -> list[dict]:
    turns: list[dict] = []
    current: dict | None = None
    buf: list[str] = []

    with AGENT_LOG.open(errors="replace") as f:
        for line_no, line in enumerate(f, 1):
            if line_no < SLICE_START:
                continue
            if line_no >= SLICE_END_EXCLUSIVE:
                break

            match = HEADER_RE.match(line.rstrip("\n"))
            if match:
                if current is not None:
                    current["block"] = "".join(buf)
                    turns.append(current)
                current = {
                    "line": line_no,
                    "ts": match.group("ts"),
                    "env": int(match.group("env")),
                    "turn": int(match.group("turn")),
                    "agent": match.group("agent"),
                    "prompt_tokens": int(match.group("prompt_tokens")),
                    "response_tokens": int(match.group("response_tokens")),
                    "global_step": global_step_for_line(line_no),
                }
                buf = []
            elif current is not None:
                buf.append(line)

    if current is not None:
        current["block"] = "".join(buf)
        turns.append(current)

    for turn in turns:
        block = turn["block"]
        output = extract_output(block)
        action_text = extract_action_text(output)
        turn["output"] = output
        turn["action_text"] = action_text
        turn["group_messages"] = [normalize_ws(x) for x in GROUP_RE.findall(action_text)]
        turn["votes"] = VOTE_RE.findall(action_text)
        turn["wait_count"] = len(WAIT_RE.findall(action_text))
        turn["wait_for"] = WAIT_FOR_RE.findall(action_text)
        turn["is_reset_start"] = (
            "=== YOUR TURN (t=0) ===" in block
            and "CONVERSATION HISTORY (chronological by ticker time):\n(No messages yet)" in block
            and "CURRENT VOTES:" not in block
        )
        utilities = {}
        for row in UTILITY_ROW_RE.finditer(block):
            utilities[int(row.group("student"))] = float(row.group("utility"))
        turn["utilities"] = utilities

    return turns


def make_segments(turns: list[dict]) -> list[dict]:
    by_env: dict[int, list[dict]] = defaultdict(list)
    for turn in turns:
        by_env[turn["env"]].append(turn)

    segments: list[dict] = []
    segment_id = 1

    for env in sorted(by_env):
        env_turns = by_env[env]
        reset_indices = [i for i, turn in enumerate(env_turns) if turn["is_reset_start"]]

        if reset_indices and reset_indices[0] > 0:
            left_turns = env_turns[: reset_indices[0]]
            segments.append(build_segment(segment_id, env, "left_continuation_fragment", left_turns))
            segment_id += 1
        elif not reset_indices:
            segments.append(build_segment(segment_id, env, "unbounded_env_fragment", env_turns))
            segment_id += 1
            continue

        for idx, start_idx in enumerate(reset_indices):
            end_idx = reset_indices[idx + 1] if idx + 1 < len(reset_indices) else len(env_turns)
            kind = "complete_bounded" if idx + 1 < len(reset_indices) else "right_trailing_fragment"
            segments.append(build_segment(segment_id, env, kind, env_turns[start_idx:end_idx]))
            segment_id += 1

    return sorted(segments, key=lambda row: (row["start_line"], row["env"], row["segment_id"]))


def build_segment(segment_id: int, env: int, boundary_type: str, turns: list[dict]) -> dict:
    output_turns = []
    for turn in turns:
        output_turns.append(
            {
                "line": turn["line"],
                "ts": turn["ts"],
                "global_step": turn["global_step"],
                "env": turn["env"],
                "turn": turn["turn"],
                "agent": turn["agent"],
                "output": turn["output"],
                "action_text": turn["action_text"],
                "group_messages": turn["group_messages"],
                "votes": turn["votes"],
                "wait_count": turn["wait_count"],
                "wait_for": turn["wait_for"],
                "utilities": turn["utilities"],
            }
        )

    public_messages = [msg for turn in output_turns for msg in turn["group_messages"]]
    votes = [(turn["agent"], vote) for turn in output_turns for vote in turn["votes"]]
    wait_count = sum(turn["wait_count"] for turn in output_turns)
    wait_for_count = sum(len(turn["wait_for"]) for turn in output_turns)

    return {
        "segment_id": segment_id,
        "env": env,
        "boundary_type": boundary_type,
        "start_line": turns[0]["line"],
        "end_line": turns[-1]["line"],
        "start_ts": turns[0]["ts"],
        "end_ts": turns[-1]["ts"],
        "start_global_step": turns[0]["global_step"],
        "end_global_step": turns[-1]["global_step"],
        "turn_count": len(turns),
        "public_message_count": len(public_messages),
        "vote_count": len(votes),
        "wait_count": wait_count,
        "wait_for_count": wait_for_count,
        "agents_seen": sorted({turn["agent"] for turn in output_turns}),
        "public_messages": public_messages,
        "votes": votes,
        "turns": output_turns,
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def write_complete_segments(segments: list[dict]) -> list[dict]:
    complete = [row for row in segments if row["boundary_type"] == "complete_bounded"]
    complete = sorted(complete, key=lambda row: (row["start_line"], row["env"], row["segment_id"]))
    rows = []
    for index, row in enumerate(complete, 1):
        enriched = dict(row)
        enriched["complete_episode_id"] = index
        final_votes = {}
        for agent, vote in row["votes"]:
            final_votes[agent] = int(vote)
        vote_counts = Counter(final_votes.values())
        chosen = None
        if vote_counts:
            student, count = vote_counts.most_common(1)[0]
            if count >= 2:
                chosen = int(student)
        enriched["final_votes"] = final_votes
        enriched["consensus"] = chosen is not None
        enriched["chosen_student"] = chosen
        all_agents = {"prof_1", "prof_2", "prof_3"}
        utility_agents = {
            turn["agent"]
            for turn in row["turns"]
            if len(turn.get("utilities", {})) == 5
        }
        enriched["full_utility_matrix_visible"] = all_agents.issubset(utility_agents)
        rows.append(enriched)
    write_jsonl(COMPLETE_SEGMENTS_JSONL, rows)
    return rows


def make_summary(turns: list[dict], segments: list[dict]) -> None:
    boundary_counts = Counter(row["boundary_type"] for row in segments)
    complete = [row for row in segments if row["boundary_type"] == "complete_bounded"]
    by_step = Counter(row["start_global_step"] for row in complete)
    turn_by_step = Counter(turn["global_step"] for turn in turns)
    consensus_count = 0
    no_consensus_count = 0
    for row in complete:
        final_votes = {}
        for agent, vote in row["votes"]:
            final_votes[agent] = int(vote)
        vote_counts = Counter(final_votes.values())
        has_consensus = bool(vote_counts and vote_counts.most_common(1)[0][1] >= 2)
        consensus_count += int(has_consensus)
        no_consensus_count += int(not has_consensus)

    lines = [
        "# Final 10 Training Steps Agent-Model Segmentation",
        "",
        "## Scope",
        "",
        "- Source: `logs/agent_model_train_auton_12993.log`",
        "- Training steps: `global_steps=66..75` inferred by timestamp alignment to `game_log_train_auton_12993.log`",
        f"- Agent-model line slice: `{SLICE_START}..{SLICE_END_EXCLUSIVE - 1}`",
        "- Excludes trailing cluster 78, which starts at line `13148261` and has no matching `game_log` training-step marker.",
        "",
        "## Counts",
        "",
        f"- Turn records: `{len(turns)}`",
        f"- Total segments: `{len(segments)}`",
        f"- Complete bounded episodes: `{boundary_counts['complete_bounded']}`",
        f"- Complete episodes with inferred consensus: `{consensus_count}`",
        f"- Complete episodes without inferred consensus: `{no_consensus_count}`",
        f"- Left continuation fragments: `{boundary_counts['left_continuation_fragment']}`",
        f"- Right trailing fragments: `{boundary_counts['right_trailing_fragment']}`",
        f"- Unbounded env fragments: `{boundary_counts['unbounded_env_fragment']}`",
        "",
        "## Complete Episodes By Start Step",
        "",
        "| Global step | Complete episodes starting in step | Turn records in step |",
        "|---:|---:|---:|",
    ]
    for step in range(66, 76):
        lines.append(f"| {step} | {by_step[step]} | {turn_by_step[step]} |")

    lines.extend(
        [
            "",
            "## Segmentation Rule",
            "",
            "An episode start is inferred from a turn block with all of:",
            "",
            "- `=== YOUR TURN (t=0) ===`",
            "- `CONVERSATION HISTORY ... (No messages yet)`",
            "- no `CURRENT VOTES:` block",
            "",
            "A complete bounded episode is a start followed by another start in the same env within the slice.",
            "The final started episode in each env is marked as `right_trailing_fragment` because it may continue after the slice.",
            "Turns before the first start in an env are marked as `left_continuation_fragment` because the episode began before global step 66.",
        ]
    )

    SUMMARY_MD.write_text("\n".join(lines))


def make_sample(segments: list[dict]) -> None:
    complete = [row for row in segments if row["boundary_type"] == "complete_bounded"]
    sample = (
        complete[:5]
        + complete[len(complete) // 2 : len(complete) // 2 + 5]
        + complete[-5:]
    )
    seen = set()
    unique_sample = []
    for row in sample:
        if row["segment_id"] not in seen:
            unique_sample.append(row)
            seen.add(row["segment_id"])

    lines = ["# Episode Segment Sample", ""]
    for row in unique_sample:
        lines.append(f"## Segment {row['segment_id']} env={row['env']} lines={row['start_line']}-{row['end_line']}")
        lines.append("")
        lines.append(
            f"- Boundary: `{row['boundary_type']}`; step `{row['start_global_step']}` to `{row['end_global_step']}`; "
            f"turns `{row['turn_count']}`; messages `{row['public_message_count']}`; votes `{row['vote_count']}`"
        )
        for turn in row["turns"][:6]:
            one_line = normalize_ws(turn["output"])
            if len(one_line) > 350:
                one_line = one_line[:347] + "..."
            lines.append(f"- `{turn['agent']}` line `{turn['line']}`: {one_line}")
        if len(row["turns"]) > 6:
            lines.append(f"- ... {len(row['turns']) - 6} more turns")
        lines.append("")
    SAMPLE_MD.write_text("\n".join(lines))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    turns = parse_turns()
    segments = make_segments(turns)
    write_jsonl(SEGMENTS_JSONL, segments)
    complete_rows = write_complete_segments(segments)
    make_summary(turns, segments)
    make_sample(segments)

    counts = Counter(row["boundary_type"] for row in segments)
    print(f"turn records: {len(turns)}")
    print(f"segments: {len(segments)}")
    for key, value in counts.most_common():
        print(f"{key}: {value}")
    print(f"wrote {SEGMENTS_JSONL}")
    print(f"wrote {COMPLETE_SEGMENTS_JSONL} ({len(complete_rows)} complete episodes)")
    print(f"wrote {SUMMARY_MD}")
    print(f"wrote {SAMPLE_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
