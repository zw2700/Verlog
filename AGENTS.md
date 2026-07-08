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
- `examples/sglang_multiturn/config/`: Existing VERL configs reused by Verlog runs. The current hiring-env launcher still uses `gsm8k_multiturn_grpo` as the base config.
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

For launchers, start from `.agents/skills/slurm/assets/train_auton_unscripted_example.sbatch`, use W&B project `unscripted`, and source secrets from private files instead of embedding tokens. Do not set a default W&B entity; each user should log to their own active W&B entity unless `WANDB_ENTITY` is explicitly set.

Ask before major remote actions: creating remote directories, syncing the repo to Rhea, installing packages, submitting jobs, cancelling jobs, or changing long-running monitor state.

## W&B

Use the repo-local W&B skill for W&B API queries:

```text
$wandb
```

Default W&B project for this repo is `unscripted`. The entity is the user's active W&B entity unless `WANDB_ENTITY` is explicitly set.

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
- Existing launchers may contain sensitive historical values. Do not print, copy, or normalize them into new files.
- Episode logs are research artifacts. If changing their schema, update readers and analysis scripts in the same change.

## Documentation Expectations

When code changes affect workflow, environment setup or cluster usage, update this file. `CLAUDE.md` should remain a pointer to `AGENTS.md` so Claude Code and Codex receive the same repo instructions. Keep `.claude/skills` as a symlink to `.agents/skills`. When cluster related knowledge changes, update `.agents/skills/slurm/SKILL.md`. When W&B project/query conventions change, update `.agents/skills/wandb/SKILL.md`.
