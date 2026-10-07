#!/usr/bin/env python3
"""Build or submit the Qwen3-4B zero-shot thinking x temperature matrix."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

PRESETS = {
    "smoke": {"num_episodes": 3, "partition": "general", "qos": "qos_general", "time": "04:00:00"},
    "pilot": {"num_episodes": 100, "partition": "general", "qos": "qos_general", "time": "12:00:00"},
    "full": {"num_episodes": 500, "partition": "general", "qos": "qos_general", "time": "24:00:00"},
}

CELL_SPECS = (
    ("qwen3-4b-zs-base-manual", "manual-tags", "base"),
    ("qwen3-4b-zs-high-temp-manual", "manual-tags", "high"),
    ("qwen3-4b-zs-base-native", "native-thinking", "base"),
    ("qwen3-4b-zs-high-temp-native", "native-thinking", "high"),
)


def build_manifest(args: argparse.Namespace) -> dict[str, Any]:
    preset = PRESETS[args.preset]
    num_episodes = args.num_episodes or preset["num_episodes"]
    run_id = args.run_id or f"{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}-{args.preset}"
    run_dir = Path(args.artifact_root).expanduser().resolve() / run_id
    seeds = [args.seed_base + i for i in range(num_episodes)]
    shared = {
        "model": args.model,
        "model_revision": args.model_revision,
        "base_temperature": args.base_temperature,
        "high_temperature": args.high_temperature,
        "top_p": args.top_p,
        "max_output_tokens": args.max_output_tokens,
        "vllm_max_model_len": args.vllm_max_model_len,
        "seed_base": args.seed_base,
        "episode_seeds": seeds,
        "num_episodes": num_episodes,
        "episode_workers": args.episode_workers,
        "environment_config": {
            "professor_ids": ["prof_1", "prof_2", "prof_3"],
            "students_per_batch": 5,
            "token_budget": 500,
            "feature_dim": 5,
            "vote_threshold": 0.5,
            "max_steps": 50,
            "terminate_on_all_voted_no_consensus": False,
            "professor_preference_mode": "random_permutation",
            "randomize_turn_order": False,
        },
    }
    cells = []
    for slug, reasoning_mode, temperature_key in CELL_SPECS:
        cell_dir = run_dir / slug
        temperature = (
            args.base_temperature if temperature_key == "base" else args.high_temperature
        )
        cells.append(
            {
                "slug": slug,
                "reasoning_mode": reasoning_mode,
                "temperature": temperature,
                "artifact_dir": str(cell_dir),
                "episode_jsonl": str(cell_dir / "episodes.jsonl"),
                "game_log": str(cell_dir / "game.log"),
                "metadata_json": str(cell_dir / "metadata.json"),
                "slurm_stdout": str(cell_dir / "slurm-%j.out"),
                "slurm_stderr": str(cell_dir / "slurm-%j.err"),
                "job_id": None,
            }
        )
    return {
        "schema_version": 1,
        "experiment": "qwen3-4b-zero-shot-thinking-temperature",
        "preset": args.preset,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "created_timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "shared": shared,
        "slurm": {
            "partition": args.partition or preset["partition"],
            "qos": args.qos or preset["qos"],
            "time": args.time or preset["time"],
            "sbatch": str(Path(args.sbatch).resolve()),
        },
        "cells": cells,
    }


def sbatch_command(manifest: dict[str, Any], cell: dict[str, Any]) -> list[str]:
    shared = manifest["shared"]
    env = shared["environment_config"]
    exports = {
        "MODEL": shared["model"],
        "NUM_EPISODES": shared["num_episodes"],
        "NUM_ENVS": min(shared["num_episodes"], 8),
        "EPISODE_WORKERS": shared["episode_workers"],
        "SEED_BASE": shared["seed_base"],
        "TEMPERATURE": cell["temperature"],
        "TOP_P": shared["top_p"],
        "MAX_OUTPUT_TOKENS": shared["max_output_tokens"],
        "VLLM_MAX_MODEL_LEN": shared["vllm_max_model_len"],
        "REASONING_MODE": cell["reasoning_mode"],
        "INCLUDE_REASONING_TEXT": 1,
        "ZERO_SHOT_CELL_NAME": cell["slug"],
        "ZERO_SHOT_METADATA_PATH": cell["metadata_json"],
        "VERL_AGENT_EPISODE_LOG_PATH": cell["episode_jsonl"],
        "VERL_GAME_LOG_PATH": cell["game_log"],
        "STUDENTS_PER_BATCH": env["students_per_batch"],
        "TOKEN_BUDGET": env["token_budget"],
        "FEATURE_DIM": env["feature_dim"],
        "VOTE_THRESHOLD": env["vote_threshold"],
        "MAX_STEPS": env["max_steps"],
        "TERMINATE_ON_ALL_VOTED_NO_CONSENSUS": int(
            env["terminate_on_all_voted_no_consensus"]
        ),
        "PROFESSOR_PREFERENCE_MODE": env["professor_preference_mode"],
        "RANDOMIZE_TURN_ORDER": int(env["randomize_turn_order"]),
        "ROLLOUT_POSTFIX": cell["slug"],
    }
    if shared["model_revision"]:
        exports["MODEL_REVISION"] = shared["model_revision"]
    export_arg = "ALL," + ",".join(f"{key}={value}" for key, value in exports.items())
    return [
        "sbatch",
        "--parsable",
        "--job-name",
        cell["slug"],
        "--partition",
        manifest["slurm"]["partition"],
        "--qos",
        manifest["slurm"]["qos"],
        "--time",
        manifest["slurm"]["time"],
        "--output",
        cell["slurm_stdout"],
        "--error",
        cell["slurm_stderr"],
        "--export",
        export_arg,
        manifest["slurm"]["sbatch"],
    ]


def write_manifest(manifest: dict[str, Any]) -> Path:
    run_dir = Path(manifest["run_dir"])
    run_dir.mkdir(parents=True, exist_ok=False)
    for cell in manifest["cells"]:
        Path(cell["artifact_dir"]).mkdir(parents=True)
    path = run_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=sorted(PRESETS), default="smoke")
    parser.add_argument("--run-id")
    parser.add_argument("--artifact-root", default="artifacts/zero-shot-thinking")
    parser.add_argument("--sbatch", default="rollout_local_vllm_frank.sbatch")
    parser.add_argument("--model", default="Qwen/Qwen3-4B")
    parser.add_argument("--model-revision")
    parser.add_argument("--base-temperature", type=float, default=1.0)
    parser.add_argument("--high-temperature", type=float, default=1.3)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-output-tokens", type=int, default=4096)
    parser.add_argument("--vllm-max-model-len", type=int, default=16384)
    parser.add_argument("--seed-base", type=int, default=0)
    parser.add_argument("--num-episodes", type=int)
    parser.add_argument("--episode-workers", type=int, default=8)
    parser.add_argument("--partition")
    parser.add_argument("--qos")
    parser.add_argument("--time")
    parser.add_argument("--submit", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.model != "Qwen/Qwen3-4B":
        raise SystemExit("This experiment is fixed to --model Qwen/Qwen3-4B")
    manifest = build_manifest(args)
    manifest_path = write_manifest(manifest)
    print(f"Manifest: {manifest_path}")
    for cell in manifest["cells"]:
        command = sbatch_command(manifest, cell)
        if args.submit:
            try:
                result = subprocess.run(command, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as exc:
                manifest.setdefault("submission_errors", []).append(
                    {
                        "cell": cell["slug"],
                        "returncode": exc.returncode,
                        "stderr": exc.stderr.strip(),
                        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                    }
                )
                manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
                raise SystemExit(f"sbatch failed for {cell['slug']}: {exc.stderr.strip()}") from exc
            cell["job_id"] = result.stdout.strip().split(";")[0]
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
            print(f"submitted {cell['slug']}: job {cell['job_id']}")
        else:
            print(" ".join(command))
    if args.submit:
        manifest["submitted_timestamp"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
