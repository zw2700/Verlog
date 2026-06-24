"""Training-compatible episode JSONL helpers for hiring-env rollouts."""

from __future__ import annotations

import fcntl
import json
import re
from pathlib import Path
from typing import Any

import numpy as np


VOTE_PATTERN = re.compile(r"<VOTE>\s*(\d+)\s*</VOTE>", re.IGNORECASE)
GROUP_PATTERN = re.compile(r"<GROUP>(.*?)</GROUP>", re.DOTALL | re.IGNORECASE)
WAIT_PATTERN = re.compile(r"<WAIT\s*/?>|<WAIT>\s*</WAIT>", re.IGNORECASE)
WAIT_FOR_PATTERN = re.compile(r"<WAIT_FOR>\s*(prof_\d+)\s*</WAIT_FOR>", re.IGNORECASE)
UTILITY_ROW_PATTERN = re.compile(
    r"Student\s+(?P<student>\d+)\s+\|\s+(?P<utility>-?\d+(?:\.\d+)?)\s+\|"
)


def json_safe(obj: Any) -> Any:
    """Convert numpy/scalar objects into JSON-serializable values."""
    if isinstance(obj, dict):
        return {str(k): json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return json_safe(obj.tolist())
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj


def append_jsonl_locked(path: str | Path, row: dict[str, Any]) -> None:
    """Append one JSONL row under a file lock to avoid multi-worker interleaving."""
    log_file = Path(path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(json_safe(row), sort_keys=True) + "\n"
    with log_file.open("a", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write(payload)
            f.flush()
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def extract_action_text(output: str) -> str:
    lower = output.lower()
    idx = lower.rfind("</think>")
    if idx >= 0:
        return output[idx + len("</think>") :].strip()
    return output.strip()


def parse_action_summary(action_text: str) -> dict[str, Any]:
    return {
        "group_messages": [re.sub(r"\s+", " ", x).strip() for x in GROUP_PATTERN.findall(action_text)],
        "votes": VOTE_PATTERN.findall(action_text),
        "wait_count": len(WAIT_PATTERN.findall(action_text)),
        "wait_for": WAIT_FOR_PATTERN.findall(action_text),
    }


def extract_turn_context(messages: list[dict[str, Any]]) -> str:
    """Return only the current observation shown to the acting professor."""
    user_content = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_content = str(msg.get("content", ""))
            break

    if not user_content:
        return "(no user turn context found)"

    marker = "=== YOUR TURN"
    marker_idx = user_content.find(marker)
    if marker_idx >= 0:
        return user_content[marker_idx:].strip()
    return user_content.strip()


def extract_utilities_from_context(turn_context: str) -> dict[str, float]:
    utilities: dict[str, float] = {}
    for match in UTILITY_ROW_PATTERN.finditer(turn_context):
        utilities[str(int(match.group("student")))] = float(match.group("utility"))
    return utilities


def build_episode_turn_entry(
    *,
    timestamp: str,
    env_idx: int,
    global_steps: int,
    epoch: int,
    turn_id: int,
    episode_turn_id: int,
    agent_id: str | None,
    prompt_tokens: int,
    response_tokens: int,
    messages: list[dict[str, Any]],
    output_text: str,
) -> dict[str, Any]:
    turn_context = extract_turn_context(messages)
    action_text = extract_action_text(output_text)
    return {
        "ts": f"{timestamp}Z",
        "epoch": epoch,
        "global_step": global_steps,
        "env": env_idx,
        "turn_id": turn_id,
        "episode_turn_id": episode_turn_id,
        "agent": agent_id,
        "prompt_tokens": prompt_tokens,
        "response_tokens": response_tokens,
        "turn_context": turn_context,
        "output": output_text,
        "action_text": action_text,
        "actions": parse_action_summary(action_text),
        "utilities": extract_utilities_from_context(turn_context),
    }


def build_episode_log_row(
    *,
    epoch: int,
    global_steps: int,
    env_idx: int,
    episode_index: int,
    turns: list[dict[str, Any]],
    reward: Any,
    info: dict[str, Any] | None,
) -> dict[str, Any]:
    info = info or {}
    episode_state = info.get("episode_state") or {}
    episode_metrics = info.get("episode_metrics") or {}
    flat_metrics = info.get("metrics") or {}
    action_validity = episode_metrics.get("action_validity") or {}
    token_accounting = episode_metrics.get("token_accounting") or {}
    social_welfare = episode_metrics.get("social_welfare") or {}
    outcome_quality = episode_metrics.get("outcome_quality") or {}
    negotiation = episode_metrics.get("negotiation_dynamics") or {}

    rank = outcome_quality.get("chosen_student_rank_global")
    consensus = bool(episode_state.get("consensus_reached", False))
    return {
        "schema_version": 1,
        "epoch": epoch,
        "global_step": global_steps,
        "env": env_idx,
        "episode_index": episode_index,
        "episode_uid": f"epoch{epoch}:step{global_steps}:env{env_idx}:episode{episode_index}",
        "partial": False,
        "start_ts": turns[0]["ts"] if turns else None,
        "end_ts": turns[-1]["ts"] if turns else None,
        "consensus": consensus,
        "chosen_student": episode_state.get("consensus_choice") if consensus else None,
        "total_turns": negotiation.get(
            "total_turns",
            sum(int(stats.get("turns", 0)) for stats in (action_validity.get("by_agent") or {}).values()),
        ),
        "tokens_used": token_accounting.get("tokens_used", episode_state.get("tokens_used")),
        "token_budget": token_accounting.get("total_budget", episode_state.get("token_budget")),
        "socially_optimal": bool(rank == 1) if rank is not None else False,
        "chosen_student_rank_global": rank,
        "social_welfare_efficiency": social_welfare.get("efficiency"),
        "actual_total_utility": social_welfare.get("actual_total_utility"),
        "optimal_total_utility": social_welfare.get("optimal_total_utility"),
        "optimal_student": social_welfare.get("optimal_student"),
        "terminal_rewards": reward if isinstance(reward, dict) else {"scalar": reward},
        "agent_rewards": info.get("agent_rewards", {}),
        "student_batch": info.get("student_batch"),
        "professor_interests": info.get("professor_interests"),
        "agent_turn_stats": action_validity.get("by_agent", {}),
        "episode_state": episode_state,
        "episode_metrics": episode_metrics,
        "flat_metrics": flat_metrics,
        "turns": turns,
    }


def append_episode_jsonl_log(
    path: str | Path,
    *,
    epoch: int,
    global_steps: int,
    env_idx: int,
    episode_index: int,
    turns: list[dict[str, Any]],
    reward: Any,
    info: dict[str, Any] | None,
) -> None:
    row = build_episode_log_row(
        epoch=epoch,
        global_steps=global_steps,
        env_idx=env_idx,
        episode_index=episode_index,
        turns=turns,
        reward=reward,
        info=info,
    )
    append_jsonl_locked(path, row)


def format_episode_diagnosis(
    env_idx: int,
    reward: Any,
    info: dict[str, Any] | None,
) -> str:
    """One per-episode reward/error summary block for the game log."""
    by_agent = {}
    consensus_line = ""
    metric_lines = []
    if isinstance(info, dict):
        em = info.get("episode_metrics") or {}
        by_agent = (em.get("action_validity") or {}).get("by_agent") or {}
        est = info.get("episode_state") or {}
        if est.get("consensus_reached"):
            consensus_line = f"consensus: YES -> student {est.get('consensus_choice')}"
        else:
            consensus_line = "consensus: NO"
        sw = em.get("social_welfare") or {}
        oq = em.get("outcome_quality") or {}
        token = em.get("token_accounting") or {}
        negotiation = em.get("negotiation_dynamics") or {}
        chosen_rank = oq.get("chosen_student_rank_global")
        metric_lines.extend(
            [
                f"socially_optimal: {'YES' if chosen_rank == 1 else 'NO'}",
                f"chosen_student_rank_global: {chosen_rank if chosen_rank is not None else 'NA'}",
                f"social_welfare_efficiency: {float(sw.get('efficiency', 0.0)):.3f}",
                f"actual_total_utility: {float(sw.get('actual_total_utility', 0.0)):.3f}",
                f"optimal_total_utility: {float(sw.get('optimal_total_utility', 0.0)):.3f}",
                f"optimal_student: {sw.get('optimal_student', 'NA')}",
                (
                    "tokens_used: "
                    f"{token.get('tokens_used', est.get('tokens_used', 'NA'))}/"
                    f"{token.get('total_budget', est.get('token_budget', 'NA'))}"
                ),
            ]
        )
        if negotiation.get("total_turns") is not None:
            metric_lines.append(f"env_total_turns: {negotiation.get('total_turns')}")

    agent_ids = sorted(by_agent) or (sorted(reward) if isinstance(reward, dict) else [])
    lines = [f"\n=== EPISODE DIAGNOSIS (env={env_idx}) ==="]
    total_turns = 0
    for ag in agent_ids:
        stats = by_agent.get(ag, {})
        turns = int(stats.get("turns", 0))
        r = float(reward.get(ag, 0.0)) if turns > 0 and isinstance(reward, dict) else 0.0
        fmt = int(stats.get("format_errors", 0))
        inv = int(stats.get("invalid_errors", 0))
        total_turns += turns
        fmt_pct = f" ({fmt / turns:.0%})" if turns and fmt else ""
        inv_pct = f" ({inv / turns:.0%})" if turns and inv else ""
        lines.append(
            f"  {ag}: reward={r:+.3f} | turns={turns} | "
            f"format_err={fmt}/{turns}{fmt_pct} | invalid_err={inv}/{turns}{inv_pct}"
        )
    if consensus_line:
        lines.append(f"  {consensus_line}   (total turns: {total_turns})")
    for metric_line in metric_lines:
        lines.append(f"  {metric_line}")
    lines.append(
        "  note: reward is the trainable delivered reward: terminal utility is "
        "shown only for professors with at least one real turn row. Silent "
        "professors have no row to receive utility, so they show reward=0."
    )
    return "\n".join(lines) + "\n"
