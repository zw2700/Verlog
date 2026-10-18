"""Matched, batched zero-shot hiring rollouts on a Slurm-allocated local model."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import time
from collections import deque
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

import hydra
from omegaconf import DictConfig, OmegaConf

from scripts.rollout_frontier import Completion, FakeVoteClient, episode_rollout
from verl.envs import hiring_episode_logging as episode_logging

ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = {"baseline", "deliberation", "deliberation_no_communication"}


def request_seed(base, scenario_seed, context):
    """The seed belongs to an agent/phase opportunity, never its queue position."""
    identity = [base, scenario_seed, context["agent_id"], context["phase"], context["actor_phase_turn"]]
    return int.from_bytes(hashlib.sha256(json.dumps(identity).encode()).digest()[:4], "big") % (2**31)


def source_provenance():
    def git(*args):
        return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()

    versions = {}
    for package in ("vllm", "torch", "transformers", "numpy", "gym", "hydra-core"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return {
        "commit": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain")),
        "hiring_submodule": git("submodule", "status", "verl/envs/hiring_env"),
        "python": platform.python_version(),
        "packages": versions,
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "node": platform.node(),
    }


def condition_configs(config):
    base = deepcopy(config["envs"]["env_config"])
    base["prompt_length"] = config["sampling"]["prompt_length"]
    result = {}
    for condition in config["conditions"]:
        env_config = deepcopy(base)
        if condition == "baseline":
            env_config["protocol"] = "async_ticker"
            env_config.pop("deliberation", None)
        else:
            env_config.update(protocol="deliberation_voting", max_steps=None)
            env_config["deliberation"] = {
                **config["deliberation"],
                "communication_enabled": condition != "deliberation_no_communication",
            }
        result[condition] = env_config
    return result


def validate_config(config):
    if config["backend"] not in {"fake", "vllm"}:
        raise ValueError("backend must be fake or vllm")
    conditions = config["conditions"]
    if not conditions or len(set(conditions)) != len(conditions) or not set(conditions) <= CONDITIONS:
        raise ValueError("conditions must be distinct members of the supported pilot conditions")
    if config["num_episodes"] < 1 or config["batch_size"] < 1 or config["seed_base"] < 0:
        raise ValueError("num_episodes/batch_size must be positive and seed_base nonnegative")
    sampling, model = config["sampling"], config["model"]
    if sampling["prompt_length"] + sampling["max_tokens"] > model["max_model_len"]:
        raise ValueError("max_model_len must cover prompt_length + max_tokens")
    if config["envs"]["env_config"].get("system_prompt"):
        raise ValueError("pilot uses the actual phase-aware environment prompts")


class LocalVLLMClient:
    """vLLM 0.10 API, verified against Rhea's installed runtime."""

    def __init__(self, config):
        from vllm import LLM, SamplingParams

        self.sampling_params = SamplingParams
        self.sampling = config["sampling"]
        self.performance = {"batches": 0, "requests": 0, "batch_wall_seconds": 0.0}
        model = config["model"]
        options = {
            key: model[key]
            for key in (
                "tensor_parallel_size",
                "dtype",
                "gpu_memory_utilization",
                "max_model_len",
                "enforce_eager",
                "enable_prefix_caching",
            )
        }
        if model["revision"] is not None:
            options.update(revision=model["revision"], tokenizer_revision=model["revision"])
        self.llm = LLM(model=model["path"], seed=config["inference_seed"], max_num_seqs=config["batch_size"], **options)
        self.tokenizer = self.llm.get_tokenizer()

    def complete_batch(self, messages, seeds):
        sampling_params = [
            self.sampling_params(
                temperature=self.sampling["temperature"],
                top_p=self.sampling["top_p"],
                max_tokens=self.sampling["max_tokens"],
                seed=seed,
            )
            for seed in seeds
        ]
        started = time.perf_counter()
        outputs = self.llm.chat(
            messages,
            sampling_params=sampling_params,
            use_tqdm=False,
            chat_template_kwargs={"enable_thinking": self.sampling["enable_native_thinking"]},
        )
        self.performance["batch_wall_seconds"] += time.perf_counter() - started
        self.performance["batches"] += 1
        self.performance["requests"] += len(outputs)
        return [
            Completion(
                text=result.outputs[0].text,
                prompt_tokens=len(result.prompt_token_ids),
                response_tokens=len(result.outputs[0].token_ids),
                cached_prompt_tokens=result.num_cached_tokens,
            )
            for result in outputs
        ]


class FakeBatchClient:
    tokenizer = None

    def __init__(self):
        self.client = FakeVoteClient()

    def complete_batch(self, messages, seeds):
        return [self.client.complete(observation) for observation in messages]


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(episode_logging.json_safe(value), indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def summarize(results, conditions):
    summary = {}
    for condition in conditions:
        rows = [row for row in results if row["condition"] == condition]
        reported_tokens = sum(row["llm_cache_reported_input_tokens"] for row in rows)
        cached_tokens = sum(row["llm_cached_input_tokens"] or 0 for row in rows)
        summary[condition] = {
            "episodes": len(rows),
            "agreement_rate": mean(float(row["consensus"]) for row in rows),
            "socially_optimal_rate": mean(float(row["chosen_student_rank_global"] == 1) for row in rows),
            "mean_welfare_efficiency": mean(row["social_welfare_efficiency"] for row in rows),
            "mean_public_messages": mean(row["public_messages"] for row in rows),
            "mean_model_calls": mean(row["turns"] for row in rows),
            "mean_participating_professors": mean(row["participating_professors"] for row in rows),
            "mean_speaking_professors": mean(row["speaking_professors"] for row in rows),
            "format_errors": sum(row["format_errors"] for row in rows),
            "invalid_actions": sum(row["invalid_actions"] for row in rows),
            "total_input_tokens": sum(row["llm_input_tokens"] for row in rows),
            "total_output_tokens": sum(row["llm_output_tokens"] for row in rows),
            "cache_reported_input_tokens": reported_tokens,
            "cached_input_tokens": cached_tokens if reported_tokens else None,
            "prefix_cache_hit_fraction": cached_tokens / reported_tokens if reported_tokens else None,
        }
    return summary


def run_pilot(cfg, client=None):
    config = OmegaConf.to_container(cfg, resolve=True) if OmegaConf.is_config(cfg) else deepcopy(cfg)
    validate_config(config)
    provenance = source_provenance()
    configs = condition_configs(config)
    plan = {
        "config": config,
        "source": provenance,
        "condition_configs": configs,
        "total_episodes": config["num_episodes"] * len(configs),
        "status": "planned" if config["dry_run"] else "running",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "fake_results": config["backend"] == "fake",
    }
    if config["dry_run"]:
        print(json.dumps(plan, indent=2, sort_keys=True))
        return plan
    if config["require_clean_git"] and provenance["dirty"]:
        raise ValueError("Use a clean commit-pinned checkout, or disable require_clean_git for CPU tests only")
    if config["backend"] == "vllm":
        if not os.environ.get("SLURM_JOB_ID") or not os.environ.get("CUDA_VISIBLE_DEVICES"):
            raise ValueError("Real model execution requires a Slurm GPU allocation; use dry_run=true on login nodes")
        visible_count = len(os.environ["CUDA_VISIBLE_DEVICES"].split(","))
        if config["model"]["tensor_parallel_size"] > visible_count:
            raise ValueError("tensor_parallel_size exceeds the Slurm-visible GPU count")
    output = Path(config["output_dir"]).resolve()
    # Refuse to append to a different/partial run or overwrite its evidence.
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "manifest.json", plan)
    started = time.monotonic()
    try:
        if client is None:
            client = FakeBatchClient() if config["backend"] == "fake" else LocalVLLMClient(config)
        pending = deque(
            (condition, seed)
            for seed in range(config["seed_base"], config["seed_base"] + config["num_episodes"])
            for condition in configs
        )
        active, results = [], []
        scenario_hashes = {}
        while pending or active:
            while pending and len(active) < config["batch_size"]:
                condition, seed = pending.popleft()
                request_context = {}
                rollout = episode_rollout(
                    env_config=configs[condition],
                    seed=seed,
                    env_idx=0,
                    episode_index=seed - config["seed_base"],
                    epoch=-1,
                    global_steps=0,
                    out_jsonl=output / condition / "episodes.jsonl",
                    game_log=output / condition / "game.log",
                    provider_name="fake" if config["backend"] == "fake" else "local-vllm-offline",
                    model_name=config["model"]["path"],
                    include_raw_response=False,
                    tokenizer=client.tokenizer,
                    request_context=request_context,
                )
                # No client ever receives privileged Gym info, only the actor's
                # filtered system/user messages yielded by the environment.
                active.append(
                    {
                        "rollout": rollout,
                        "messages": next(rollout),
                        "condition": condition,
                        "seed": seed,
                        "context": request_context,
                    }
                )
            seeds = [request_seed(config["inference_seed"], row["seed"], row["context"]) for row in active]
            for row, seed in zip(active, seeds, strict=True):
                row["context"]["sampling_seed"] = seed
            completions = client.complete_batch([row["messages"] for row in active], seeds)
            if len(completions) != len(active):
                raise ValueError("completion count must match actor prompt count")
            remaining = []
            for row, completion in zip(active, completions, strict=True):
                try:
                    row["messages"] = row["rollout"].send(completion)
                    remaining.append(row)
                except StopIteration as finished:
                    result = {**finished.value, "condition": row["condition"]}
                    hashes = scenario_hashes.setdefault(row["seed"], set())
                    hashes.add(result["scenario_sha256"])
                    if len(hashes) != 1:
                        raise ValueError(f"Unmatched scenario for seed {row['seed']}") from None
                    results.append(result)
                    episode_logging.append_jsonl(output / "results.jsonl", result)
                    print(
                        f"{len(results)}/{plan['total_episodes']} {row['condition']} seed={row['seed']} "
                        f"calls={result['turns']} agreement={result['consensus']} "
                        f"welfare={result['social_welfare_efficiency']:.4f}",
                        flush=True,
                    )
            active = remaining
        summary = summarize(results, config["conditions"])
        summary["paired_welfare_differences"] = {}
        if "baseline" in configs:
            baseline = {row["seed"]: row for row in results if row["condition"] == "baseline"}
            for condition in config["conditions"]:
                if condition != "baseline":
                    differences = [
                        row["social_welfare_efficiency"] - baseline[row["seed"]]["social_welfare_efficiency"]
                        for row in results
                        if row["condition"] == condition
                    ]
                    summary["paired_welfare_differences"][condition] = mean(differences)
        write_json(output / "summary.json", summary)
        plan.update(
            status="complete",
            completed_episodes=len(results),
            elapsed_seconds=time.monotonic() - started,
            paired_scenarios_verified=len(scenario_hashes),
            inference=getattr(client, "performance", None),
        )
        write_json(output / "manifest.json", plan)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return summary
    except Exception as exc:
        plan.update(
            status="failed",
            error_type=type(exc).__name__,
            error=str(exc)[:1000],
            inference=getattr(client, "performance", None),
        )
        write_json(output / "manifest.json", plan)
        raise


@hydra.main(config_path="../configs", config_name="zero_shot_pilot", version_base=None)
def main(config: DictConfig):
    run_pilot(config)


if __name__ == "__main__":
    main()
