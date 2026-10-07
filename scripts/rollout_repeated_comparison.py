"""Paired prompt comparison over random-horizon unanimous bargaining sessions."""
from __future__ import annotations

import json
import multiprocessing
import os
import random
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from scripts import rollout_frontier as rf
from scripts import rollout_prompt_comparison as paired
from scripts.repeated_admissions import RepeatedAdmissionsRound, public_round_record, selection_utilities


def sample_session_lengths(sessions, continuation_probability=0.8, seed=9162026):
    assert 0 <= continuation_probability < 1
    rng = random.Random(seed)
    lengths = []
    for _ in range(sessions):
        rounds = 1
        while rng.random() < continuation_probability:
            rounds += 1
        lengths.append(rounds)
    return lengths


def run_session(task):
    args, base, root_str, session, rounds = task
    root = Path(root_str)
    initial = rf.AsyncTickerAdmissionsEnv({**base, "seed": session})
    initial.reset()
    preferences = {a: p.tolist() for a, p in initial.professor_interests.items()}
    configs = {name: paired.prompt_config(base, name == "discussion") for name in ("baseline", "discussion")}
    original_class = rf.AsyncTickerAdmissionsEnv
    # Scope the runner's environment adapter to this isolated worker/task.
    rf.AsyncTickerAdmissionsEnv = RepeatedAdmissionsRound
    try:
        order = ("baseline", "discussion") if session % 2 == 0 else ("discussion", "baseline")
        for condition in order:
            history, payoffs = [], {a: [] for a in preferences}
            totals = {a: 0.0 for a in preferences}
            round_results = []
            for round_idx in range(rounds):
                seed = session + 1000 * round_idx
                episode_id = session + 1000 * round_idx
                folder = root / condition / "episodes"
                output = folder / f"{episode_id}.jsonl"
                config = {**configs[condition], "session_round": round_idx + 1,
                          "fixed_preferences": preferences,
                          "model": args.model, "model_revision": args.model_revision,
                          "context_token_limit": (int(os.environ.get("VLLM_MAX_MODEL_LEN", "32768")) - args.max_output_tokens - 64) if args.provider != "fake" else None,
                          "previous_public_rounds": list(history), "private_payoffs": payoffs,
                          "cumulative_utilities": totals}
                client = rf.make_client(args)
                if hasattr(client, "extra_body"):
                    client.extra_body = {**client.extra_body, "seed": seed}
                result = rf.run_episode(
                    client=client, env_config=config, seed=seed,
                    env_idx=session, episode_index=round_idx, epoch=-1, global_steps=0,
                    out_jsonl=output, game_log=folder / f"{episode_id}.log",
                    provider_name=args.provider, model_name=args.model,
                    reasoning_mode=args.reasoning_mode, cell_name=condition,
                    include_raw_response=False, include_reasoning_text=True)
                row = json.loads(output.read_text())
                row.update(session_id=session, session_round=round_idx+1, session_rounds=rounds)
                utility = selection_utilities(row)
                for agent in preferences:
                    totals[agent] += utility[agent]
                    payoffs[agent].append(utility[agent])
                row["session_cumulative_selection_utilities"] = dict(totals)
                row["round_selection_utilities"] = utility
                output.write_text(json.dumps(row) + "\n")
                history.append(public_round_record(row, round_idx + 1))
                round_results.append(result)
            (root / condition / "sessions" / f"{session}.json").write_text(json.dumps({
                "session_id": session, "preferences": preferences,
                "cumulative_selection_utilities": totals, "round_results": round_results,
            }, indent=2) + "\n")
        return session
    finally:
        rf.AsyncTickerAdmissionsEnv = original_class


def main():
    args = rf.parse_args()
    sessions = args.num_episodes
    probability = float(os.environ.get("CONTINUATION_PROBABILITY", "0.8"))
    lengths = sample_session_lengths(sessions, probability)
    assert args.vote_threshold == 1.0
    assert sessions <= 1000 and args.seed_base == 0
    root = Path(args.out_jsonl).resolve().parent / "repeated-comparison"
    root.mkdir(parents=True, exist_ok=False)
    base = rf.load_env_config(args)
    manifest = {"status": "running", "training": False, "arguments": vars(args),
                "hidden_session_lengths": lengths, "continuation_probability": probability,
                "expected_rounds_per_session": 1 / (1 - probability), "sessions_per_prompt": sessions,
                "horizon_disclosed": False, "fixed_round_cap": None,
                "environment_config": base, "seed_formula": "session_id + 1000 * zero_based_round",
                "discussion_guidance": paired.DISCUSSION_GUIDANCE,
                "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
                "independent_sampling_unit": "session", "selection_utility_discount": 1.0}
    for name in ("baseline", "discussion"):
        (root / name / "episodes").mkdir(parents=True)
        (root / name / "sessions").mkdir()
        config = paired.prompt_config(base, name == "discussion")
        (root / name / "base_prompt_config.json").write_text(json.dumps(config, indent=2) + "\n")
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    try:
        with ProcessPoolExecutor(max_workers=int(os.environ.get("PROMPT_COMPARISON_WORKERS", "8")),
                                 mp_context=multiprocessing.get_context("spawn")) as pool:
            tasks = [pool.submit(run_session, (args, base, str(root), session, lengths[session]))
                     for session in range(sessions)]
            for n, task in enumerate(as_completed(tasks), 1):
                print(f"Completed session pair {n}/{sessions}, session={task.result()}", flush=True)
        episode_ids = [session + 1000 * r for session in range(sessions) for r in range(lengths[session])]
        paired.analyze(root, episode_ids)
        for round_idx in range(max(lengths)):
            surviving_sessions = [s for s in range(sessions) if lengths[s] > round_idx]
            round_root = root / f"round-{round_idx+1}"
            for name in ("baseline", "discussion"):
                folder = round_root / name / "episodes"
                folder.mkdir(parents=True)
                for session in surviving_sessions:
                    episode_id = session + 1000 * round_idx
                    (folder / f"{session}.jsonl").symlink_to(root / name / "episodes" / f"{episode_id}.jsonl")
            paired.analyze(round_root, surviving_sessions)
        manifest["status"] = "complete"
    except BaseException:
        manifest["status"] = "failed"
        raise
    finally:
        (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
