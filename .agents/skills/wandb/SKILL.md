---
name: wandb
description: Inspect Weights & Biases (W&B) runs for this repo. Use when Codex needs W&B run state, metrics, summaries, history, URLs, latest runs, groups, ETA estimates, or project/entity queries for codebase-skills / Verlog work. Also use when Rhea/Auton Slurm work needs W&B context; keep W&B API calls and W&B-derived status in this skill, not in slurm.
---

# W&B

Use this skill for W&B run inspection for `codebase-skills` / Verlog.

Keep this skill focused on W&B API work. If the user needs Rhea queues, Slurm logs, SSH cleanup, or job submission, use `$slurm` for that part and return here for W&B metrics, history, URLs, and ETAs.

## Project Selection

Default W&B project for this repo:

```text
unscripted
```

Each user logs this project under their own W&B entity. For API calls that need `entity/project`, prefer, in order:

1. A project/entity or W&B URL explicitly provided by the user.
2. A full `entity/project` path found in run URLs, logs, or local W&B config.
3. `WANDB_ENTITY` plus `trainer.project_name` from the launcher or template. The template in `$slurm` uses project `unscripted` and does not set a default entity.
4. `WANDB_PROJECT` from environment or `monitor/monitor.env` if present, without printing secrets from that file. Treat bare project names as under the active/default W&B entity.
5. Project `unscripted` under the active/default W&B entity.

## Safety Rules

- Never print tokens, `.netrc`, `.env`, `secrets.env`, `.wandb_key`, or `WANDB_API_KEY`.
- Prefer local W&B auth first. Local auth often works through `~/.netrc` or the active shell environment.
- If local auth is unavailable and the run is tied to Rhea, query W&B remotely only after loading the key without printing it.
- Do not inspect Slurm queues, read remote logs for non-W&B purposes, submit jobs, or cancel jobs from this skill. Use `$slurm`.
- Do not trust a single step-time outlier for ETA. Use recent W&B history and cross-check with `$slurm` log progress when available.

## Local Queries

Use the repo environment if available. Try `uv run python` first when `uv` is available; otherwise use the active Python environment with `wandb` installed.

Inspect one run:

```bash
uv run python - <<'PY'
import os
import wandb

PROJECT_NAME = os.environ.get("WANDB_PROJECT", "unscripted")
ENTITY = os.environ.get("WANDB_ENTITY")
RUN_ID = "RUN_ID"

api = wandb.Api(timeout=60)
ENTITY = ENTITY or api.default_entity
PROJECT = PROJECT_NAME if "/" in PROJECT_NAME else f"{ENTITY}/{PROJECT_NAME}"
run = api.run(f"{PROJECT}/{RUN_ID}")
summary = dict(run.summary)

def first(mapping, keys):
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None

print("id:", run.id)
print("name:", run.name)
print("state:", run.state)
print("url:", run.url)
print("global_step:", first(summary, ["training/global_step", "train/global_step", "global_step"]))
print("step_time:", first(summary, ["training/step_time", "train/step_time", "step_time"]))
PY
```

List recent runs:

```bash
uv run python - <<'PY'
import os
import wandb

PROJECT_NAME = os.environ.get("WANDB_PROJECT", "unscripted")
ENTITY = os.environ.get("WANDB_ENTITY")

api = wandb.Api(timeout=60)
ENTITY = ENTITY or api.default_entity
PROJECT = PROJECT_NAME if "/" in PROJECT_NAME else f"{ENTITY}/{PROJECT_NAME}"
runs = api.runs(PROJECT, order="-created_at", per_page=20)

for run in runs:
    summary = dict(run.summary)
    step = (
        summary.get("training/global_step")
        or summary.get("train/global_step")
        or summary.get("global_step")
        or "?"
    )
    print(run.created_at, run.id, run.state, step, run.name, run.url, sep="\t")
PY
```

Filter by group or display name when the user mentions a run family:

```bash
uv run python - <<'PY'
import os
import wandb

PROJECT_NAME = os.environ.get("WANDB_PROJECT", "unscripted")
ENTITY = os.environ.get("WANDB_ENTITY")
GROUP = "GROUP_NAME"

api = wandb.Api(timeout=60)
ENTITY = ENTITY or api.default_entity
PROJECT = PROJECT_NAME if "/" in PROJECT_NAME else f"{ENTITY}/{PROJECT_NAME}"
runs = api.runs(PROJECT, filters={"group": GROUP}, order="-created_at")

for run in runs:
    print(run.id, run.state, run.name, run.url, sep="\t")
PY
```

## Remote Fallback

Use this only for W&B API access when local auth is unavailable and the run is associated with Rhea. Use the project repo/env and load auth without printing secrets:

```bash
ssh rhea 'PROJECT_DIR="${PROJECT_DIR:-/zfsauton2/home/$USER/unscripted/Verlog}"; ENV_PATH="${ENV_PATH:-/zfsauton/scratch/cpulling/conda_envs/verlog}"; cd "$PROJECT_DIR"; export PATH="$ENV_PATH/bin:$PATH"; export CONDA_PREFIX="$ENV_PATH"; set -a; [ -f monitor/monitor.env ] && source monitor/monitor.env; set +a; [ -n "${WANDB_KEY_FILE:-}" ] && [ -r "$WANDB_KEY_FILE" ] && export WANDB_API_KEY="$(cat "$WANDB_KEY_FILE")"; python3 - <<'"'"'PY'"'"'
import os
import wandb

PROJECT_NAME = os.environ.get("WANDB_PROJECT", "unscripted")
ENTITY = os.environ.get("WANDB_ENTITY")
RUN_ID = "RUN_ID"

api = wandb.Api(timeout=60)
ENTITY = ENTITY or api.default_entity
PROJECT = PROJECT_NAME if "/" in PROJECT_NAME else f"{ENTITY}/{PROJECT_NAME}"
run = api.run(f"{PROJECT}/{RUN_ID}")
summary = dict(run.summary)

print(run.id, run.name, run.state, run.url)
print("global_step:", summary.get("training/global_step") or summary.get("train/global_step") or summary.get("global_step"))
PY'
```

Do not print the key. If the remote host has neither `WANDB_KEY_FILE` nor an existing W&B login, stop and ask for the W&B entity/auth path rather than dumping env files.

## ETA Pattern

Estimate ETA from recent history, not just summary:

```bash
uv run python - <<'PY'
import os
import statistics
import wandb

PROJECT_NAME = os.environ.get("WANDB_PROJECT", "unscripted")
ENTITY = os.environ.get("WANDB_ENTITY")
RUN_ID = "RUN_ID"
TARGET_STEPS = 75

api = wandb.Api(timeout=60)
ENTITY = ENTITY or api.default_entity
PROJECT = PROJECT_NAME if "/" in PROJECT_NAME else f"{ENTITY}/{PROJECT_NAME}"
run = api.run(f"{PROJECT}/{RUN_ID}")
history = run.history(
    keys=["training/global_step", "train/global_step", "training/step_time", "train/step_time"],
    samples=500,
)

step_col = "training/global_step" if "training/global_step" in history else "train/global_step"
time_col = "training/step_time" if "training/step_time" in history else "train/step_time"
rows = history.dropna(subset=[step_col, time_col]).tail(50)

step = int(rows[step_col].max())
step_times = [float(value) for value in rows[time_col].tolist()]
median_step_time = statistics.median(step_times)
remaining_seconds = max(TARGET_STEPS - step, 0) * median_step_time

print("run:", run.id, run.name)
print("state:", run.state)
print("step:", step)
print("target_steps:", TARGET_STEPS)
print("median_step_time:", median_step_time)
print("remaining_hours:", remaining_seconds / 3600)
print("url:", run.url)
PY
```

If the run has an obvious target in `run.config` or the Slurm launcher, use that instead of the default `TARGET_STEPS`. If multiple runs are active, compute ETA per run and say which target and metric keys were used.

## Reporting Back

Be concrete and brief:

- Include run id, run name, W&B state, URL, latest step, and metric names used.
- For ETA, include the target step count and recent-history window.
- Mention whether local auth or remote host auth was used, without printing any auth material.
- If W&B has not synced recently, say when the latest history row appears and avoid pretending it reflects live Slurm progress.
