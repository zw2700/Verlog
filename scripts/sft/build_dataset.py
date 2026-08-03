#!/usr/bin/env python3
"""Select clean teacher trajectories and build decision-level SFT Parquet files."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from scripts.sft.rollout_core import (
    action_error_counts,
    count_chat_tokens,
    is_clean_socially_optimal,
    iter_jsonl,
    load_seed_file,
    load_target_tokenizer,
)
from verl.envs import hiring_episode_logging as episode_logging

# Qwen occasionally emits the unambiguous opening-tag typo <_THINK> while
# still closing with </THINK>. Accept that typo for compact-target recovery;
# compact_teacher_output always emits the canonical <THINK> spelling.
THINK_PATTERN = re.compile(r"<_?THINK>(.*?)</THINK>", re.DOTALL | re.IGNORECASE)
STUDENT_PATTERN = re.compile(r"\bstudent\s+(\d+)\b", re.IGNORECASE)
VOTE_PATTERN = re.compile(r"<VOTE>\s*(\d+)\s*</VOTE>", re.IGNORECASE)
META_THOUGHT_PATTERN = re.compile(
    r"^(?:"
    r"let me (?:analy[sz]e|review|think|consider)|"
    r"i (?:need|should) to (?:analy[sz]e|review|think|consider)|"
    r"i should (?:keep (?:this|it) concise|be concise)|"
    r"(?:now|next),? i(?:'ll| will) (?:respond|act)|"
    r"time to (?:respond|act)|"
    r"the (?:best|pragmatic|strategic) (?:move|choice) is\s*$"
    r")",
    re.IGNORECASE,
)
ACTION_RELEVANCE_PATTERN = re.compile(
    r"\b(?:vote|switch|hold|stick|stay|propose|support|advocate|recommend|favor|choose|select|"
    r"consensus|compromise|coordinate|persuade|ask|message|wait|hear|listen)\w*\b",
    re.IGNORECASE,
)
RATIONALE_PATTERN = re.compile(
    r"\b(?:because|since|therefore|thus|so|best|highest|utility|welfare|"
    r"strong|balanced|broad|versatile|pragmatic|guarantee|risk|outcome)\w*\b",
    re.IGNORECASE,
)


class DatasetBuildError(ValueError):
    """A trajectory cannot safely be represented in the requested SFT dataset."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", nargs="+", required=True, help="JSONL files or directories containing JSONL files")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--target-tokenizer", required=True)
    parser.add_argument("--target-tokenizer-trust-remote-code", action="store_true")
    parser.add_argument("--target-enable-thinking", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--target-format", choices=["raw", "compact-think"], default="raw")
    parser.add_argument("--max-think-tokens", type=int, default=64)
    parser.add_argument("--max-prompt-tokens", type=int, default=4096)
    parser.add_argument("--max-response-tokens", type=int, default=512)
    parser.add_argument("--max-sequence-tokens", type=int, default=4608)
    parser.add_argument("--validation-fraction", type=float, default=0.1)
    parser.add_argument("--validation-seeds-file", default=None)
    parser.add_argument("--split-seed", type=int, default=1)
    parser.add_argument(
        "--selected-scenario-count",
        type=int,
        default=None,
        help=(
            "Require and deterministically select exactly this many clean scenarios. "
            "Useful for size-matched teacher comparisons."
        ),
    )
    parser.add_argument(
        "--selection-seed",
        type=int,
        default=1,
        help="Hash-ranking seed used only when --selected-scenario-count truncates clean scenarios.",
    )
    parser.add_argument("--allow-mixed-env-configs", action="store_true")
    return parser.parse_args()


def discover_jsonl_paths(inputs: Iterable[str | Path]) -> list[Path]:
    paths: list[Path] = []
    for value in inputs:
        path = Path(value).expanduser()
        if path.is_dir():
            paths.extend(sorted(candidate for candidate in path.rglob("*.jsonl") if candidate.is_file()))
        elif path.is_file():
            paths.append(path)
        else:
            raise FileNotFoundError(path)
    unique = sorted(set(paths))
    if not unique:
        raise ValueError("No JSONL input files found")
    return unique


def scenario_key(episode: dict[str, Any]) -> str:
    scenario_id = episode.get("scenario_id")
    if scenario_id:
        return str(scenario_id)
    config_hash = episode.get("env_config_hash")
    seed = episode.get("scenario_seed")
    if config_hash is None or not isinstance(seed, int):
        raise DatasetBuildError("Episode lacks scenario_id or env_config_hash/scenario_seed")
    return f"{config_hash}:seed{seed}"


def episode_sort_key(episode: dict[str, Any]) -> tuple[int, int, int, int]:
    return (
        len(episode.get("turns") or []),
        int(episode.get("tokens_used") or 0),
        int(episode.get("llm_output_tokens") or 0),
        int(episode.get("attempt") or 0),
    )


def select_exact_scenario_count(
    selected: list[tuple[dict[str, Any], list[dict[str, Any]]]],
    *,
    count: int | None,
    selection_seed: int,
) -> list[tuple[dict[str, Any], list[dict[str, Any]]]]:
    """Return a deterministic exact-size subset of already validated scenarios."""
    if count is None:
        return selected
    if count <= 0:
        raise ValueError("selected scenario count must be positive")
    if len(selected) < count:
        raise ValueError(f"Only {len(selected)} clean dataset-valid scenarios are available; need {count}")
    ranked = sorted(
        selected,
        key=lambda item: hashlib.sha256(
            f"{selection_seed}:{scenario_key(item[0])}".encode("utf-8")
        ).digest(),
    )
    return ranked[:count]


def _thought_sentences(thought: str) -> list[str]:
    """Split prose and bullet-style reasoning without retaining list markers."""
    thought = re.sub(r"(?m)^\s*\d+[.)]\s+.*$", "", thought)
    pieces = re.split(r"(?<=[.!?])\s+|\n+", thought)
    sentences: list[str] = []
    for piece in pieces:
        # Numbered strategy menus describe alternatives, not the eventual
        # action; selecting one line in isolation can reverse the decision.
        if re.match(r"^\s*\d+[.)]\s*", piece):
            continue
        cleaned = re.sub(r"^\s*(?:[-*•]+|\d+[.)])\s*", "", piece).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        if not cleaned or cleaned in {"<THINK>", "</THINK>"}:
            continue
        # Bare headings and bookkeeping fragments are poor supervision targets.
        if cleaned.endswith(":") or len(cleaned.split()) < 3:
            continue
        sentences.append(cleaned)
    return sentences


def _target_students(action_text: str) -> set[str]:
    votes = set(VOTE_PATTERN.findall(action_text))
    return votes or set(STUDENT_PATTERN.findall(action_text))


def _action_alignment_score(sentence: str, action_text: str) -> int:
    score = 0
    if VOTE_PATTERN.search(action_text) and re.search(
        r"\b(?:vote|switch|hold|stick|stay|choose|select|support|favor)\w*\b", sentence, re.IGNORECASE
    ):
        score += 3
    if re.search(r"<GROUP>", action_text, re.IGNORECASE) and re.search(
        r"\b(?:propose|advocate|recommend|persuade|message|ask|discuss|invite)\w*\b", sentence, re.IGNORECASE
    ):
        score += 3
    if re.search(r"<WAIT(?:_FOR)?>|<WAIT\s*/?>", action_text, re.IGNORECASE) and re.search(
        r"\b(?:wait|hear|listen)\w*\b", sentence, re.IGNORECASE
    ):
        score += 5
    wait_for = re.search(r"<WAIT_FOR>\s*(prof_\d+)\s*</WAIT_FOR>", action_text, re.IGNORECASE)
    if wait_for and wait_for.group(1).lower() in sentence.lower():
        score += 2
    return score


def _sentence_score(sentence: str, *, target_students: set[str], action_text: str) -> int:
    if META_THOUGHT_PATTERN.search(sentence):
        return -100
    mentioned = set(STUDENT_PATTERN.findall(sentence))
    score = 0
    if mentioned & target_students:
        score += 8
        score -= 2 * len(mentioned - target_students)
    elif mentioned:
        score += 1
        if target_students:
            score -= 6
    if ACTION_RELEVANCE_PATTERN.search(sentence):
        score += 4
    if RATIONALE_PATTERN.search(sentence):
        score += 2
    if re.search(r"\b(?:i|i(?:'ll| will)|we|let me)\b", sentence, re.IGNORECASE):
        score += 1
    score += _action_alignment_score(sentence, action_text)
    return score


def _token_count(tokenizer, text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))


def _fallback_compact_thought(action_text: str) -> str:
    vote = VOTE_PATTERN.search(action_text)
    if vote:
        return f"I will vote for Student {vote.group(1)}."
    students = STUDENT_PATTERN.findall(action_text)
    if students:
        return f"I will propose Student {students[0]} and invite consensus."
    if re.search(r"<WAIT_FOR>|<WAIT\s*/?>", action_text, re.IGNORECASE):
        return "I will wait for more information before deciding."
    return "I will take the concise valid action shown below."


def _fit_complete_candidate(sentence: str, tokenizer, *, max_tokens: int) -> str | None:
    """Fit at a sentence or clause boundary; never retain an arbitrary token tail."""
    if _token_count(tokenizer, sentence) <= max_tokens:
        return sentence
    clauses = re.split(r"(?<=[;:])\s+|\s+[—–]\s+|,\s+(?=(?:but|so|because|which|while|and)\b)", sentence)
    prefix: list[str] = []
    for clause in clauses:
        candidate = " ".join(prefix + [clause]).strip()
        if _token_count(tokenizer, candidate) > max_tokens:
            break
        prefix.append(clause)
    if not prefix:
        return None
    fitted = " ".join(prefix).strip().rstrip(",;:")
    if fitted and fitted[-1] not in ".!?":
        fitted += "."
    return fitted if _token_count(tokenizer, fitted) <= max_tokens else None


def compact_teacher_output(output: str, tokenizer, *, max_think_tokens: int) -> str:
    """Keep one or two action-relevant rationales and the original action text.

    Only the final complete THINK block is considered. The recoverable opening
    typo <_THINK> is canonicalized, but incomplete blocks remain invalid. This
    avoids concatenating malformed retries or earlier scratch work.
    """
    if max_think_tokens <= 0:
        raise DatasetBuildError("max_think_tokens must be positive")
    matches = list(THINK_PATTERN.finditer(output or ""))
    if not matches:
        raise DatasetBuildError("compact-think target has no complete THINK block")
    action_text = episode_logging.extract_action_text(output)
    if not action_text:
        raise DatasetBuildError("compact-think target has no action after THINK")

    thought = matches[-1].group(1).strip()
    target_students = _target_students(action_text)
    ranked = sorted(
        enumerate(_thought_sentences(thought)),
        key=lambda item: (
            _sentence_score(item[1], target_students=target_students, action_text=action_text),
            item[0],
        ),
        reverse=True,
    )
    selected: list[tuple[int, str]] = []
    for index, sentence in ranked:
        score = _sentence_score(sentence, target_students=target_students, action_text=action_text)
        if score < 4:
            continue
        fitted = _fit_complete_candidate(sentence, tokenizer, max_tokens=max_think_tokens)
        if fitted is None:
            continue
        if selected:
            primary = selected[0][1]
            needs_action = not ACTION_RELEVANCE_PATTERN.search(primary)
            needs_rationale = not RATIONALE_PATTERN.search(primary)
            supplies_missing_piece = (needs_action and ACTION_RELEVANCE_PATTERN.search(fitted)) or (
                needs_rationale and RATIONALE_PATTERN.search(fitted)
            )
            if not supplies_missing_piece:
                continue
        trial = " ".join(text for _, text in sorted(selected + [(index, fitted)]))
        if _token_count(tokenizer, trial) <= max_think_tokens:
            selected.append((index, fitted))
        if len(selected) == 2 or (
            selected
            and ACTION_RELEVANCE_PATTERN.search(selected[0][1])
            and RATIONALE_PATTERN.search(selected[0][1])
        ):
            break

    if selected:
        compact_thought = " ".join(text for _, text in sorted(selected))
    else:
        fallback = _fallback_compact_thought(action_text)
        compact_thought = _fit_complete_candidate(fallback, tokenizer, max_tokens=max_think_tokens)
        if compact_thought is None:
            raise DatasetBuildError("max_think_tokens is too small for a coherent compact target")
    return f"<THINK>{compact_thought}</THINK>\n{action_text}"


def _exact_prompt_messages(turn: dict[str, Any]) -> list[dict[str, Any]]:
    messages = turn.get("messages")
    if not isinstance(messages, list) or not messages:
        raise DatasetBuildError("turn lacks exact captured messages")
    copied = [copy.deepcopy(message) for message in messages]
    if not all(isinstance(message, dict) and message.get("role") in {"system", "user"} for message in copied):
        raise DatasetBuildError("captured prompt must contain only system/user messages")
    if copied[-1].get("role") != "user":
        raise DatasetBuildError("captured prompt does not end with a user message")
    return copied


def build_decision_rows(
    episode: dict[str, Any],
    tokenizer,
    *,
    target_format: str,
    max_think_tokens: int,
    max_prompt_tokens: int,
    max_response_tokens: int,
    max_sequence_tokens: int,
    target_enable_thinking: bool,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for turn_index, turn in enumerate(episode.get("turns") or []):
        prompt_messages = _exact_prompt_messages(turn)
        raw_output = str(turn.get("output") or "").strip()
        if not raw_output:
            raise DatasetBuildError(f"turn {turn_index} has empty output")
        if target_format == "raw":
            target_output = raw_output
        elif target_format == "compact-think":
            target_output = compact_teacher_output(raw_output, tokenizer, max_think_tokens=max_think_tokens)
        else:
            raise DatasetBuildError(f"Unknown target format: {target_format}")

        prompt_tokens = count_chat_tokens(
            tokenizer,
            prompt_messages,
            add_generation_prompt=True,
            enable_thinking=target_enable_thinking,
        )
        response_tokens = len(tokenizer.encode(target_output, add_special_tokens=False))
        full_messages = prompt_messages + [{"role": "assistant", "content": target_output}]
        sequence_tokens = count_chat_tokens(
            tokenizer,
            full_messages,
            add_generation_prompt=False,
            enable_thinking=target_enable_thinking,
        )
        if prompt_tokens > max_prompt_tokens:
            raise DatasetBuildError(f"turn {turn_index} prompt has {prompt_tokens} > {max_prompt_tokens} tokens")
        if response_tokens > max_response_tokens:
            raise DatasetBuildError(f"turn {turn_index} response has {response_tokens} > {max_response_tokens} tokens")
        if sequence_tokens > max_sequence_tokens:
            raise DatasetBuildError(f"turn {turn_index} sequence has {sequence_tokens} > {max_sequence_tokens} tokens")

        rows.append(
            {
                "messages": full_messages,
                "enable_thinking": target_enable_thinking,
                "scenario_id": scenario_key(episode),
                "scenario_seed": int(episode["scenario_seed"]),
                "episode_uid": str(episode.get("episode_uid") or ""),
                "attempt": int(episode.get("attempt") or 0),
                "turn_index": int(turn.get("episode_turn_id", turn_index)),
                "agent": str(turn.get("agent") or ""),
                "target_format": target_format,
                "prompt_tokens": prompt_tokens,
                "response_tokens": response_tokens,
                "sequence_tokens": sequence_tokens,
                "social_welfare_efficiency": float(episode.get("social_welfare_efficiency") or 0.0),
                "llm_turns_in_episode": len(episode.get("turns") or []),
                "public_tokens_in_episode": int(episode.get("tokens_used") or 0),
                "teacher_model": str(episode.get("teacher_model") or ""),
                "env_config_hash": str(episode.get("env_config_hash") or ""),
                "teacher_action_text": str(turn.get("action_text") or ""),
            }
        )
    if not rows:
        raise DatasetBuildError("episode has no turns")
    return rows


def rejection_reasons(episode: dict[str, Any]) -> list[str]:
    reasons = []
    if not episode.get("consensus"):
        reasons.append("no_consensus")
    if not episode.get("socially_optimal"):
        reasons.append("not_socially_optimal")
    efficiency = episode.get("social_welfare_efficiency")
    if not isinstance(efficiency, int | float) or float(efficiency) < 1.0 - 1e-6:
        reasons.append("suboptimal_efficiency")
    format_errors, invalid_errors = action_error_counts(episode)
    if format_errors:
        reasons.append("format_error")
    if invalid_errors:
        reasons.append("invalid_action")
    turns = episode.get("turns") or []
    if not turns:
        reasons.append("no_turns")
    if any(bool(turn.get("completion_truncated")) for turn in turns):
        reasons.append("truncated_completion")
    if any(not str(turn.get("output") or "").strip() for turn in turns):
        reasons.append("empty_output")
    return reasons


def choose_validation_scenarios(
    selected: list[tuple[dict[str, Any], list[dict[str, Any]]]],
    *,
    validation_fraction: float,
    validation_seeds: set[int] | None,
    split_seed: int,
) -> set[str]:
    """Choose a deterministic scenario-level validation split.

    An explicit seed file is authoritative.  For a fractional split, select an
    exact number of scenarios by hash rank so small pilots still get a useful,
    nonempty validation split without separating turns from the same episode.
    """
    if validation_seeds is not None:
        return {scenario_key(episode) for episode, _ in selected if int(episode["scenario_seed"]) in validation_seeds}
    if validation_fraction <= 0 or len(selected) < 2:
        return set()

    validation_count = round(validation_fraction * len(selected))
    validation_count = max(1, min(validation_count, len(selected) - 1))

    def split_rank(item: tuple[dict[str, Any], list[dict[str, Any]]]) -> bytes:
        episode, _ = item
        return hashlib.sha256(f"{split_seed}:{scenario_key(episode)}".encode()).digest()

    ranked = sorted(selected, key=split_rank)
    return {scenario_key(episode) for episode, _ in ranked[:validation_count]}


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> None:
    args = parse_args()
    if not 0 <= args.validation_fraction < 1:
        raise SystemExit("--validation-fraction must be in [0, 1)")
    if min(args.max_prompt_tokens, args.max_response_tokens, args.max_sequence_tokens) <= 0:
        raise SystemExit("Token limits must be positive")

    input_paths = discover_jsonl_paths(args.input)
    episodes = list(iter_jsonl(input_paths))
    if not episodes:
        raise SystemExit("No episodes found")
    config_hashes = {str(episode.get("env_config_hash")) for episode in episodes}
    if len(config_hashes) > 1 and not args.allow_mixed_env_configs:
        raise SystemExit(f"Input contains multiple environment configs: {sorted(config_hashes)}")
    target_tokenizers = {str(episode.get("target_tokenizer")) for episode in episodes}
    if len(target_tokenizers) > 1:
        raise SystemExit(f"Input contains multiple target tokenizers: {sorted(target_tokenizers)}")
    if target_tokenizers != {args.target_tokenizer}:
        raise SystemExit(
            f"Input was collected for target tokenizer(s) {sorted(target_tokenizers)}, "
            f"but --target-tokenizer is {args.target_tokenizer!r}"
        )

    tokenizer = load_target_tokenizer(
        args.target_tokenizer,
        trust_remote_code=args.target_tokenizer_trust_remote_code,
    )
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    rejection_counts: Counter[str] = Counter()
    for episode in episodes:
        try:
            grouped[scenario_key(episode)].append(episode)
        except DatasetBuildError:
            rejection_counts["missing_scenario_identity"] += 1

    selected: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
    scenario_failures: Counter[str] = Counter()
    for key, candidates in sorted(grouped.items()):
        clean_candidates = []
        for episode in candidates:
            reasons = rejection_reasons(episode)
            rejection_counts.update(reasons)
            if is_clean_socially_optimal(episode):
                clean_candidates.append(episode)
        if not clean_candidates:
            scenario_failures["no_clean_socially_optimal_attempt"] += 1
            continue
        for episode in sorted(clean_candidates, key=episode_sort_key):
            try:
                rows = build_decision_rows(
                    episode,
                    tokenizer,
                    target_format=args.target_format,
                    max_think_tokens=args.max_think_tokens,
                    max_prompt_tokens=args.max_prompt_tokens,
                    max_response_tokens=args.max_response_tokens,
                    max_sequence_tokens=args.max_sequence_tokens,
                    target_enable_thinking=args.target_enable_thinking,
                )
            except DatasetBuildError as exc:
                rejection_counts[f"dataset_validation:{exc}"] += 1
                continue
            selected.append((episode, rows))
            break
        else:
            scenario_failures["all_clean_attempts_failed_dataset_validation"] += 1

    if not selected:
        raise SystemExit("No scenarios produced valid SFT rows")

    eligible_clean_scenarios = len(selected)
    try:
        selected = select_exact_scenario_count(
            selected,
            count=args.selected_scenario_count,
            selection_seed=args.selection_seed,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    validation_seeds = set(load_seed_file(args.validation_seeds_file)) if args.validation_seeds_file else None
    validation_scenarios = choose_validation_scenarios(
        selected,
        validation_fraction=args.validation_fraction,
        validation_seeds=validation_seeds,
        split_seed=args.split_seed,
    )
    train_rows: list[dict[str, Any]] = []
    validation_rows: list[dict[str, Any]] = []
    selected_manifest = []
    for episode, rows in selected:
        is_validation = scenario_key(episode) in validation_scenarios
        split = "validation" if is_validation else "train"
        (validation_rows if is_validation else train_rows).extend(rows)
        selected_manifest.append(
            {
                "scenario_id": scenario_key(episode),
                "scenario_seed": int(episode["scenario_seed"]),
                "episode_uid": episode.get("episode_uid"),
                "attempt": int(episode.get("attempt") or 0),
                "split": split,
                "decision_rows": len(rows),
                "llm_turns": len(episode.get("turns") or []),
                "tokens_used": int(episode.get("tokens_used") or 0),
            }
        )

    if not train_rows:
        raise SystemExit("Scenario-level split produced no training rows")
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    train_frame = pd.DataFrame(train_rows)
    validation_frame = pd.DataFrame(validation_rows, columns=train_frame.columns)
    train_frame.to_parquet(output_dir / "train.parquet", index=False)
    validation_frame.to_parquet(output_dir / "validation.parquet", index=False)
    write_jsonl(output_dir / "selected_episodes.jsonl", selected_manifest)

    all_rows = train_rows + validation_rows
    report = {
        "input_files": [str(path) for path in input_paths],
        "input_attempts": len(episodes),
        "input_scenarios": len(grouped),
        "eligible_clean_scenarios": eligible_clean_scenarios,
        "selected_scenarios": len(selected),
        "requested_selected_scenarios": args.selected_scenario_count,
        "selection_seed": args.selection_seed,
        "train_scenarios": sum(item["split"] == "train" for item in selected_manifest),
        "validation_scenarios": sum(item["split"] == "validation" for item in selected_manifest),
        "train_decision_rows": len(train_rows),
        "validation_decision_rows": len(validation_rows),
        "target_format": args.target_format,
        "target_tokenizer": args.target_tokenizer,
        "target_enable_thinking": args.target_enable_thinking,
        "env_config_hashes": sorted(config_hashes),
        "rejection_counts": dict(sorted(rejection_counts.items())),
        "scenario_failure_counts": dict(sorted(scenario_failures.items())),
        "agent_counts": dict(sorted(Counter(row["agent"] for row in all_rows).items())),
        "prompt_tokens": _numeric_summary(row["prompt_tokens"] for row in all_rows),
        "response_tokens": _numeric_summary(row["response_tokens"] for row in all_rows),
        "sequence_tokens": _numeric_summary(row["sequence_tokens"] for row in all_rows),
    }
    (output_dir / "dataset_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))


def _numeric_summary(values: Iterable[int | float]) -> dict[str, float | int | None]:
    numbers = sorted(float(value) for value in values)
    if not numbers:
        return {"count": 0, "min": None, "mean": None, "p50": None, "p90": None, "p99": None, "max": None}

    def percentile(fraction: float) -> float:
        index = min(round(fraction * (len(numbers) - 1)), len(numbers) - 1)
        return numbers[index]

    return {
        "count": len(numbers),
        "min": numbers[0],
        "mean": sum(numbers) / len(numbers),
        "p50": percentile(0.50),
        "p90": percentile(0.90),
        "p99": percentile(0.99),
        "max": numbers[-1],
    }


if __name__ == "__main__":
    main()
