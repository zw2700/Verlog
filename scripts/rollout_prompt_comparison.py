"""Paired inference-only prompt comparison using the existing rollout runner.

Invoked by rollout_local_vllm_frank.sbatch with PROMPT_COMPARISON=1.
Process isolation keeps environment RNG resets independent across episodes.
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from scripts import rollout_frontier as rf

DISCUSSION_GUIDANCE = """DISCUSSION STRATEGY:
- Before your first vote, use a concise <GROUP> message to state your preferred student, one acceptable alternative if you have one, and a qualitative reason for your preference. Do not reveal exact utility numbers.
- Seek another professor's preferences before committing your vote. When you need their reply, use <WAIT_FOR>prof_name</WAIT_FOR> after your message instead of immediately voting in the same turn.
- Read colleagues' proposals and respond to the specific agreement or disagreement. Explain whether you can support their candidate, or propose an acceptable alternative; do not merely repeat your first proposal.
- Use what you learn to choose a candidate that gives you high personal utility and can obtain consensus. If new information changes which agreement is achievable, reconsider your choice and revise your vote while the game is still ongoing.
- Keep discussion purposeful and concise. Once there is enough information to reach a satisfactory agreement, vote; do not prolong discussion just to send more messages. Preserve enough shared tokens to finish the decision.
"""


def prompt_config(base: dict, discussion: bool) -> dict:
    if not discussion:
        return dict(base)
    env = rf.AsyncTickerAdmissionsEnv(base)
    prompts = {}
    for agent in env.professor_ids:
        original = env.get_system_prompt(agent) or env.build_system_prompt(agent)
        # Replace the early-voting suggestion so instructions do not conflict.
        original = original.replace(
            "- If you have made up your mind, you should VOTE using <VOTE>N</VOTE>.",
            "- After considering the discussion, cast your vote using <VOTE>N</VOTE>.",
        )
        prompts[agent] = original + "\n\n" + DISCUSSION_GUIDANCE
    return {**base, "system_prompt": prompts}


def run_pair(task: tuple) -> int:
    args, configs, root_str, seed = task
    root = Path(root_str)
    order = ("baseline", "discussion") if seed % 2 == 0 else ("discussion", "baseline")
    for condition in order:
        folder = root / condition / "episodes"
        output = folder / f"{seed}.jsonl"
        client = rf.make_client(args)
        if hasattr(client, "extra_body"):
            client.extra_body = {**client.extra_body, "seed": seed}
        result = rf.run_episode(
            client=client, env_config=configs[condition], seed=seed,
            env_idx=seed, episode_index=0, epoch=-1, global_steps=0,
            out_jsonl=output, game_log=folder / f"{seed}.log",
            provider_name=args.provider, model_name=args.model,
            reasoning_mode=args.reasoning_mode, cell_name=condition,
            include_raw_response=False, include_reasoning_text=True,
        )
        (folder / f"{seed}.summary.json").write_text(json.dumps(result) + "\n")
    return seed


def analyze(root: Path, seeds: list[int]) -> dict:
    repo = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo / "analysis" / "v1"))
    from compute_category_metrics import group_messages, votes

    summaries, paired = {}, {}
    for condition in ("baseline", "discussion"):
        folder = root / condition
        rows = [json.loads((folder / "episodes" / f"{s}.jsonl").read_text()) for s in seeds]
        paired[condition] = rows
        (folder / "episodes.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows))
        subprocess.run([sys.executable, str(repo / "analysis/v1.5/compute_preference_scenario_metrics.py"),
                        "--episode-log", str(folder / "episodes.jsonl"), "--out-dir", str(folder)], check=True)
        count = len(rows)
        changes = []
        for row in rows:
            previous, revised = {}, 0
            for turn in row["turns"]:
                agent = turn["agent"]
                for vote in votes(turn, set(range(len(row["student_batch"])))):
                    revised += agent in previous and previous[agent] != vote
                    previous[agent] = vote
            changes.append(revised)
        summary = {
            "episodes": count,
            "consensus_rate": sum(bool(r["consensus"]) for r in rows) / count,
            "socially_optimal_rate": sum(bool(r.get("socially_optimal")) for r in rows) / count,
            "mean_group_messages": sum(sum(len(group_messages(t)) for t in r["turns"]) for r in rows) / count,
            "mean_turns": sum(len(r["turns"]) for r in rows) / count,
            "mean_group_tokens": sum(r.get("tokens_used", 0) for r in rows) / count,
            "mean_vote_revisions": sum(changes) / count,
            "episodes_with_vote_revision": sum(c > 0 for c in changes) / count,
            "truncated_response_turns": sum(t.get("response_truncated", False) for r in rows for t in r["turns"]),
        }
        summaries[condition] = summary
        title = (f"{condition.capitalize()} prompt | Initial Qwen3-4B | n={count} | "
                 f"Consensus {summary['consensus_rate']:.1%} | Socially optimal {summary['socially_optimal_rate']:.1%}")
        subprocess.run([sys.executable, str(repo / "analysis/v1.5/plot_preference_scenario_categories.py"),
                        "--input", str(folder / "preference_scenario_category_breakdown.csv"),
                        "--title", title], check=True)
    for baseline, discussion in zip(paired["baseline"], paired["discussion"]):
        assert baseline["seed"] == discussion["seed"]
        for key in ("student_batch", "professor_interests"):
            assert baseline[key] == discussion[key], (baseline["seed"], key)
    summaries["pairing_verified"] = True
    (root / "summary.json").write_text(json.dumps(summaries, indent=2) + "\n")
    return summaries


def main() -> None:
    args = rf.parse_args()
    root = Path(args.out_jsonl).resolve().parent / "prompt-comparison"
    root.mkdir(parents=True, exist_ok=False)
    base = rf.load_env_config(args)
    configs = {name: prompt_config(base, name == "discussion") for name in ("baseline", "discussion")}
    seeds = list(range(args.seed_base, args.seed_base + args.num_episodes))
    manifest = {
        "status": "running", "training": False, "arguments": vars(args),
        "environment_configs": configs, "episode_seeds": seeds,
        "sampling_seed": "episode seed passed to vLLM for both prompts",
        "guidance": DISCUSSION_GUIDANCE, "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "source_sha256": {str(p.resolve().relative_to(Path.cwd())): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (Path(__file__), Path(rf.__file__), Path(rf.AsyncTickerAdmissionsEnv.__module__.replace('.', '/') + '.py'))},
    }
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    for name in configs:
        (root / name / "episodes").mkdir(parents=True)
        env = rf.AsyncTickerAdmissionsEnv(configs[name])
        prompts = {a: env.get_system_prompt(a) or env.build_system_prompt(a) for a in env.professor_ids}
        (root / name / "prompts.json").write_text(json.dumps(prompts, indent=2) + "\n")
    try:
        with ProcessPoolExecutor(max_workers=int(os.environ.get("PROMPT_COMPARISON_WORKERS", "8")),
                                 mp_context=multiprocessing.get_context("spawn")) as pool:
            futures = [pool.submit(run_pair, (args, configs, str(root), seed)) for seed in seeds]
            for n, future in enumerate(as_completed(futures), 1):
                seed = future.result()
                print(f"Completed pair {n}/{len(seeds)} seed={seed}", flush=True)
        print(json.dumps(analyze(root, seeds), indent=2), flush=True)
        manifest["status"] = "complete"
    except BaseException:
        manifest["status"] = "failed"
        raise
    finally:
        (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
