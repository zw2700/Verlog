#!/usr/bin/env python3
"""Run hiring-env rollouts against frontier/API models.

This runner bypasses PPO but uses the same AsyncTickerAdmissionsEnv and the
same episode JSONL row builder as training rollouts.
"""

from __future__ import annotations

import argparse
import fcntl
import importlib.metadata
import json
import os
import random
import re
import subprocess
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from verl.envs import hiring_episode_logging as episode_logging
from verl.envs.hiring_env.env import AsyncTickerAdmissionsEnv

DEFAULT_ENV_CONFIG = {
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
}


@dataclass
class Completion:
    text: str
    prompt_tokens: int | None = None
    response_tokens: int | None = None
    raw: dict[str, Any] | None = None
    vote_metadata: dict[str, Any] | None = None
    reasoning_text: str | None = None
    reasoning_format: str | None = None
    finish_reason: str | None = None
    visible_action_missing: bool = False


class ProviderError(RuntimeError):
    pass


REASONING_MODES = ("manual-tags", "native-thinking")
VISIBLE_ACTION_TAGS = ("<GROUP>", "<VOTE>", "<WAIT>", "<WAIT_FOR>")
ENV_RESET_LOCK = threading.Lock()


def adapt_messages_for_reasoning_mode(
    messages: list[dict[str, str]], reasoning_mode: str
) -> list[dict[str, str]]:
    """Return the exact messages to send for the selected reasoning mode."""
    if reasoning_mode == "manual-tags":
        return messages
    if reasoning_mode != "native-thinking":
        raise ValueError(f"Unsupported reasoning mode: {reasoning_mode}")

    replacements = (
        (
            "Every turn must begin with <THINK>...</THINK> private reasoning, followed by your action tag(s).",
            "Use model-native private reasoning, then emit only the visible action tag(s).",
        ),
        (
            "  <THINK>your reasoning</THINK><GROUP>I propose student 2</GROUP>"
            "<VOTE>2</VOTE><WAIT_FOR>prof_name</WAIT_FOR>",
            "  <GROUP>I propose student 2</GROUP><VOTE>2</VOTE><WAIT_FOR>prof_name</WAIT_FOR>",
        ),
        (
            "- <THINK> tokens do NOT count against the shared token budget.",
            "- Model-native private reasoning does NOT count against the shared token budget.",
        ),
        (
            "- <THINK> tokens DO count against your personal ticker time (turn order).",
            "- The visible action advances ticker time; native private reasoning is handled by the model runtime.",
        ),
        (
            "- <THINK> content is PRIVATE — only you can see your own thoughts in your history.",
            "- Model-native reasoning is PRIVATE and is not shown to other professors.",
        ),
        (
            "- Other professors' <THINK> blocks are NEVER shown to you.",
            "- Other professors' private reasoning is NEVER shown to you.",
        ),
        ("- Always output <THINK>...</THINK> before your action.\n", ""),
        ("- Always close your <THINK> tag with </THINK> before starting your action tag.\n", ""),
        (
            "- Format: <THINK>reasoning</THINK><ACTION_TAG>content</ACTION_TAG>",
            "- After reasoning privately, output only recognized visible action tags.",
        ),
        (
            "- Keep <THINK> reasoning concise - aim for 3 sentences or less to organize your "
            "thoughts efficiently. You don't want to take up too much space, or your message "
            "history will get truncated in the future.",
            "- Keep model-native private reasoning focused so there is room for a visible action.",
        ),
        (
            "  Example: <THINK>Student 2 is best.</THINK><VOTE>2</VOTE>",
            "  Example: <VOTE>2</VOTE>",
        ),
        (
            "- Use <THINK> for private reasoning before each action, but be concise.",
            "- Reason privately using the model's native thinking mode before choosing a visible action.",
        ),
        (
            "(only <GROUP> messages consume budget; <THINK> is free)",
            "(only <GROUP> messages consume budget; native private reasoning is not shared)",
        ),
        (
            "Your turn (remember: start with <THINK>your reasoning</THINK>, then your action):",
            "Your turn: reason privately, then output only your visible action tag(s):",
        ),
    )

    adapted: list[dict[str, str]] = []
    for message in messages:
        updated = str(message.get("content", ""))
        for old, new in replacements:
            updated = updated.replace(old, new)
        if re.search(r"</?THINK>", updated, flags=re.IGNORECASE):
            raise ProviderError(
                "Native-thinking prompt adaptation left a literal THINK tag; "
                "the environment prompt likely changed and the adapter needs review"
            )
        adapted.append({**message, "content": updated})

    system_text = "\n".join(
        message["content"] for message in adapted if message.get("role") == "system"
    )
    missing_tags = [tag for tag in VISIBLE_ACTION_TAGS if tag not in system_text]
    if missing_tags:
        raise ProviderError(f"Native prompt adaptation lost visible action tags: {missing_tags}")
    return adapted


def chat_template_kwargs_for_mode(reasoning_mode: str) -> dict[str, bool]:
    if reasoning_mode not in REASONING_MODES:
        raise ValueError(f"Unsupported reasoning mode: {reasoning_mode}")
    return {"enable_thinking": reasoning_mode == "native-thinking"}


def _extract_reasoning_and_visible_content(
    message: dict[str, Any],
    content: str,
    *,
    strip_embedded_reasoning: bool,
) -> tuple[str, str | None, str | None]:
    """Separate private reasoning from content that may be sent to the environment.

    Some OpenAI-compatible servers expose reasoning in a dedicated field. vLLM
    0.10 instead returns Qwen3 reasoning inside ``message.content``. In native
    mode, including that text in the environment action leaks it into history
    and can exhaust the model context. An unclosed block means generation ended
    before a visible action, so the safe visible content is the prefix only.
    """
    for key in ("reasoning_content", "reasoning"):
        value = message.get(key)
        if value:
            return content, str(value), "separated"

    closed = re.search(r"<think>(.*?)</think>", content, flags=re.DOTALL | re.IGNORECASE)
    if closed:
        reasoning = closed.group(1).strip()
        visible = content
        if strip_embedded_reasoning:
            visible = (content[: closed.start()] + content[closed.end() :]).strip()
        return visible, reasoning, "embedded"

    opened = re.search(r"<think>", content, flags=re.IGNORECASE)
    if opened and strip_embedded_reasoning:
        visible = content[: opened.start()].strip()
        reasoning = content[opened.end() :].strip()
        return visible, reasoning, "embedded-unclosed"

    return content, None, None


def _http_json(
    url: str,
    *,
    headers: dict[str, str],
    payload: dict[str, Any],
    timeout: float,
    max_retries: int,
) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        req = urllib.request.Request(
            url,
            data=data,
            headers={**headers, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_error = ProviderError(f"HTTP {exc.code} from {url}: {body[:1000]}")
            if exc.code not in {408, 409, 429, 500, 502, 503, 504}:
                break
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
        if attempt < max_retries:
            time.sleep(min(30.0, 2.0**attempt + random.random()))
    raise ProviderError(str(last_error))


def _env_key(name: str, explicit_value: str | None) -> str:
    if explicit_value:
        return explicit_value
    value = os.environ.get(name)
    if not value:
        raise ProviderError(f"Missing API key. Set {name} or pass --api-key-env.")
    return value


def _env_key_or_default(name: str, explicit_value: str | None, default: str) -> str:
    if explicit_value:
        return explicit_value
    return os.environ.get(name) or default


def _json_env(name: str) -> dict[str, Any]:
    value = os.environ.get(name)
    if not value:
        return {}
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ProviderError(f"{name} must be a JSON object")
    return parsed


def _extract_text_logprob_vote_metadata(
    output_text: str,
    content_logprobs: list[dict[str, Any]] | None,
) -> dict[str, Any] | None:
    """Best-effort vote metadata from OpenAI-compatible token logprobs."""
    if not content_logprobs:
        return None
    match = episode_logging.VOTE_PATTERN.search(output_text or "")
    if not match:
        return None
    digit_start = match.start(1)
    cursor = 0
    chosen_item = None
    for item in content_logprobs:
        token = str(item.get("token", ""))
        next_cursor = cursor + len(token)
        if cursor <= digit_start < max(next_cursor, cursor + 1):
            chosen_item = item
            break
        cursor = next_cursor
    if chosen_item is None:
        return None
    alternatives = []
    for alt in chosen_item.get("top_logprobs") or []:
        alternatives.append((str(alt.get("token", "")), float(alt.get("logprob", 0.0))))
    return {
        "vote_alternatives": alternatives or None,
        "vote_chosen_token": str(chosen_item.get("token", "")),
        "vote_chosen_logprob": (
            float(chosen_item["logprob"]) if chosen_item.get("logprob") is not None else None
        ),
    }


class BaseClient:
    def complete(self, messages: list[dict[str, str]]) -> Completion:
        raise NotImplementedError


class OpenAICompatibleClient(BaseClient):
    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        base_url: str,
        temperature: float,
        max_tokens: int,
        timeout: float,
        max_retries: int,
        top_p: float | None,
        request_logprobs: bool,
        token_limit_field: str = "max_tokens",
        extra_headers: dict[str, str] | None = None,
        extra_body: dict[str, Any] | None = None,
        strip_embedded_reasoning: bool = False,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self.top_p = top_p
        self.request_logprobs = request_logprobs
        self.token_limit_field = token_limit_field
        self.extra_headers = extra_headers or {}
        self.extra_body = extra_body or {}
        self.strip_embedded_reasoning = strip_embedded_reasoning

    def complete(self, messages: list[dict[str, str]]) -> Completion:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        payload[self.token_limit_field] = self.max_tokens
        if self.top_p is not None:
            payload["top_p"] = self.top_p
        if self.request_logprobs:
            payload["logprobs"] = True
            payload["top_logprobs"] = 20
        payload.update(self.extra_body)

        raw = _http_json(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", **self.extra_headers},
            payload=payload,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )
        choices = raw.get("choices") or []
        if not choices:
            raise ProviderError(f"No choices in OpenAI-compatible response: {raw}")
        choice = choices[0]
        message = choice.get("message") or {}
        raw_content = message.get("content") or ""
        text, reasoning_text, reasoning_format = _extract_reasoning_and_visible_content(
            message,
            raw_content,
            strip_embedded_reasoning=self.strip_embedded_reasoning,
        )
        usage = raw.get("usage") or {}
        content_logprobs = ((choice.get("logprobs") or {}).get("content")) if isinstance(choice, dict) else None
        return Completion(
            text=text,
            prompt_tokens=usage.get("prompt_tokens"),
            response_tokens=usage.get("completion_tokens"),
            raw=raw,
            vote_metadata=_extract_text_logprob_vote_metadata(text, content_logprobs),
            reasoning_text=reasoning_text,
            reasoning_format=reasoning_format,
            finish_reason=choice.get("finish_reason"),
            visible_action_missing=not text.strip(),
        )


class AnthropicClient(BaseClient):
    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        base_url: str,
        temperature: float,
        max_tokens: int,
        timeout: float,
        max_retries: int,
        top_p: float | None,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self.top_p = top_p

    @staticmethod
    def _convert_messages(messages: list[dict[str, str]]) -> tuple[str | None, list[dict[str, str]]]:
        system_parts = []
        converted = []
        for message in messages:
            role = message.get("role")
            content = str(message.get("content", ""))
            if role == "system":
                system_parts.append(content)
            elif role in {"user", "assistant"}:
                converted.append({"role": role, "content": content})
        return ("\n\n".join(system_parts) if system_parts else None), converted

    def complete(self, messages: list[dict[str, str]]) -> Completion:
        system, anthropic_messages = self._convert_messages(messages)
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": anthropic_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if system:
            payload["system"] = system
        if self.top_p is not None:
            payload["top_p"] = self.top_p

        raw = _http_json(
            f"{self.base_url}/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
            payload=payload,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )
        text_parts = [
            str(block.get("text", ""))
            for block in raw.get("content", [])
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        usage = raw.get("usage") or {}
        return Completion(
            text="".join(text_parts),
            prompt_tokens=usage.get("input_tokens"),
            response_tokens=usage.get("output_tokens"),
            raw=raw,
            vote_metadata=None,
            finish_reason=raw.get("stop_reason"),
            visible_action_missing=not any(part.strip() for part in text_parts),
        )


class FakeVoteClient(BaseClient):
    def __init__(self, student: int = 0, reasoning_mode: str = "manual-tags") -> None:
        self.student = student
        self.reasoning_mode = reasoning_mode

    def complete(self, messages: list[dict[str, str]]) -> Completion:
        reasoning = "I will cast a simple vote for smoke testing."
        if self.reasoning_mode == "native-thinking":
            text = f"<VOTE>{self.student}</VOTE>"
            reasoning_format = "separated"
        else:
            text = f"<THINK>{reasoning}</THINK>\n<VOTE>{self.student}</VOTE>"
            reasoning_format = "embedded"
        prompt_tokens = sum(len(str(message.get("content", "")).split()) for message in messages)
        return Completion(
            text=text,
            prompt_tokens=prompt_tokens,
            response_tokens=len(text.split()),
            raw={"provider": "fake", "student": self.student},
            vote_metadata=None,
            reasoning_text=reasoning,
            reasoning_format=reasoning_format,
            finish_reason="stop",
        )


def make_client(args: argparse.Namespace) -> BaseClient:
    if args.provider == "fake":
        return FakeVoteClient(student=args.fake_vote_student, reasoning_mode=args.reasoning_mode)

    if args.provider == "anthropic":
        return AnthropicClient(
            model=args.model,
            api_key=_env_key(args.api_key_env or "ANTHROPIC_API_KEY", None),
            base_url=args.base_url or "https://api.anthropic.com/v1",
            temperature=args.temperature,
            max_tokens=args.max_output_tokens,
            timeout=args.timeout,
            max_retries=args.max_retries,
            # Anthropic rejects some models when both temperature and top_p are
            # specified. Keep temperature for training-run comparability and
            # omit top_p so the provider default applies.
            top_p=None,
        )

    if args.provider == "openrouter":
        extra_headers = {}
        if args.openrouter_referer:
            extra_headers["HTTP-Referer"] = args.openrouter_referer
        if args.openrouter_title:
            extra_headers["X-Title"] = args.openrouter_title
        return OpenAICompatibleClient(
            model=args.model,
            api_key=_env_key(args.api_key_env or "OPENROUTER_API_KEY", None),
            base_url=args.base_url or "https://openrouter.ai/api/v1",
            temperature=args.temperature,
            max_tokens=args.max_output_tokens,
            timeout=args.timeout,
            max_retries=args.max_retries,
            top_p=args.top_p,
            request_logprobs=args.request_logprobs,
            token_limit_field="max_tokens",
            extra_headers=extra_headers,
        )

    if args.provider == "openai":
        return OpenAICompatibleClient(
            model=args.model,
            api_key=_env_key(args.api_key_env or "OPENAI_API_KEY", None),
            base_url=args.base_url or "https://api.openai.com/v1",
            temperature=args.temperature,
            max_tokens=args.max_output_tokens,
            timeout=args.timeout,
            max_retries=args.max_retries,
            top_p=args.top_p,
            request_logprobs=args.request_logprobs,
            token_limit_field="max_completion_tokens",
        )

    if args.provider == "cmu-gateway":
        return OpenAICompatibleClient(
            model=args.model,
            api_key=_env_key(args.api_key_env or "CMU_GATEWAY_API_KEY", None),
            base_url=args.base_url or "https://ai-gateway.andrew.cmu.edu/v1",
            temperature=args.temperature,
            max_tokens=args.max_output_tokens,
            timeout=args.timeout,
            max_retries=args.max_retries,
            top_p=args.top_p,
            request_logprobs=args.request_logprobs,
            token_limit_field="max_tokens",
        )

    if args.provider == "local-vllm":
        extra_body = _json_env("LOCAL_VLLM_EXTRA_BODY_JSON")
        chat_template_kwargs = dict(extra_body.get("chat_template_kwargs") or {})
        chat_template_kwargs.update(chat_template_kwargs_for_mode(args.reasoning_mode))
        extra_body["chat_template_kwargs"] = chat_template_kwargs
        return OpenAICompatibleClient(
            model=args.model,
            api_key=_env_key_or_default(args.api_key_env or "LOCAL_VLLM_API_KEY", None, "dummy"),
            base_url=args.base_url or os.environ.get("LOCAL_VLLM_BASE_URL") or "http://127.0.0.1:8000/v1",
            temperature=args.temperature,
            max_tokens=args.max_output_tokens,
            timeout=args.timeout,
            max_retries=args.max_retries,
            top_p=args.top_p,
            request_logprobs=args.request_logprobs,
            token_limit_field="max_tokens",
            extra_body=extra_body,
            strip_embedded_reasoning=args.reasoning_mode == "native-thinking",
        )

    if args.provider == "openai-compatible":
        if not args.base_url:
            raise ProviderError("--base-url is required for --provider openai-compatible")
        key_name = args.api_key_env or "OPENAI_API_KEY"
        return OpenAICompatibleClient(
            model=args.model,
            api_key=_env_key(key_name, None),
            base_url=args.base_url,
            temperature=args.temperature,
            max_tokens=args.max_output_tokens,
            timeout=args.timeout,
            max_retries=args.max_retries,
            top_p=args.top_p,
            request_logprobs=args.request_logprobs,
            token_limit_field="max_tokens",
        )

    raise ProviderError(f"Unsupported provider: {args.provider}")


def flatten_info(info_obj: Any) -> dict[str, Any]:
    if isinstance(info_obj, dict) and info_obj:
        first_val = next(iter(info_obj.values()))
        if isinstance(first_val, dict) and "active_agent" in first_val:
            return first_val
    return info_obj if isinstance(info_obj, dict) else {}


def is_done(terminations: Any, truncations: Any) -> bool:
    term = any(terminations.values()) if isinstance(terminations, dict) else bool(terminations)
    trunc = any(truncations.values()) if isinstance(truncations, dict) else bool(truncations)
    return term or trunc


def load_env_config(args: argparse.Namespace) -> dict[str, Any]:
    config = dict(DEFAULT_ENV_CONFIG)
    config.update(
        {
            "students_per_batch": args.students_per_batch,
            "token_budget": args.token_budget,
            "feature_dim": args.feature_dim,
            "vote_threshold": args.vote_threshold,
            "max_steps": args.max_steps,
            "prompt_length": args.prompt_length,
        }
    )
    if args.max_prompt_words is not None:
        config["max_prompt_words"] = args.max_prompt_words
    if args.terminate_on_all_voted_no_consensus is not None:
        config["terminate_on_all_voted_no_consensus"] = args.terminate_on_all_voted_no_consensus
    if args.reward_mode is not None:
        config["reward_mode"] = args.reward_mode
    if args.reward_alpha is not None:
        config["reward_alpha"] = args.reward_alpha
    if args.show_ability_vectors is not None:
        config["show_ability_vectors"] = args.show_ability_vectors
    if args.randomize_turn_order:
        config["randomize_turn_order"] = True
    if args.utility_mode is not None:
        config["utility_mode"] = args.utility_mode
    if args.professor_preference_mode is not None:
        config["professor_preference_mode"] = args.professor_preference_mode
    if args.preference_correlation_threshold is not None:
        config["preference_correlation_threshold"] = args.preference_correlation_threshold
    if args.preference_rejection_max_attempts is not None:
        config["preference_rejection_max_attempts"] = args.preference_rejection_max_attempts
    if args.env_config_json:
        path = Path(args.env_config_json)
        overrides = json.loads(path.read_text()) if path.exists() else json.loads(args.env_config_json)
        config.update(overrides)
    return config


def _command_output(args: list[str]) -> str | None:
    try:
        return subprocess.run(
            args,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def _package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def write_metadata(path: str | Path | None, metadata: dict[str, Any]) -> None:
    if not path:
        return
    metadata_path = Path(path)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = metadata_path.with_suffix(metadata_path.suffix + ".tmp")
    temporary.write_text(json.dumps(episode_logging.json_safe(metadata), indent=2, sort_keys=True) + "\n")
    temporary.replace(metadata_path)


def build_run_metadata(
    args: argparse.Namespace,
    env_config: dict[str, Any],
    *,
    start_ts: str,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "status": "running",
        "cell_name": args.cell_name,
        "provider": args.provider,
        "model": args.model,
        "requested_model_revision": args.model_revision,
        "resolved_model_revision": args.model_revision,
        "reasoning_mode": args.reasoning_mode,
        "chat_template_kwargs": chat_template_kwargs_for_mode(args.reasoning_mode),
        "temperature": args.temperature,
        "top_p": args.top_p,
        "max_output_tokens": args.max_output_tokens,
        "seed_base": args.seed_base,
        "episode_seeds": [args.seed_base + i for i in range(args.num_episodes)],
        "num_episodes": args.num_episodes,
        "num_envs": args.num_envs,
        "episode_workers": args.episode_workers,
        "environment_config": env_config,
        "artifacts": {
            "episode_jsonl": str(Path(args.out_jsonl).resolve()),
            "game_log": str(Path(args.game_log).resolve()) if args.game_log else None,
            "metadata_json": str(Path(args.metadata_json).resolve()) if args.metadata_json else None,
        },
        "git": {
            "branch": _command_output(["git", "branch", "--show-current"]),
            "commit": _command_output(["git", "rev-parse", "HEAD"]),
            "dirty": bool(_command_output(["git", "status", "--short"])),
        },
        "runtime": {
            "vllm_version": _package_version("vllm"),
            "vllm_max_model_len": os.environ.get("VLLM_MAX_MODEL_LEN"),
            "python": os.sys.version.split()[0],
        },
        "start_timestamp": start_ts,
        "end_timestamp": None,
    }


def write_game_log(
    path: str | Path | None,
    *,
    episode_header: str,
    turn_blocks: list[str],
    env_idx: int,
    reward: Any,
    final_info: dict[str, Any],
) -> None:
    if not path:
        return
    log_file = Path(path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        episode_header
        + "".join(turn_blocks)
        + episode_logging.format_episode_diagnosis(env_idx, reward, final_info)
    )
    with log_file.open("a", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write(payload)
            f.flush()
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def write_game_log_prompt_header(path: str | Path | None, system_prompts: dict[str, str]) -> None:
    if not path:
        return
    log_file = Path(path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().isoformat(timespec="seconds")
    lines = [
        "",
        "=" * 70,
        f"=== GAME LOG RUN PROMPTS {timestamp}Z ===",
        "=" * 70,
        "System prompts logged once for this rollout process. Per-turn entries below log only "
        "the dynamic turn context.",
        "",
    ]
    for agent_id in sorted(system_prompts):
        lines.append(f"--- SYSTEM PROMPT agent={agent_id} ---")
        lines.append(str(system_prompts[agent_id]))
        lines.append("")
    log_file.write_text("\n".join(lines), encoding="utf-8")


def reset_seeded_env(
    env_config: dict[str, Any], seed: int
) -> tuple[AsyncTickerAdmissionsEnv, list[dict[str, str]], dict[str, Any]]:
    """Create/reset an env atomically around its process-global NumPy RNG."""
    with ENV_RESET_LOCK:
        env = AsyncTickerAdmissionsEnv({**env_config, "seed": seed})
        messages, info = env.reset()
    return env, messages, info


def run_episode(
    *,
    client: BaseClient,
    env_config: dict[str, Any],
    seed: int,
    env_idx: int,
    episode_index: int,
    epoch: int,
    global_steps: int,
    out_jsonl: str | Path,
    game_log: str | Path | None,
    provider_name: str,
    model_name: str,
    reasoning_mode: str,
    cell_name: str | None,
    include_raw_response: bool,
    include_reasoning_text: bool,
) -> dict[str, Any]:
    # Provider calls remain concurrent, but env reset must be seed-safe.
    env, messages, info = reset_seeded_env(env_config, seed)
    flat_info = flatten_info(info)
    agent_id = flat_info.get("active_agent")

    turns: list[dict[str, Any]] = []
    game_blocks: list[str] = []
    reward: Any = {}
    done = False
    turn_id = 0
    start_wall = time.time()

    while not done:
        acting_agent = agent_id
        if acting_agent is None:
            raise RuntimeError("Environment did not provide an active_agent")

        request_messages = adapt_messages_for_reasoning_mode(messages, reasoning_mode)
        completion = client.complete(request_messages)
        output_text = completion.text or ""
        now = datetime.utcnow().isoformat(timespec="seconds")
        prompt_tokens = completion.prompt_tokens
        prompt_token_source = "provider_usage"
        if prompt_tokens is None:
            prompt_tokens = sum(len(str(message.get("content", "")).split()) for message in messages)
            prompt_token_source = "estimated_whitespace"
        response_token_source = "provider_usage"
        if completion.response_tokens is not None:
            response_tokens = completion.response_tokens
        else:
            response_tokens = len(output_text.split())
            response_token_source = "estimated_whitespace"

        turn_entry = episode_logging.build_episode_turn_entry(
            timestamp=now,
            env_idx=env_idx,
            global_steps=global_steps,
            epoch=epoch,
            turn_id=turn_id,
            episode_turn_id=len(turns),
            agent_id=acting_agent,
            prompt_tokens=int(prompt_tokens),
            response_tokens=int(response_tokens),
            messages=request_messages,
            output_text=output_text,
        )
        turn_entry["prompt_token_source"] = prompt_token_source
        turn_entry["response_token_source"] = response_token_source
        turn_entry["provider_finish_reason"] = completion.finish_reason
        turn_entry["response_truncated"] = completion.finish_reason in {
            "length",
            "max_tokens",
        }
        turn_entry["visible_action_missing"] = completion.visible_action_missing
        if include_raw_response and completion.raw is not None:
            turn_entry["provider_raw_response"] = completion.raw
        if completion.reasoning_format is not None:
            reasoning_entry: dict[str, Any] = {
                "format": completion.reasoning_format,
                "present": bool(completion.reasoning_text),
                "characters": len(completion.reasoning_text or ""),
            }
            if include_reasoning_text and completion.reasoning_text:
                reasoning_entry["text"] = completion.reasoning_text
            turn_entry["native_reasoning"] = reasoning_entry
        turns.append(turn_entry)

        game_blocks.append(
            f"\n=== {now}Z env={env_idx} turn={turn_id} agent={acting_agent} "
            f"prompt_tokens={prompt_tokens} response_tokens={response_tokens} ===\n"
            f"[TURN CONTEXT]\n{episode_logging.extract_turn_context(request_messages)}\n\n"
            f"[OUTPUT]\n{output_text}\n"
        )

        action: Any = output_text
        if completion.vote_metadata is not None:
            action = {
                acting_agent: {
                    "text": output_text,
                    "metadata": completion.vote_metadata,
                }
            }
        else:
            action = {acting_agent: output_text}

        messages, reward, terminations, truncations, info = env.step(action)
        flat_info = flatten_info(info)
        agent_id = flat_info.get("active_agent")
        done = is_done(terminations, truncations)
        turn_id += 1

    episode_row = episode_logging.build_episode_log_row(
        epoch=epoch,
        global_steps=global_steps,
        env_idx=env_idx,
        episode_index=episode_index,
        turns=turns,
        reward=reward,
        info=flat_info,
    )
    episode_row["seed"] = seed
    episode_row["experiment"] = {
        "cell_name": cell_name,
        "reasoning_mode": reasoning_mode,
        "provider": provider_name,
        "model": model_name,
    }
    episode_logging.append_jsonl_locked(out_jsonl, episode_row)
    write_game_log(
        game_log,
        episode_header=(
            f"\n{'=' * 70}\n"
            f"=== FRONTIER ROLLOUT provider={provider_name} model={model_name} "
            f"seed={seed} env={env_idx} episode={episode_index} ===\n"
            f"{'=' * 70}\n"
        ),
        turn_blocks=game_blocks,
        env_idx=env_idx,
        reward=reward,
        final_info=flat_info,
    )

    metrics = flat_info.get("metrics") or {}
    llm_input_tokens = sum(int(turn.get("prompt_tokens") or 0) for turn in turns)
    llm_output_tokens = sum(int(turn.get("response_tokens") or 0) for turn in turns)
    return {
        "seed": seed,
        "env": env_idx,
        "episode_index": episode_index,
        "turns": len(turns),
        "llm_input_tokens": llm_input_tokens,
        "llm_output_tokens": llm_output_tokens,
        "llm_total_tokens": llm_input_tokens + llm_output_tokens,
        "consensus": bool((flat_info.get("episode_state") or {}).get("consensus_reached", False)),
        "chosen_student_rank_global": metrics.get("outcome/chosen_student_rank_global"),
        "social_welfare_efficiency": metrics.get("social_welfare/efficiency"),
        "elapsed_sec": time.time() - start_wall,
        "native_reasoning_turns": sum(
            1 for turn in turns if (turn.get("native_reasoning") or {}).get("present")
        ),
        "truncated_response_turns": sum(
            1 for turn in turns if turn.get("response_truncated")
        ),
        "missing_visible_action_turns": sum(
            1 for turn in turns if turn.get("visible_action_missing")
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--provider",
        required=True,
        choices=["openai", "anthropic", "openrouter", "cmu-gateway", "local-vllm", "openai-compatible", "fake"],
    )
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--model-revision", default=os.environ.get("MODEL_REVISION") or None)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--api-key-env", default=None)
    parser.add_argument("--num-episodes", type=int, default=10)
    parser.add_argument("--num-envs", type=int, default=32)
    parser.add_argument(
        "--episode-workers",
        type=int,
        default=1,
        help="Concurrent episodes sent to the provider; default 1 preserves prior behavior.",
    )
    parser.add_argument("--seed-base", type=int, default=0)
    parser.add_argument("--out-jsonl", default=os.environ.get("VERL_AGENT_EPISODE_LOG_PATH"))
    parser.add_argument("--game-log", default=os.environ.get("VERL_GAME_LOG_PATH"))
    parser.add_argument("--metadata-json", default=os.environ.get("ZERO_SHOT_METADATA_PATH"))
    parser.add_argument("--cell-name", default=os.environ.get("ZERO_SHOT_CELL_NAME"))
    parser.add_argument("--reasoning-mode", choices=REASONING_MODES, default="manual-tags")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=None)
    parser.add_argument("--max-output-tokens", type=int, default=512)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--request-logprobs", action="store_true")
    parser.add_argument("--include-raw-response", action="store_true")
    parser.add_argument("--include-reasoning-text", action="store_true")
    parser.add_argument("--fake-vote-student", type=int, default=0)
    parser.add_argument("--openrouter-referer", default=None)
    parser.add_argument("--openrouter-title", default="Verlog frontier rollout")

    parser.add_argument("--students-per-batch", type=int, default=5)
    parser.add_argument("--token-budget", type=int, default=500)
    parser.add_argument("--feature-dim", type=int, default=5)
    parser.add_argument("--vote-threshold", type=float, default=0.5)
    parser.add_argument("--max-steps", type=int, default=50)
    parser.add_argument("--terminate-on-all-voted-no-consensus", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--prompt-length", type=int, default=4096)
    parser.add_argument("--max-prompt-words", type=int, default=None)
    parser.add_argument("--reward-mode", choices=["individual", "group", "combined"], default=None)
    parser.add_argument("--reward-alpha", type=float, default=None)
    parser.add_argument("--show-ability-vectors", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--randomize-turn-order", action="store_true")
    parser.add_argument("--utility-mode", choices=["linear", "squared", "exp"], default=None)
    parser.add_argument(
        "--professor-preference-mode",
        choices=[
            "random_permutation",
            "diverse_top_feature",
            "rejection_low_correlation",
            "rejection_low_correlation_distinct_top",
        ],
        default=None,
    )
    parser.add_argument("--preference-correlation-threshold", type=float, default=None)
    parser.add_argument("--preference-rejection-max-attempts", type=int, default=None)
    parser.add_argument(
        "--env-config-json",
        default=None,
        help="JSON string or path to a JSON object of env config overrides.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.out_jsonl:
        raise SystemExit("--out-jsonl or VERL_AGENT_EPISODE_LOG_PATH is required")
    if args.reasoning_mode == "native-thinking" and args.provider not in {"local-vllm", "fake"}:
        raise SystemExit("--reasoning-mode native-thinking is supported only for local-vllm and fake")
    Path(args.out_jsonl).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_jsonl).write_text("")
    if args.game_log:
        Path(args.game_log).parent.mkdir(parents=True, exist_ok=True)

    env_config = load_env_config(args)
    start_ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    metadata = build_run_metadata(args, env_config, start_ts=start_ts)
    write_metadata(args.metadata_json, metadata)
    try:
        client = make_client(args)
        if args.game_log:
            prompt_env = AsyncTickerAdmissionsEnv({**env_config, "seed": args.seed_base})
            prompt_env.reset()
            system_prompts = {
                agent_id: adapt_messages_for_reasoning_mode(
                    [
                        {
                            "role": "system",
                            "content": (
                                prompt_env.get_system_prompt(agent_id)
                                or prompt_env.build_system_prompt(
                                    agent_id,
                                    preference_vector=prompt_env.professor_interests[agent_id].tolist(),
                                )
                            ),
                        }
                    ],
                    args.reasoning_mode,
                )[0]["content"]
                for agent_id in prompt_env.professor_ids
            }
            write_game_log_prompt_header(args.game_log, system_prompts)
        print(
            f"Running {args.num_episodes} episodes provider={args.provider} model={args.model} "
            f"reasoning_mode={args.reasoning_mode} temperature={args.temperature} "
            f"top_p={args.top_p} out_jsonl={args.out_jsonl}"
        )
        print(f"Chat template kwargs: {json.dumps(chat_template_kwargs_for_mode(args.reasoning_mode))}")
        print(f"Episode seeds: {metadata['episode_seeds']}")
        print(f"Env config: {json.dumps(env_config, sort_keys=True)}")

        def run_index(i: int) -> dict[str, Any]:
            env_idx = i % max(args.num_envs, 1)
            episode_index = i // max(args.num_envs, 1)
            return run_episode(
                client=client,
                env_config=env_config,
                seed=args.seed_base + i,
                env_idx=env_idx,
                episode_index=episode_index,
                epoch=-1,
                global_steps=0,
                out_jsonl=args.out_jsonl,
                game_log=args.game_log,
                provider_name=args.provider,
                model_name=args.model,
                reasoning_mode=args.reasoning_mode,
                cell_name=args.cell_name,
                include_raw_response=args.include_raw_response,
                include_reasoning_text=args.include_reasoning_text,
            )

        results_by_index: list[dict[str, Any] | None] = [None] * args.num_episodes
        completed = 0
        worker_count = min(max(args.episode_workers, 1), max(args.num_episodes, 1))
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = {executor.submit(run_index, i): i for i in range(args.num_episodes)}
            for future in as_completed(futures):
                i = futures[future]
                result = future.result()
                results_by_index[i] = result
                completed += 1
                print(
                    f"[{completed}/{args.num_episodes}] seed={result['seed']} env={result['env']} "
                    f"turns={result['turns']} consensus={result['consensus']} "
                    f"native_reasoning_turns={result['native_reasoning_turns']} "
                    f"truncated={result['truncated_response_turns']} "
                    f"missing_action={result['missing_visible_action_turns']} "
                    f"llm_tokens={result['llm_input_tokens']}+{result['llm_output_tokens']} "
                    f"rank={result['chosen_student_rank_global']} "
                    f"sw_eff={result['social_welfare_efficiency']} "
                    f"elapsed={result['elapsed_sec']:.1f}s",
                    flush=True,
                )

        results = [result for result in results_by_index if result is not None]
        if len(results) != args.num_episodes:
            raise RuntimeError(
                f"Expected {args.num_episodes} episode results, received {len(results)}"
            )

        consensus = sum(1 for result in results if result["consensus"])
        socially_optimal = sum(1 for result in results if result["chosen_student_rank_global"] == 1)
        llm_input_tokens = sum(int(result["llm_input_tokens"]) for result in results)
        llm_output_tokens = sum(int(result["llm_output_tokens"]) for result in results)
        native_reasoning_turns = sum(int(result["native_reasoning_turns"]) for result in results)
        truncated_response_turns = sum(
            int(result["truncated_response_turns"]) for result in results
        )
        missing_visible_action_turns = sum(
            int(result["missing_visible_action_turns"]) for result in results
        )
        metadata.update(
            {
                "status": "complete",
                "end_timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "result_summary": {
                    "episodes": len(results),
                    "consensus_rate": consensus / max(len(results), 1),
                    "socially_optimal_rate": socially_optimal / max(len(results), 1),
                    "llm_input_tokens": llm_input_tokens,
                    "llm_output_tokens": llm_output_tokens,
                    "native_reasoning_turns": native_reasoning_turns,
                    "native_reasoning_observed": native_reasoning_turns > 0,
                    "truncated_response_turns": truncated_response_turns,
                    "missing_visible_action_turns": missing_visible_action_turns,
                },
            }
        )
        write_metadata(args.metadata_json, metadata)
        print(
            f"Done. consensus_rate={consensus / max(len(results), 1):.3f} "
            f"socially_optimal_rate={socially_optimal / max(len(results), 1):.3f} "
            f"native_reasoning_turns={native_reasoning_turns} "
            f"llm_input_tokens={llm_input_tokens} "
            f"llm_output_tokens={llm_output_tokens} "
            f"llm_total_tokens={llm_input_tokens + llm_output_tokens}"
        )
    except BaseException as exc:
        metadata.update(
            {
                "status": "failed",
                "end_timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "failure": {"type": type(exc).__name__, "message": str(exc)},
            }
        )
        write_metadata(args.metadata_json, metadata)
        raise


if __name__ == "__main__":
    main()
