#!/usr/bin/env python3
"""Probe whether an OpenRouter model can identify the best private-utility student.

This script instantiates the real hiring environment, reuses its chat prompt
builder, asks a model to name the student with maximum utility from the visible
table, and compares the answer against the environment's exact dot-product
utility calculation.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import types
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
HIRING_ENV_PARENT = REPO_ROOT / "verl" / "envs"
if str(HIRING_ENV_PARENT) not in sys.path:
    sys.path.insert(0, str(HIRING_ENV_PARENT))


DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


@dataclass
class TrialResult:
    trial: int
    response_mode: str
    seed: int
    professor: str
    gold_index: int
    gold_ranking: list[int]
    displayed_ranking: list[int]
    predicted_index: int | None
    predicted_ranking: list[int] | None
    correct: bool
    displayed_correct: bool
    parse_ok: bool
    full_ranking_correct: bool | None
    top2_set_correct: bool | None
    exact_pairwise_correct: int | None
    exact_pairwise_total: int | None
    exact_pairwise_accuracy: float | None
    displayed_pairwise_correct: int | None
    displayed_pairwise_total: int | None
    displayed_pairwise_accuracy: float | None
    mean_abs_rank_error: float | None
    gold_utility_exact: float
    predicted_utility_exact: float | None
    utility_regret: float | None
    top_two_gap_exact: float
    displayed_utilities: list[float]
    displayed_gold_indices: list[int]
    exact_utilities: list[float]
    model_content: str
    error: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a small chat-completion probe against the real Verlog hiring env prompt "
            "to test whether a model identifies the highest-utility student."
        )
    )
    parser.add_argument("--trials", type=int, default=10, help="Number of independent env resets to test.")
    parser.add_argument("--model", default="openai/gpt-4o-mini", help="OpenAI-compatible model id.")
    parser.add_argument("--api-key-env", default="OPENROUTER_API_KEY", help="Environment variable holding API key.")
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="OpenAI-compatible API base URL, e.g. http://127.0.0.1:8000/v1 for local vLLM.",
    )
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature.")
    parser.add_argument("--max-tokens", type=int, default=128, help="Maximum response tokens.")
    parser.add_argument("--timeout", type=float, default=60.0, help="HTTP timeout in seconds.")
    parser.add_argument(
        "--disable-thinking",
        action="store_true",
        help=(
            'Pass chat_template_kwargs={"enable_thinking": false} for models whose '
            "chat template otherwise spends completion budget on hidden reasoning."
        ),
    )
    parser.add_argument("--seed", type=int, default=0, help="Base seed. Trial t uses seed + t.")
    parser.add_argument(
        "--professors",
        default="prof_1,prof_2,prof_3",
        help="Comma-separated professor ids to pass to the env.",
    )
    parser.add_argument("--students-per-batch", type=int, default=5, help="Number of students per env batch.")
    parser.add_argument("--feature-dim", type=int, default=5, help="Student ability vector dimension.")
    parser.add_argument("--token-budget", type=int, default=1000, help="Token budget in the env prompt.")
    parser.add_argument("--vote-threshold", type=float, default=0.5, help="Consensus threshold in the env prompt.")
    parser.add_argument("--out-jsonl", type=Path, default=None, help="Optional path to write per-trial JSONL.")
    parser.add_argument(
        "--response-mode",
        choices=["json", "vote", "ranking"],
        default="json",
        help=(
            "Ask for plain JSON top-1, for the env's normal "
            "<THINK>...</THINK><VOTE>N</VOTE> action, or for a full ranking."
        ),
    )
    parser.add_argument(
        "--dump-prompts",
        action="store_true",
        help="Print the diagnostic prompt for each trial before calling OpenRouter.",
    )
    return parser.parse_args()


def load_env_class() -> Any:
    try:
        import gym  # noqa: F401
    except ModuleNotFoundError as exc:
        if exc.name != "gym":
            raise
        sys.modules["gym"] = types.SimpleNamespace(Env=object)

    try:
        from hiring_env.env import AsyncTickerAdmissionsEnv
    except ModuleNotFoundError as exc:
        missing = exc.name or "unknown"
        raise SystemExit(
            f"Missing Python dependency {missing!r}. Run this inside the Verlog training environment "
            "or install the repo dependencies before using the probe."
        ) from exc
    return AsyncTickerAdmissionsEnv


def make_env(args: argparse.Namespace, seed: int, professor_ids: list[str]) -> Any:
    env_cls = load_env_class()
    config = {
        "professor_ids": professor_ids,
        "students_per_batch": args.students_per_batch,
        "token_budget": args.token_budget,
        "feature_dim": args.feature_dim,
        "vote_threshold": args.vote_threshold,
        "seed": seed,
    }
    return env_cls(config)


def exact_utilities(env: Any, professor: str) -> list[float]:
    preference = env.professor_interests[professor]
    return [
        env._calculate_utility_for_student(preference, student["profile_vector"])  # noqa: SLF001
        for student in env.student_batch
    ]


def diagnostic_messages(messages: list[dict[str, str]], response_mode: str) -> list[dict[str, str]]:
    """Preserve the real env messages and append a narrow diagnostic request."""
    if response_mode == "vote":
        content = (
            "DIAGNOSTIC TASK: Act as this professor. Your only goal this turn is to vote for "
            "the student with the highest utility for you, based on the Utility column visible "
            "in the student table above. Follow the environment action format exactly and return "
            "only: <THINK>short private reason</THINK><VOTE>N</VOTE>. Do not wait. Do not send "
            "a group message."
        )
    elif response_mode == "ranking":
        content = (
            "DIAGNOSTIC TASK: Ignore the negotiation action format for this one response. "
            "Using the Utility column visible in the student table above, rank ALL student "
            "indices from highest utility for you to lowest utility for you. Include each "
            "student index exactly once. Return ONLY valid JSON in this exact shape: "
            '{"student_ranking": [0, 1, 2, 3, 4], "reason": "short reason"}'
        )
    else:
        content = (
            "DIAGNOSTIC TASK: Ignore the negotiation action format for this one response. "
            "Using the Utility column visible in the student table above, identify the "
            "student index with the highest utility for you. Return ONLY valid JSON in "
            'this exact shape: {"student_index": 0, "reason": "short reason"}'
        )

    merged_messages = [dict(message) for message in messages]
    merged_messages[-1]["content"] = merged_messages[-1]["content"] + "\n\n" + content
    return merged_messages


def call_chat_api(
    base_url: str,
    api_key: str | None,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    timeout: float,
    disable_thinking: bool = False,
) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if disable_thinking:
        payload["chat_template_kwargs"] = {"enable_thinking": False}
    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if base_url.rstrip("/") == DEFAULT_BASE_URL:
        headers["X-Title"] = "Verlog best-student probe"

    referer = os.environ.get("OPENROUTER_HTTP_REFERER")
    if referer:
        headers["HTTP-Referer"] = referer

    chat_url = base_url.rstrip("/") + "/chat/completions"
    request = urllib.request.Request(
        chat_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Chat API HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Chat API request failed: {exc}") from exc

    data = json.loads(raw)
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected chat API response: {raw}") from exc


def parse_student_index(content: str) -> int | None:
    cleaned = content.strip()
    vote_match = re.search(r"<VOTE>\s*(\d+)\s*</VOTE>", cleaned, re.IGNORECASE)
    if vote_match:
        return int(vote_match.group(1))

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        parsed = json.loads(cleaned)
        value = parsed.get("student_index")
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
    except json.JSONDecodeError:
        pass

    match = re.search(r'"?student_index"?\s*[:=]\s*"?(\d+)"?', cleaned, re.IGNORECASE)
    if match:
        return int(match.group(1))

    match = re.search(r"\bStudent\s+(\d+)\b", cleaned, re.IGNORECASE)
    if match:
        return int(match.group(1))

    numbers = re.findall(r"\b\d+\b", cleaned)
    if len(numbers) == 1:
        return int(numbers[0])

    return None


def strip_code_fence(content: str) -> str:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def normalize_ranking(values: Any, n_students: int) -> list[int] | None:
    if not isinstance(values, list):
        return None

    ranking: list[int] = []
    seen: set[int] = set()
    for value in values:
        if isinstance(value, int):
            index = value
        elif isinstance(value, str) and value.strip().isdigit():
            index = int(value.strip())
        else:
            return None

        if index < 0 or index >= n_students or index in seen:
            return None
        ranking.append(index)
        seen.add(index)

    if len(ranking) != n_students:
        return None
    return ranking


def parse_student_ranking(content: str, n_students: int) -> list[int] | None:
    cleaned = strip_code_fence(content)

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            for key in (
                "student_ranking",
                "ranking",
                "ranked_students",
                "student_indices",
                "students",
                "order",
            ):
                ranking = normalize_ranking(parsed.get(key), n_students)
                if ranking is not None:
                    return ranking
        ranking = normalize_ranking(parsed, n_students)
        if ranking is not None:
            return ranking
    except json.JSONDecodeError:
        pass

    key_match = re.search(
        r"(?:student_ranking|ranking|ranked_students|student_indices|students|order)"
        r'["\']?\s*[:=]\s*\[([^\]]+)\]',
        cleaned,
        re.IGNORECASE,
    )
    if key_match:
        values = re.findall(r"\b\d+\b", key_match.group(1))
        ranking = normalize_ranking(values, n_students)
        if ranking is not None:
            return ranking

    bracket_match = re.search(r"\[([0-9,\s]+)\]", cleaned)
    if bracket_match:
        values = re.findall(r"\b\d+\b", bracket_match.group(1))
        ranking = normalize_ranking(values, n_students)
        if ranking is not None:
            return ranking

    student_mentions = re.findall(r"\bStudent\s+(\d+)\b", cleaned, re.IGNORECASE)
    ranking = normalize_ranking(student_mentions, n_students)
    if ranking is not None:
        return ranking

    return None


def pairwise_order_score(ranking: list[int], utilities: list[float]) -> tuple[int, int, float]:
    position = {student: rank for rank, student in enumerate(ranking)}
    correct = 0
    total = 0
    for left in range(len(utilities)):
        for right in range(left + 1, len(utilities)):
            if utilities[left] == utilities[right]:
                continue
            total += 1
            better, worse = (left, right) if utilities[left] > utilities[right] else (right, left)
            if position[better] < position[worse]:
                correct += 1
    accuracy = correct / total if total else 1.0
    return correct, total, accuracy


def mean_abs_rank_error(predicted_ranking: list[int], gold_ranking: list[int]) -> float:
    predicted_position = {student: rank for rank, student in enumerate(predicted_ranking)}
    gold_position = {student: rank for rank, student in enumerate(gold_ranking)}
    errors = [
        abs(predicted_position[student] - gold_position[student])
        for student in gold_ranking
    ]
    return sum(errors) / len(errors)


def run_trial(
    args: argparse.Namespace,
    api_key: str,
    trial: int,
    seed: int,
    professor_ids: list[str],
) -> TrialResult:
    professor = professor_ids[trial % len(professor_ids)]
    env = make_env(args, seed, professor_ids)
    env.reset()

    messages = env._build_chat_messages(professor)  # noqa: SLF001
    messages = diagnostic_messages(messages, args.response_mode)
    if args.dump_prompts:
        print(f"\n--- trial={trial} seed={seed} professor={professor} prompt ---")
        for message in messages:
            print(f"[{message['role']}]\n{message['content']}\n")

    utilities = exact_utilities(env, professor)
    ranked_indices = sorted(range(len(utilities)), key=lambda index: (-utilities[index], index))
    gold_index = ranked_indices[0]
    gold_utility = utilities[gold_index]
    top_two_gap = gold_utility - utilities[ranked_indices[1]] if len(ranked_indices) > 1 else 0.0
    displayed_utilities = [round(value, 1) for value in utilities]
    displayed_ranking = sorted(range(len(displayed_utilities)), key=lambda index: (-displayed_utilities[index], index))
    displayed_best = max(displayed_utilities)
    displayed_gold_indices = [
        index for index, utility in enumerate(displayed_utilities) if utility == displayed_best
    ]

    try:
        model_content = call_chat_api(
            base_url=args.base_url,
            api_key=api_key,
            model=args.model,
            messages=messages,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            timeout=args.timeout,
            disable_thinking=args.disable_thinking,
        )
        error = None
    except RuntimeError as exc:
        model_content = ""
        error = str(exc)

    predicted_ranking = (
        parse_student_ranking(model_content, len(utilities))
        if model_content and args.response_mode == "ranking"
        else None
    )
    predicted_index = (
        predicted_ranking[0]
        if predicted_ranking
        else parse_student_index(model_content) if model_content else None
    )
    parse_ok = predicted_index is not None and 0 <= predicted_index < len(utilities)
    predicted_utility = utilities[predicted_index] if parse_ok else None
    utility_regret = gold_utility - predicted_utility if predicted_utility is not None else None
    correct = predicted_index == gold_index
    displayed_correct = predicted_index in displayed_gold_indices
    ranking_parse_ok = predicted_ranking is not None
    full_ranking_correct = None
    top2_set_correct = None
    exact_pairwise_correct = None
    exact_pairwise_total = None
    exact_pairwise_accuracy = None
    displayed_pairwise_correct = None
    displayed_pairwise_total = None
    displayed_pairwise_accuracy = None
    rank_error = None
    if ranking_parse_ok:
        full_ranking_correct = predicted_ranking == ranked_indices
        top2_set_correct = set(predicted_ranking[:2]) == set(ranked_indices[:2])
        exact_pairwise_correct, exact_pairwise_total, exact_pairwise_accuracy = pairwise_order_score(
            predicted_ranking,
            utilities,
        )
        displayed_pairwise_correct, displayed_pairwise_total, displayed_pairwise_accuracy = pairwise_order_score(
            predicted_ranking,
            displayed_utilities,
        )
        rank_error = mean_abs_rank_error(predicted_ranking, ranked_indices)

    return TrialResult(
        trial=trial,
        response_mode=args.response_mode,
        seed=seed,
        professor=professor,
        gold_index=gold_index,
        gold_ranking=ranked_indices,
        displayed_ranking=displayed_ranking,
        predicted_index=predicted_index,
        predicted_ranking=predicted_ranking,
        correct=correct,
        displayed_correct=displayed_correct,
        parse_ok=ranking_parse_ok if args.response_mode == "ranking" else parse_ok,
        full_ranking_correct=full_ranking_correct,
        top2_set_correct=top2_set_correct,
        exact_pairwise_correct=exact_pairwise_correct,
        exact_pairwise_total=exact_pairwise_total,
        exact_pairwise_accuracy=exact_pairwise_accuracy,
        displayed_pairwise_correct=displayed_pairwise_correct,
        displayed_pairwise_total=displayed_pairwise_total,
        displayed_pairwise_accuracy=displayed_pairwise_accuracy,
        mean_abs_rank_error=rank_error,
        gold_utility_exact=gold_utility,
        predicted_utility_exact=predicted_utility,
        utility_regret=utility_regret,
        top_two_gap_exact=top_two_gap,
        displayed_utilities=displayed_utilities,
        displayed_gold_indices=displayed_gold_indices,
        exact_utilities=utilities,
        model_content=model_content,
        error=error,
    )


def print_trial(result: TrialResult) -> None:
    status = "OK" if result.correct else "MISS"
    if result.error:
        status = "ERROR"
    elif result.response_mode == "ranking" and not result.parse_ok:
        status = "UNPARSEABLE"
    regret = "n/a" if result.utility_regret is None else f"{result.utility_regret:.4f}"
    if result.response_mode == "ranking":
        pairwise = (
            "n/a"
            if result.exact_pairwise_accuracy is None
            else f"{result.exact_pairwise_accuracy:.3f}"
        )
        print(
            f"[{status}] trial={result.trial:02d} seed={result.seed} professor={result.professor} "
            f"gold_rank={result.gold_ranking} pred_rank={result.predicted_ranking} "
            f"top1_gold={result.gold_index} top1_pred={result.predicted_index} "
            f"regret={regret} pairwise={pairwise} displayed={result.displayed_utilities}"
        )
    else:
        print(
            f"[{status}] trial={result.trial:02d} seed={result.seed} professor={result.professor} "
            f"gold={result.gold_index} pred={result.predicted_index} "
            f"gold_u={result.gold_utility_exact:.4f} regret={regret} "
            f"displayed={result.displayed_utilities} displayed_gold={result.displayed_gold_indices}"
        )
    if result.error:
        print(f"       error: {result.error}")
    elif result.response_mode == "ranking" and not result.parse_ok:
        print(f"       model_content: {result.model_content!r}")
    elif not result.correct:
        print(f"       model_content: {result.model_content!r}")


def summarize(results: list[TrialResult]) -> None:
    completed = [result for result in results if result.error is None]
    parseable = [result for result in completed if result.parse_ok]
    correct = [result for result in completed if result.correct]
    displayed_correct = [result for result in completed if result.displayed_correct]
    regrets = [result.utility_regret for result in parseable if result.utility_regret is not None]
    close_trials = [result for result in completed if result.top_two_gap_exact <= 0.05]
    displayed_ties = [result for result in completed if len(result.displayed_gold_indices) > 1]

    print("\n=== summary ===")
    print(f"completed_calls: {len(completed)}/{len(results)}")
    print(f"parseable_answers: {len(parseable)}/{len(completed) if completed else 0}")
    accuracy_denominator = len(completed) if completed else 1
    print(f"exact_top1_accuracy: {len(correct)}/{len(completed)} = {len(correct) / accuracy_denominator:.3f}")
    print(
        "displayed_table_top_accuracy: "
        f"{len(displayed_correct)}/{len(completed)} = {len(displayed_correct) / accuracy_denominator:.3f}"
    )
    if regrets:
        avg_regret = sum(regrets) / len(regrets)
        max_regret = max(regrets)
        print(f"avg_utility_regret: {avg_regret:.4f}")
        print(f"max_utility_regret: {max_regret:.4f}")
    ranking_results = [result for result in parseable if result.response_mode == "ranking"]
    if ranking_results:
        full_correct = [
            result for result in ranking_results if result.full_ranking_correct
        ]
        top2_correct = [
            result for result in ranking_results if result.top2_set_correct
        ]
        exact_pairwise_correct = sum(result.exact_pairwise_correct or 0 for result in ranking_results)
        exact_pairwise_total = sum(result.exact_pairwise_total or 0 for result in ranking_results)
        displayed_pairwise_correct = sum(result.displayed_pairwise_correct or 0 for result in ranking_results)
        displayed_pairwise_total = sum(result.displayed_pairwise_total or 0 for result in ranking_results)
        rank_errors = [
            result.mean_abs_rank_error
            for result in ranking_results
            if result.mean_abs_rank_error is not None
        ]
        ranking_denominator = len(ranking_results)
        print(
            "full_exact_ranking_accuracy: "
            f"{len(full_correct)}/{ranking_denominator} = {len(full_correct) / ranking_denominator:.3f}"
        )
        print(
            "top2_set_accuracy: "
            f"{len(top2_correct)}/{ranking_denominator} = {len(top2_correct) / ranking_denominator:.3f}"
        )
        if exact_pairwise_total:
            print(
                "exact_pairwise_order_accuracy: "
                f"{exact_pairwise_correct}/{exact_pairwise_total} = "
                f"{exact_pairwise_correct / exact_pairwise_total:.3f}"
            )
        if displayed_pairwise_total:
            print(
                "displayed_pairwise_order_accuracy: "
                f"{displayed_pairwise_correct}/{displayed_pairwise_total} = "
                f"{displayed_pairwise_correct / displayed_pairwise_total:.3f}"
            )
        if rank_errors:
            print(f"mean_abs_rank_error: {sum(rank_errors) / len(rank_errors):.4f}")
    print(f"top_two_gap_le_0.05_trials: {len(close_trials)}/{len(completed)}")
    print(f"displayed_utility_tie_trials: {len(displayed_ties)}/{len(completed)}")


def main() -> None:
    args = parse_args()
    api_key = os.environ.get(args.api_key_env)
    if not api_key and args.base_url.rstrip("/") == DEFAULT_BASE_URL:
        raise SystemExit(f"Missing API key. Set {args.api_key_env}=... before running this script.")

    professor_ids = [prof.strip() for prof in args.professors.split(",") if prof.strip()]
    if not professor_ids:
        raise SystemExit("--professors must contain at least one professor id.")

    if args.out_jsonl:
        args.out_jsonl.parent.mkdir(parents=True, exist_ok=True)

    results: list[TrialResult] = []
    output_file = args.out_jsonl.open("w", encoding="utf-8") if args.out_jsonl else None
    try:
        for trial in range(args.trials):
            seed = args.seed + trial
            result = run_trial(args, api_key, trial, seed, professor_ids)
            results.append(result)
            print_trial(result)
            if output_file is not None:
                output_file.write(json.dumps(asdict(result)) + "\n")
                output_file.flush()
            time.sleep(0.1)
    finally:
        if output_file is not None:
            output_file.close()

    summarize(results)


if __name__ == "__main__":
    main()
