# AGENTS.md

Guidance for AI agents working in this repo. Keep it current when the workflow changes.

## Running training + ablations

Training runs on **Verl**, which is configured with **Hydra**. Hyperparameters live in
composable config files, **not** in the sbatch. Do not paste walls of `key=value` args
into new sbatch scripts — override the Hydra config instead.

Key files:
- `configs/train_auton.yaml` — the canonical training config (composes over `ppo_trainer`).
- `configs/env/auton_admissions.yaml` — env params (`num_envs`, `env_config.*` such as
  `professor_ids`, `students_per_batch`, `token_budget`, `vote_threshold`, …).
- `slurm/train_auton.sbatch` — the only supported Rhea training entrypoint. Never hardcode experiment params here.
- `slurm/common.sh` — node/env/Ray setup (sourced by the sbatch).
- `slurm/README.md` — full human-facing docs.

### The rule for ablations: one `tag`, and the override is self-documenting

Every ablation is one submit command. Always set a `tag` **and** change the underlying
config value(s). The `tag` becomes the wandb run name; the changed value(s) are captured
in the wandb config. Both are logged automatically — do not edit config files for a
one-off ablation.

```bash
# pattern: sbatch slurm/train_auton.sbatch tag=<short-slug> <hydra.overrides...>
sbatch slurm/train_auton.sbatch tag=students7 envs.env_config.students_per_batch=7
```

This yields a **traceable run**:
- wandb **run name** = `unscripted_auton_students7_<jobid>` (from `tag` -> `trainer.experiment_name`
  -> `wandb.init(name=...)`).
- wandb **config panel** = the full resolved Hydra config, including
  `envs.env_config.students_per_batch = 7`, filterable/groupable in the UI
  (`wandb.init(config=...)`).

Conventions for agents:
- **`tag` must describe the change**, kebab/camel, no spaces: `tag=noconsensus`,
  `tag=corr0.5`, `tag=profs5`. Keep the baseline as `tag=base`.
- **Change exactly what the ablation says** and nothing else — one variable per run unless
  the task explicitly asks for a grid.
- **Keep tag and override in sync**: if you set `tag=students7`, the run must actually pass
  `envs.env_config.students_per_batch=7`. Mismatched tag/value makes runs untraceable.
- Adding a key that isn't in the schema needs Hydra's `+` prefix
  (`+envs.env_config.new_flag=true`); changing an existing key does not.
- List values (e.g. `professor_ids`) are passed quoted:
  `envs.env_config.professor_ids='["prof_1","prof_2"]'`.

### Sweeps (grids)

Prefer a loop of independent Slurm jobs, one `tag` per cell, so each cell is its own
traceable wandb run:

```bash
for s in 3 5 7; do
  sbatch slurm/train_auton.sbatch tag=students$s envs.env_config.students_per_batch=$s
done
```

### Before running / reporting

- Runs need `slurm/auton.env` (install from `slurm/auton.env.example` and verify
  `ENV_PATH`, `DATA_DIR`, and `MODEL_PATH`). It is git-ignored and must remain private.
  Standard `wandb login` state is sufficient; `WANDB_API_KEY` is optional.
- When reporting an ablation, cite the **wandb run name** (`unscripted_auton_<tag>_<jobid>`) and the
  exact override(s) used, so the run is reproducible from the report alone.
- Every Rhea training job must use `slurm/train_auton.sbatch`. Do not add copied
  sbatch launchers or alternate submission paths; use explicit Hydra overrides.
- Do not update a checkout that may be serving running jobs. Runs from different
  code versions must use separate commit-pinned worktrees/directories. Record the
  exact commit and submit directory, and leave that source tree immutable until
  every job using it has finished. Cells in one matched experiment may share one
  immutable worktree when they use the exact same commit.

### Asymmetric critic observations

`critic_observation.mode=actor_visible` gives the value critic exactly the actor
prompt. `critic_observation.mode=all_utilities` appends a training-only table of
every professor's per-student utilities to the critic system prompt. In both modes,
the acting policy and reference policy receive only the original actor-visible
prompt, and the critic evaluates the exact response tokens sampled by that policy.

Every job writes compact row-level critic diagnostics to
`logs/critic_rows_<jobid>.jsonl`, including value, return, advantage, reward,
professor, episode/turn identity, bootstrap status, and actor/critic prompt lengths.
W&B also records prompt-length deltas and the critic fit/correlation metrics.

### Critic sanity probe

The hiring wrapper has an opt-in critic-only diagnostic. `critic_probe_mode=visible`
samples an independent `-1` or `+1` terminal target for every professor and episode,
adds that professor's target to the visible prompt, zeros intermediate environment
rewards, and replaces terminal utilities with the sampled targets. `hidden` returns
the same random targets without adding them to the prompt and is the negative control.
Normal hiring behavior is unchanged when the mode is `off`.

Freeze the actor for the entire probe, remove KL shaping, and use undiscounted
Monte Carlo returns so completed-episode targets are exactly `-1` or `+1`:

```bash
for mode in visible hidden; do
  sbatch slurm/train_auton.sbatch \
    tag=critic-probe-$mode \
    envs.env_config.critic_probe_mode=$mode \
    algorithm.use_kl_in_reward=false \
    algorithm.step_gamma=1.0 \
    algorithm.step_lam=1.0 \
    trainer.critic_warmup=20 \
    trainer.critic_warmup_batch_repeat_times=1 \
    trainer.critic_warmup_batch_divide_ratio=1 \
    trainer.total_training_steps=20
done
```

Read `critic_probe/s0/value_target_mse`, `critic_probe/s0/value_target_pearson`,
and `critic_probe/s0/sign_accuracy`. The visible run should improve sharply on
fresh random targets; the hidden run should remain near chance. Also verify
`critic_probe/s0/return_target_mse` stays near zero, which checks terminal reward
routing and GAE independently of value prediction. Probe metrics exclude bootstrap
rows and incomplete rollout fragments. Critic updates in an active probe also use
only naturally completed episode rows, preventing learned bootstrap values from
contaminating the fixed-label regression check. The resulting irregular batch is
padded to a multiple of the critic world size times its per-GPU microbatch size so
all FSDP ranks execute the same number of collectives.
# Repository Guidelines

## Project Context

This repo is the Verlog / VERL fork for the Unscripted Multiagent LLMs work.

The research target is the async admissions/hiring game: professor agents evaluate student candidates under a shared token budget, communicate asynchronously, vote, and sometimes reach consensus. Treat bad outcomes as a decomposition problem, not one generic "collaboration failed" label. The important failure modes are private-best identification, social aggregation, timing, communication value, and credit assignment.

Be precise about terminology:

- The task environment is `envs.env_name=async_ticker_admissions`, backed by `AsyncTickerAdmissionsEnv`.
- `gsm8k` config names and parquet paths are inherited VERL prompt/data plumbing in the current working launchers.
- Runtime/conda paths are implementation details; do not confuse them with the research environment.

## Project Structure & Module Organization

- `verl/`: The modified VERL codebase. Keep upstream-style changes local and narrow.
- `verl/envs/hiring_env/`: Git submodule for the hiring/admissions environment. Initialize submodules before assuming tests or imports work.
- `verl/envs/hiring_env_wrapper.py`: VERL wrapper around `AsyncTickerAdmissionsEnv`.
- `verl/envs/environments/__init__.py`: Registers `async_ticker_admissions` with the VERL environment factory.
- `verl/envs/hiring_episode_logging.py`: Training-compatible JSONL episode logging and action-summary helpers.
- `verl/experimental/agent_loop/tool_agent_loop.py`: Multi-agent/tool loop integration; changes here affect rollout behavior.
- `examples/sglang_multiturn/config/`: Upstream VERL examples retained for reference. Rhea training uses `configs/train_auton.yaml`.
- `analysis/`: Research analysis artifacts, category labels, preference-scenario summaries, plots, and report scripts.
- `scripts/rollout_frontier.py`: Frontier/API model rollouts for the hiring env.
- `scripts/rollout_viewer.py`: Local inspection utility for rollout logs.
- `monitor/`: Claude/W&B/Slurm monitor scaffolding.
- `.agents/skills/`: Canonical repo-local skills. Use `slurm` for Rhea/Auton Slurm and `wandb` for W&B run inspection. `.claude/skills` is a symlink to this directory so Claude Code sees the same skills; edit skills only under `.agents/skills/`.

## Build, Test, and Development Commands

Initialize submodules when setting up a fresh clone:

```bash
git submodule update --init --recursive
```

Project setup follows the existing README pattern:

```bash
conda create -n verlog python==3.10
conda activate verlog
USE_MEGATRON=0 bash scripts/install_vllm_sglang_mcore.sh
pip install --no-deps -e .
```

Useful local checks:

```bash
python -m pytest tests/envs/test_hiring_env_metrics.py
python -m pytest tests/experimental/test_agent_loop_env_metric_aggregation.py
python -m pytest tests/interactions/test_interaction_registry.py
ruff check verl/envs scripts tests
```

The full VERL test suite may require optional distributed-training dependencies and GPUs. Prefer targeted tests for the code you touched, and say clearly when broader tests were not run.

## Rhea / Auton Operations

This project uses Rhea/Auton Slurm cluster.

Use the repo-local Slurm skill for live cluster work:

```text
$slurm
```

Default project-owned Rhea training shape:

```text
partition/qos: general / qos_general
resources: 1 node, 4 a6000 GPUs, 32 CPUs, 200G RAM, 47:59:00
project checkout: /zfsauton/scratch/$USER/unscripted/Verlog
runtime env: shared/project Verlog conda env; verify on Rhea before submitting
VERL seed dataset: shared/project parquet files used by the dataloader
task env: async_ticker_admissions
model default: Qwen/Qwen3-4B
W&B project: unscripted
```

Every project run must use `slurm/train_auton.sbatch` with private paths and optional secrets in the git-ignored `slurm/auton.env`. The launcher must preserve Slurm's `CUDA_VISIBLE_DEVICES`, pass `SLURM_CPUS_PER_TASK` explicitly to Ray, and use job-scoped Ray temporary state. Experiment changes belong in explicit Hydra overrides, not copied launchers. Use W&B project `unscripted`; do not set a default W&B entity, so each user logs to their active entity unless `WANDB_ENTITY` is explicitly set.

Ask before major remote actions: creating remote directories, syncing the repo to Rhea, installing packages, submitting jobs, cancelling jobs, or changing long-running monitor state.

## W&B

Use the repo-local W&B skill for W&B API queries:

```text
$wandb
```

Default W&B project for this repo is `unscripted`. The entity is the user's active W&B entity unless `WANDB_ENTITY` is explicitly set.

New PPO runs also log `config_provenance` alongside the resolved W&B config. It contains the
primary Hydra config name, exact `hydra_task_overrides`, the resolved `original_config` composed
without task overrides, and `resolved_changes` mapping every affected config path to its original
and overridden values. Use W&B's Run Comparer with **Diff only** for cross-run comparison, and use
`config_provenance` when the question is specifically whether a value came from a Hydra override.

## Coding Style & Conventions

- Follow the existing VERL style unless a local file clearly establishes a stronger pattern.
- Python target is 3.10+ for this repo.
- Keep changes scoped to the requested behavior. Avoid broad upstream refactors.
- Prefer explicit Hydra/config overrides over hidden defaults.
- Use assertions for expected research-data invariants.
- Avoid defensive compatibility layers unless they are needed for current launchers or tests.
- Keep agent-loop and environment changes easy to audit; these paths are experiment-critical.
- Use `rg` for search and targeted `pytest` commands for verification.

## Data, Logs, and Secrets

- Keep large generated logs, checkpoints, W&B runtime folders, caches, and temporary files out of Git.
- Put the Rhea project checkout and high-volume artifacts under `/zfsauton/scratch`, not home directories.
- Never add new literal API keys or tokens to sbatch files or docs.
- Never print, copy, or commit credentials found in local or remote runtime files.
- Episode logs are research artifacts. If changing their schema, update readers and analysis scripts in the same change.

## Documentation Expectations

When code changes affect workflow, environment setup or cluster usage, update this file. `CLAUDE.md` should remain a pointer to `AGENTS.md` so Claude Code and Codex receive the same repo instructions. Keep `.claude/skills` as a symlink to `.agents/skills`. When cluster related knowledge changes, update `.agents/skills/slurm/SKILL.md`. When W&B project/query conventions change, update `.agents/skills/wandb/SKILL.md`.
