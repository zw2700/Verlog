from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from analysis import compute_zero_shot_matrix
from scripts import launch_zero_shot_matrix, rollout_frontier
from verl.envs.hiring_env.env import AsyncTickerAdmissionsEnv


def env_messages() -> list[dict[str, str]]:
    env = AsyncTickerAdmissionsEnv({**rollout_frontier.DEFAULT_ENV_CONFIG, "seed": 0})
    messages, _ = env.reset()
    return messages


def test_concurrent_env_resets_preserve_seed_pairing() -> None:
    def signature(seed: int) -> str:
        _, _, info = rollout_frontier.reset_seeded_env(
            rollout_frontier.DEFAULT_ENV_CONFIG, seed
        )
        flat_info = rollout_frontier.flatten_info(info)
        return json.dumps(
            rollout_frontier.episode_logging.json_safe(
                {
                    "students": flat_info["student_batch"],
                    "interests": flat_info["professor_interests"],
                }
            ),
            sort_keys=True,
        )

    seeds = list(range(16))
    expected = {seed: signature(seed) for seed in seeds}
    with ThreadPoolExecutor(max_workers=8) as executor:
        observed = dict(zip(seeds, executor.map(signature, seeds), strict=True))

    assert observed == expected


def test_manual_mode_is_unchanged_and_disables_native_thinking() -> None:
    messages = env_messages()
    assert rollout_frontier.adapt_messages_for_reasoning_mode(messages, "manual-tags") is messages
    assert rollout_frontier.chat_template_kwargs_for_mode("manual-tags") == {
        "enable_thinking": False
    }


def test_native_mode_adapts_only_reasoning_protocol() -> None:
    messages = env_messages()
    adapted = rollout_frontier.adapt_messages_for_reasoning_mode(messages, "native-thinking")
    text = "\n".join(message["content"] for message in adapted)

    assert "<THINK>" not in text.upper()
    assert "model-native private reasoning" in text
    assert "maximize your personal utility" in text
    assert "Voting requires 50% agreement" in text
    for tag in rollout_frontier.VISIBLE_ACTION_TAGS:
        assert tag in text
    assert rollout_frontier.chat_template_kwargs_for_mode("native-thinking") == {
        "enable_thinking": True
    }


def test_openai_compatible_separated_reasoning_preserves_visible_action(monkeypatch) -> None:
    payload_seen = {}

    def fake_http_json(url, *, headers, payload, timeout, max_retries):
        payload_seen.update(payload)
        return {
            "choices": [
                {
                    "message": {
                        "reasoning_content": "Private native reasoning",
                        "content": "<VOTE>2</VOTE>",
                    }
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 7},
        }

    monkeypatch.setattr(rollout_frontier, "_http_json", fake_http_json)
    client = rollout_frontier.OpenAICompatibleClient(
        model="Qwen/Qwen3-4B",
        api_key="dummy",
        base_url="http://localhost:8000/v1",
        temperature=1.3,
        max_tokens=512,
        timeout=1,
        max_retries=0,
        top_p=1.0,
        request_logprobs=False,
        extra_body={"chat_template_kwargs": {"enable_thinking": True}},
    )
    completion = client.complete([{"role": "user", "content": "act"}])

    assert payload_seen["chat_template_kwargs"] == {"enable_thinking": True}
    assert completion.text == "<VOTE>2</VOTE>"
    assert completion.reasoning_text == "Private native reasoning"
    assert completion.reasoning_format == "separated"


def _openai_client(*, strip_embedded_reasoning: bool) -> rollout_frontier.OpenAICompatibleClient:
    return rollout_frontier.OpenAICompatibleClient(
        model="Qwen/Qwen3-4B",
        api_key="dummy",
        base_url="http://localhost:8000/v1",
        temperature=1.0,
        max_tokens=1024,
        timeout=1,
        max_retries=0,
        top_p=1.0,
        request_logprobs=False,
        strip_embedded_reasoning=strip_embedded_reasoning,
    )


def test_native_embedded_reasoning_is_not_sent_as_visible_action(monkeypatch) -> None:
    def fake_http_json(url, *, headers, payload, timeout, max_retries):
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": "<think>private</think>\n<VOTE>2</VOTE>"},
                }
            ]
        }

    monkeypatch.setattr(rollout_frontier, "_http_json", fake_http_json)
    completion = _openai_client(strip_embedded_reasoning=True).complete([])

    assert completion.text == "<VOTE>2</VOTE>"
    assert completion.reasoning_text == "private"
    assert completion.reasoning_format == "embedded"
    assert completion.finish_reason == "stop"
    assert not completion.visible_action_missing


def test_native_unclosed_reasoning_becomes_missing_action(monkeypatch) -> None:
    def fake_http_json(url, *, headers, payload, timeout, max_retries):
        return {
            "choices": [
                {
                    "finish_reason": "length",
                    "message": {"content": "<think>private but truncated"},
                }
            ]
        }

    monkeypatch.setattr(rollout_frontier, "_http_json", fake_http_json)
    completion = _openai_client(strip_embedded_reasoning=True).complete([])

    assert completion.text == ""
    assert completion.reasoning_text == "private but truncated"
    assert completion.reasoning_format == "embedded-unclosed"
    assert completion.finish_reason == "length"
    assert completion.visible_action_missing


def test_manual_embedded_reasoning_remains_in_environment_action(monkeypatch) -> None:
    raw_content = "<THINK>private</THINK><VOTE>2</VOTE>"

    def fake_http_json(url, *, headers, payload, timeout, max_retries):
        return {"choices": [{"finish_reason": "stop", "message": {"content": raw_content}}]}

    monkeypatch.setattr(rollout_frontier, "_http_json", fake_http_json)
    completion = _openai_client(strip_embedded_reasoning=False).complete([])

    assert completion.text == raw_content
    assert completion.reasoning_text == "private"
    assert completion.reasoning_format == "embedded"


def launcher_args(tmp_path: Path) -> argparse.Namespace:
    return argparse.Namespace(
        preset="smoke",
        run_id="test-run",
        artifact_root=str(tmp_path),
        sbatch="rollout_local_vllm_frank.sbatch",
        model="Qwen/Qwen3-4B",
        model_revision="abc123",
        base_temperature=1.0,
        high_temperature=1.3,
        top_p=1.0,
        max_output_tokens=4096,
        vllm_max_model_len=16384,
        seed_base=10,
        num_episodes=3,
        episode_workers=8,
        partition=None,
        qos=None,
        time=None,
        submit=False,
    )


def test_four_cells_have_distinct_paths_and_identical_paired_seeds(tmp_path: Path) -> None:
    manifest = launch_zero_shot_matrix.build_manifest(launcher_args(tmp_path))
    paths = [cell["episode_jsonl"] for cell in manifest["cells"]]

    assert len(manifest["cells"]) == 4
    assert len(set(paths)) == 4
    assert manifest["shared"]["episode_seeds"] == [10, 11, 12]
    assert {cell["temperature"] for cell in manifest["cells"]} == {1.0, 1.3}
    assert {cell["reasoning_mode"] for cell in manifest["cells"]} == {
        "manual-tags",
        "native-thinking",
    }
    command = launch_zero_shot_matrix.sbatch_command(manifest, manifest["cells"][0])
    export_arg = command[command.index("--export") + 1]
    assert "MAX_OUTPUT_TOKENS=4096" in export_arg
    assert "VLLM_MAX_MODEL_LEN=16384" in export_arg
    assert "INCLUDE_REASONING_TEXT=1" in export_arg
    assert "EPISODE_WORKERS=8" in export_arg


def minimal_episode(seed: int) -> dict:
    return {
        "seed": seed,
        "consensus": True,
        "chosen_student": 0,
        "socially_optimal": True,
        "social_welfare_efficiency": 1.0,
        "tokens_used": 10,
        "total_turns": 2,
        "turns": [
            {
                "agent": "prof_1",
                "response_truncated": True,
                "visible_action_missing": True,
                "actions": {
                    "group_messages": [],
                    "votes": ["0"],
                    "wait_count": 0,
                    "wait_for": [],
                },
            },
            {
                "agent": "prof_2",
                "actions": {
                    "group_messages": [],
                    "votes": ["0"],
                    "wait_count": 0,
                    "wait_for": [],
                },
            },
        ],
        "student_batch": [
            {"index": 0, "profile_vector": [1.0, 0.0, 0.0]},
            {"index": 1, "profile_vector": [0.0, 1.0, 0.0]},
            {"index": 2, "profile_vector": [0.0, 0.0, 1.0]},
        ],
        "professor_interests": {
            "prof_1": [1.0, 0.0, 0.0],
            "prof_2": [1.0, 0.0, 0.0],
            "prof_3": [1.0, 0.0, 0.0],
        },
        "agent_turn_stats": {
            "prof_1": {"turns": 1, "format_errors": 0, "invalid_errors": 0},
            "prof_2": {"turns": 1, "format_errors": 0, "invalid_errors": 0},
            "prof_3": {"turns": 0, "format_errors": 0, "invalid_errors": 0},
        },
    }


def test_matrix_analysis_emits_expected_four_cell_fields(tmp_path: Path) -> None:
    manifest = launch_zero_shot_matrix.build_manifest(launcher_args(tmp_path))
    run_dir = Path(manifest["run_dir"])
    run_dir.mkdir(parents=True)
    for cell in manifest["cells"]:
        cell_dir = Path(cell["artifact_dir"])
        cell_dir.mkdir()
        Path(cell["episode_jsonl"]).write_text(json.dumps(minimal_episode(10)) + "\n")
    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))

    rows = compute_zero_shot_matrix.run(manifest_path)
    overall = [row for row in rows if row["scenario"] == "all"]

    assert len(overall) == 4
    assert all(row["episode_count"] == 1 for row in overall)
    assert all(row["instant_decision_rate"] == 1.0 for row in overall)
    assert all("invalid_action_rate" in row for row in overall)
    assert all(row["truncated_response_rate"] == 0.5 for row in overall)
    assert all(row["missing_visible_action_rate"] == 0.5 for row in overall)
    assert (run_dir / "analysis/matrix_summary.csv").exists()
    assert (run_dir / "analysis/matrix_summary.json").exists()
    assert (run_dir / "analysis/matrix_summary.md").exists()
    assert (run_dir / "analysis/qualitative_trace_pairs.json").exists()


def test_run_metadata_contains_resolved_experimental_variables(tmp_path: Path) -> None:
    args = launcher_args(tmp_path)
    args.provider = "local-vllm"
    args.reasoning_mode = "native-thinking"
    args.cell_name = "qwen3-4b-zs-base-native"
    args.out_jsonl = str(tmp_path / "episodes.jsonl")
    args.game_log = str(tmp_path / "game.log")
    args.metadata_json = str(tmp_path / "metadata.json")
    args.num_envs = 3
    args.temperature = 1.0
    metadata = rollout_frontier.build_run_metadata(
        args,
        rollout_frontier.DEFAULT_ENV_CONFIG,
        start_ts="2026-08-19T00:00:00Z",
    )

    assert metadata["model"] == "Qwen/Qwen3-4B"
    assert metadata["requested_model_revision"] == "abc123"
    assert metadata["chat_template_kwargs"] == {"enable_thinking": True}
    assert metadata["episode_seeds"] == [10, 11, 12]
    assert metadata["environment_config"]["token_budget"] == 500
    assert metadata["episode_workers"] == 8


@pytest.mark.parametrize("reasoning_mode", ["manual-tags", "native-thinking"])
def test_fake_rollout_keeps_manifest_log_path_and_replaces_previous_run(tmp_path, monkeypatch, reasoning_mode):
    output = tmp_path / "episodes.jsonl"
    output.write_text('{"seed": -1}\n')
    monkeypatch.delenv("VERL_GAME_LOG_PATH", raising=False)
    monkeypatch.delenv("ZERO_SHOT_METADATA_PATH", raising=False)
    monkeypatch.setattr(sys, "argv", [
        "rollout_frontier", "--provider", "fake", "--num-episodes", "2",
        "--episode-workers", "2", "--seed-base", "10",
        "--reasoning-mode", reasoning_mode, "--out-jsonl", str(output),
    ])

    rollout_frontier.main()

    rows = compute_zero_shot_matrix.read_jsonl(output)
    assert len(rows) == 2
    assert sorted(row["seed"] for row in rows) == [10, 11]
    assert all(row["experiment"]["reasoning_mode"] == reasoning_mode for row in rows)
