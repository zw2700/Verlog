"""Resume only unfinished paired samples and then generate the original plots."""
import argparse
import json
import os
from pathlib import Path

from scripts import rollout_frontier as rf
from scripts import rollout_prompt_comparison as paired


def main():
    root = Path(os.environ["PROMPT_COMPARISON_RECOVERY"])
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    args = argparse.Namespace(**manifest["arguments"])
    args.base_url = os.environ["LOCAL_VLLM_BASE_URL"]
    configs = manifest["environment_configs"]
    seeds = manifest["episode_seeds"]
    recovery = {"job_id": os.environ.get("SLURM_JOB_ID"),
                "max_model_len": os.environ.get("VLLM_MAX_MODEL_LEN"), "recovered": []}
    manifest.setdefault("recoveries", []).append(recovery)
    manifest["status"] = "recovering"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    try:
        for seed in seeds:
            for condition in ("baseline", "discussion"):
                folder = root / condition / "episodes"
                summary = folder / f"{seed}.summary.json"
                if summary.exists():
                    continue
                output = folder / f"{seed}.jsonl"
                assert not output.exists() or not output.read_text().strip(), "Existing episode without summary needs inspection"
                client = rf.make_client(args)
                client.extra_body = {**client.extra_body, "seed": seed}
                result = rf.run_episode(
                    client=client, env_config=configs[condition], seed=seed,
                    env_idx=seed, episode_index=0, epoch=-1, global_steps=0,
                    out_jsonl=output, game_log=folder / f"{seed}.log",
                    provider_name=args.provider, model_name=args.model,
                    reasoning_mode=args.reasoning_mode, cell_name=condition,
                    include_raw_response=False, include_reasoning_text=True)
                summary.write_text(json.dumps(result) + "\n")
                recovery["recovered"].append({"seed": seed, "condition": condition})
                print(f"Recovered {condition} seed={seed}", flush=True)
        print(json.dumps(paired.analyze(root, seeds), indent=2), flush=True)
        manifest["status"] = "complete"
    except BaseException:
        manifest["status"] = "failed"
        raise
    finally:
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
