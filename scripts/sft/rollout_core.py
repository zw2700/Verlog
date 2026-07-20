#!/usr/bin/env python3
"""Shared rollout primitives for the hiring-environment SFT pipeline.

This module intentionally does not decide which trajectories belong in an SFT
dataset.  It runs one fully captured episode and records enough information for
the dataset builder to make that decision later.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import shlex
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from scripts.rollout_frontier import Completion, make_client
from verl.envs import hiring_episode_logging as episode_logging
from verl.envs.hiring_env.env import AsyncTickerAdmissionsEnv

DEFAULT_ENV_CONFIG: dict[str, Any] = {
    "professor_ids": ["prof_1", "prof_2", "prof_3"],
    "students_per_batch": 5,
    "token_budget": 500,
    "feature_dim": 5,
    "vote_threshold": 0.5,
    "max_steps": 50,
    "terminate_on_all_voted_no_consensus": False,
    "professor_preference_mode": "random_permutation",
    "preference_correlation_threshold": 0.0,
    "preference_rejection_max_attempts": 1000,
    "reward_mode": "individual",
    "reward_alpha": 0.5,
    "show_ability_vectors": True,
    "randomize_turn_order": False,
    "utility_mode": "linear",
    "format_penalty": 0.1,
    "invalid_action_penalty": 0.1,
    "prompt_length": 4096,
}

DEFAULT_ENV_CONFIG_PATH = Path(__file__).with_name("configs") / "hiring_v1.json"
DEFAULT_SFT_ENV_PATH = Path(__file__).with_name("sft.env")
TRUNCATION_FINISH_REASONS = {"length", "max_tokens", "max_output_tokens"}
ENV_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def utc_timestamp() -> str:
    """Return the timestamp format expected by hiring_episode_logging."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "")


def canonical_json(value: Any) -> str:
    return json.dumps(episode_logging.json_safe(value), sort_keys=True, separators=(",", ":"))


def env_config_hash(config: dict[str, Any]) -> str:
    """Stable short identifier for a fully resolved environment configuration."""
    return hashlib.sha256(canonical_json(config).encode("utf-8")).hexdigest()[:16]


def make_scenario_id(config_hash: str, scenario_seed: int) -> str:
    return f"{config_hash}:seed{scenario_seed}"


def load_json_object(value: str | Path | None) -> dict[str, Any]:
    if value is None:
        return {}
    path = Path(value).expanduser()
    raw = path.read_text(encoding="utf-8") if path.exists() else str(value)
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("Environment configuration must be a JSON object")
    return parsed


def load_dotenv_file(path: str | Path, *, override: bool = False) -> dict[str, str]:
    """Load a small, shell-compatible KEY=VALUE env file without executing it."""
    env_path = Path(path).expanduser()
    if not env_path.is_file():
        raise FileNotFoundError(env_path)

    loaded: dict[str, str] = {}
    for line_number, raw_line in enumerate(env_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        if "=" not in line:
            raise ValueError(f"Invalid env assignment in {env_path}:{line_number}")
        name, raw_value = line.split("=", 1)
        name = name.strip()
        if not ENV_NAME_PATTERN.fullmatch(name):
            raise ValueError(f"Invalid environment variable name {name!r} in {env_path}:{line_number}")

        raw_value = raw_value.strip()
        if raw_value.startswith(("'", '"')):
            try:
                parts = shlex.split(raw_value, comments=True, posix=True)
            except ValueError as exc:
                raise ValueError(f"Invalid quoted value in {env_path}:{line_number}: {exc}") from exc
            if len(parts) > 1:
                raise ValueError(f"Unexpected text after quoted value in {env_path}:{line_number}")
            value = parts[0] if parts else ""
        else:
            value = re.split(r"\s+#", raw_value, maxsplit=1)[0].strip()

        loaded[name] = value
        if override or name not in os.environ:
            os.environ[name] = value
    return loaded


def bootstrap_env_file(
    *,
    default_path: str | Path | None = DEFAULT_SFT_ENV_PATH,
    argv: list[str] | None = None,
) -> str | None:
    """Load --env-file before constructing CLI defaults from the environment."""
    default = None
    if default_path is not None and Path(default_path).expanduser().is_file():
        default = str(Path(default_path).expanduser())
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--env-file", default=default)
    known, _ = pre_parser.parse_known_args(sys.argv[1:] if argv is None else argv)
    if known.env_file:
        load_dotenv_file(known.env_file)
    return known.env_file


def load_env_config(value: str | Path | None) -> dict[str, Any]:
    """Load an override and merge it onto explicit v1-compatible defaults."""
    config = copy.deepcopy(DEFAULT_ENV_CONFIG)
    config.update(load_json_object(value))
    return config


def load_seed_file(path: str | Path) -> list[int]:
    """Read either a JSON integer list or a newline/comma separated seed file."""
    raw = Path(path).expanduser().read_text(encoding="utf-8").strip()
    if not raw:
        return []
    if raw.startswith("["):
        parsed = json.loads(raw)
        if not isinstance(parsed, list) or not all(isinstance(seed, int) for seed in parsed):
            raise ValueError("Seed JSON must be a list of integers")
        return parsed
    normalized = raw.replace(",", "\n")
    return [int(item.strip()) for item in normalized.splitlines() if item.strip()]


def resolve_seeds(*, seed_base: int, num_scenarios: int, seeds_file: str | Path | None) -> list[int]:
    seeds = load_seed_file(seeds_file) if seeds_file else list(range(seed_base, seed_base + num_scenarios))
    if not seeds:
        raise ValueError("At least one scenario seed is required")
    if len(seeds) != len(set(seeds)):
        raise ValueError("Scenario seeds must be unique")
    return seeds


def flatten_info(info_obj: Any) -> dict[str, Any]:
    if isinstance(info_obj, dict) and info_obj:
        first_value = next(iter(info_obj.values()))
        if isinstance(first_value, dict) and "active_agent" in first_value:
            return first_value
    return info_obj if isinstance(info_obj, dict) else {}


def is_done(terminations: Any, truncations: Any) -> bool:
    terminated = any(terminations.values()) if isinstance(terminations, dict) else bool(terminations)
    truncated = any(truncations.values()) if isinstance(truncations, dict) else bool(truncations)
    return terminated or truncated


def extract_finish_reason(completion: Completion) -> str | None:
    raw = completion.raw
    if not isinstance(raw, dict):
        return None
    if raw.get("stop_reason") is not None:
        return str(raw["stop_reason"])
    choices = raw.get("choices")
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        reason = choices[0].get("finish_reason")
        return str(reason) if reason is not None else None
    return None


def count_chat_tokens(
    tokenizer,
    messages: list[dict[str, Any]],
    *,
    add_generation_prompt: bool,
    enable_thinking: bool,
) -> int:
    """Tokenize a chat while tolerating templates without enable_thinking."""
    kwargs = {
        "tokenize": True,
        "add_generation_prompt": add_generation_prompt,
    }
    try:
        tokens = tokenizer.apply_chat_template(messages, enable_thinking=enable_thinking, **kwargs)
    except (TypeError, ValueError):
        tokens = tokenizer.apply_chat_template(messages, **kwargs)
    if hasattr(tokens, "shape"):
        shape = tuple(tokens.shape)
        return int(shape[-1])
    if tokens and isinstance(tokens[0], list):
        return len(tokens[0])
    return len(tokens)


def _completion_token_counts(completion: Completion, output_text: str, target_tokenizer) -> tuple[int, int]:
    if completion.response_tokens is not None:
        provider_tokens = int(completion.response_tokens)
    else:
        provider_tokens = len(output_text.split())
    target_tokens = len(target_tokenizer.encode(output_text, add_special_tokens=False))
    return provider_tokens, target_tokens


def run_captured_episode(
    *,
    client,
    env_config: dict[str, Any],
    scenario_seed: int,
    attempt: int,
    target_tokenizer,
    target_tokenizer_name: str,
    target_enable_thinking: bool,
    provider_name: str,
    model_name: str,
    temperature: float,
    scenario_index: int = 0,
    include_raw_response: bool = False,
) -> dict[str, Any]:
    """Run one episode with exact per-decision inputs captured in the result."""
    config = copy.deepcopy(env_config)
    config_hash = env_config_hash(config)
    scenario_id = make_scenario_id(config_hash, scenario_seed)
    env = AsyncTickerAdmissionsEnv({**config, "seed": scenario_seed}, tokenizer=target_tokenizer)
    messages, info = env.reset()
    flat_info = flatten_info(info)
    agent_id = flat_info.get("active_agent")

    turns: list[dict[str, Any]] = []
    reward: Any = {}
    done = False
    start_wall = time.time()

    while not done:
        if agent_id is None:
            raise RuntimeError("Environment did not provide an active_agent")

        acting_agent = str(agent_id)
        prompt_was_truncated = bool(env.last_prompt_truncated)
        exact_messages = copy.deepcopy(messages)
        target_prompt_tokens = count_chat_tokens(
            target_tokenizer,
            exact_messages,
            add_generation_prompt=True,
            enable_thinking=target_enable_thinking,
        )
        completion = client.complete(exact_messages)
        output_text = completion.text or ""
        provider_response_tokens, target_response_tokens = _completion_token_counts(
            completion, output_text, target_tokenizer
        )
        prompt_tokens = completion.prompt_tokens
        prompt_token_source = "provider_usage"
        if prompt_tokens is None:
            prompt_tokens = sum(len(str(message.get("content", "")).split()) for message in exact_messages)
            prompt_token_source = "estimated_whitespace"
        response_token_source = "provider_usage" if completion.response_tokens is not None else "estimated_whitespace"
        finish_reason = extract_finish_reason(completion)

        turn = episode_logging.build_episode_turn_entry(
            timestamp=utc_timestamp(),
            env_idx=scenario_index,
            global_steps=0,
            epoch=-1,
            turn_id=len(turns),
            episode_turn_id=len(turns),
            agent_id=acting_agent,
            prompt_tokens=int(prompt_tokens),
            response_tokens=provider_response_tokens,
            messages=exact_messages,
            output_text=output_text,
        )
        turn.update(
            {
                "messages": episode_logging.json_safe(exact_messages),
                "prompt_token_source": prompt_token_source,
                "response_token_source": response_token_source,
                "target_prompt_tokens": target_prompt_tokens,
                "target_response_tokens": target_response_tokens,
                "prompt_was_truncated": prompt_was_truncated,
                "finish_reason": finish_reason,
                "completion_truncated": finish_reason in TRUNCATION_FINISH_REASONS,
            }
        )
        if include_raw_response and completion.raw is not None:
            turn["provider_raw_response"] = completion.raw
        turns.append(turn)

        action: Any
        if completion.vote_metadata is not None:
            action = {acting_agent: {"text": output_text, "metadata": completion.vote_metadata}}
        else:
            action = {acting_agent: output_text}
        messages, reward, terminations, truncations, info = env.step(action)
        flat_info = flatten_info(info)
        agent_id = flat_info.get("active_agent")
        done = is_done(terminations, truncations)

    row = episode_logging.build_episode_log_row(
        epoch=-1,
        global_steps=0,
        env_idx=scenario_index,
        episode_index=attempt,
        turns=turns,
        reward=reward,
        info=flat_info,
    )
    row.update(
        {
            "sft_rollout_schema_version": 1,
            "scenario_seed": scenario_seed,
            "scenario_index": scenario_index,
            "scenario_id": scenario_id,
            "attempt": attempt,
            "episode_uid": f"{scenario_id}:attempt{attempt}",
            "env_config": episode_logging.json_safe(config),
            "env_config_hash": config_hash,
            "provider": provider_name,
            "teacher_model": model_name,
            "teacher_temperature": temperature,
            "target_tokenizer": target_tokenizer_name,
            "target_enable_thinking": target_enable_thinking,
            "elapsed_sec": time.time() - start_wall,
        }
    )
    return row


def action_error_counts(episode: dict[str, Any]) -> tuple[int, int]:
    stats = episode.get("agent_turn_stats") or {}
    if not stats:
        stats = ((episode.get("episode_metrics") or {}).get("action_validity") or {}).get("by_agent") or {}
    format_errors = sum(int((value or {}).get("format_errors", 0)) for value in stats.values())
    invalid_errors = sum(int((value or {}).get("invalid_errors", 0)) for value in stats.values())
    return format_errors, invalid_errors


def is_clean_socially_optimal(episode: dict[str, Any], *, epsilon: float = 1e-6) -> bool:
    """Strict trajectory predicate used for adaptive collection and SFT selection."""
    format_errors, invalid_errors = action_error_counts(episode)
    efficiency = episode.get("social_welfare_efficiency")
    turns = episode.get("turns") or []
    return bool(
        episode.get("consensus")
        and episode.get("socially_optimal")
        and isinstance(efficiency, int | float)
        and float(efficiency) >= 1.0 - epsilon
        and format_errors == 0
        and invalid_errors == 0
        and turns
        and all(str(turn.get("output") or "").strip() for turn in turns)
        and not any(bool(turn.get("completion_truncated")) for turn in turns)
    )


def iter_jsonl(paths: Iterable[str | Path]) -> Iterable[dict[str, Any]]:
    for raw_path in paths:
        path = Path(raw_path).expanduser()
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON in {path}:{line_number}: {exc}") from exc
                if not isinstance(value, dict):
                    raise ValueError(f"Expected JSON object in {path}:{line_number}")
                yield value


def append_jsonl(path: str | Path, row: dict[str, Any]) -> None:
    output = Path(path).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(episode_logging.json_safe(row), sort_keys=True) + "\n")


def wilson_interval(successes: int, total: int, *, z: float = 1.96) -> tuple[float | None, float | None]:
    if total <= 0:
        return None, None
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(proportion * (1 - proportion) / total + z * z / (4 * total * total)) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def add_provider_arguments(parser: argparse.ArgumentParser) -> None:
    provider_default = os.environ.get("PROVIDER")
    model_default = os.environ.get("MODEL")
    parser.add_argument(
        "--provider",
        required=provider_default is None,
        default=provider_default,
        choices=["openai", "anthropic", "openrouter", "cmu-gateway", "local-vllm", "openai-compatible", "fake"],
    )
    parser.add_argument("--model", required=model_default is None, default=model_default)
    parser.add_argument(
        "--env-file",
        default=str(DEFAULT_SFT_ENV_PATH) if DEFAULT_SFT_ENV_PATH.is_file() else None,
        help=(
            "KEY=VALUE file loaded before CLI parsing; process environment and explicit CLI arguments take precedence."
        ),
    )
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--api-key-env", default=None)
    parser.add_argument("--temperature", type=float, default=float(os.environ.get("TEMPERATURE", "1.0")))
    parser.add_argument("--top-p", type=float, default=None)
    parser.add_argument("--max-output-tokens", type=int, default=int(os.environ.get("MAX_OUTPUT_TOKENS", "512")))
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--request-logprobs", action="store_true")
    parser.add_argument("--include-raw-response", action="store_true")
    parser.add_argument("--fake-vote-student", type=int, default=0)
    parser.add_argument("--openrouter-referer", default=None)
    parser.add_argument("--openrouter-title", default="Verlog hiring SFT rollout")


def add_rollout_environment_arguments(parser: argparse.ArgumentParser, *, tokenizer_required: bool = True) -> None:
    parser.add_argument("--env-config", default=str(DEFAULT_ENV_CONFIG_PATH))
    parser.add_argument("--target-tokenizer", required=tokenizer_required, default=None)
    parser.add_argument("--target-tokenizer-trust-remote-code", action="store_true")
    parser.add_argument(
        "--target-enable-thinking",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Chat-template thinking mode for target token accounting; this does not alter the teacher request.",
    )


def load_target_tokenizer(name_or_path: str, *, trust_remote_code: bool = False):
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(name_or_path, trust_remote_code=trust_remote_code)


__all__ = [
    "DEFAULT_ENV_CONFIG",
    "DEFAULT_ENV_CONFIG_PATH",
    "DEFAULT_SFT_ENV_PATH",
    "action_error_counts",
    "add_provider_arguments",
    "add_rollout_environment_arguments",
    "append_jsonl",
    "bootstrap_env_file",
    "count_chat_tokens",
    "env_config_hash",
    "is_clean_socially_optimal",
    "iter_jsonl",
    "load_env_config",
    "load_dotenv_file",
    "load_seed_file",
    "load_target_tokenizer",
    "make_client",
    "make_scenario_id",
    "resolve_seeds",
    "run_captured_episode",
    "wilson_interval",
]
