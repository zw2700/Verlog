# AGENTS.md

Guidance for AI agents working in this repo. Keep it current when the workflow changes.

## Running training + ablations

Training runs on **Verl**, which is configured with **Hydra**. Hyperparameters live in
composable config files, **not** in the sbatch. Do not paste walls of `key=value` args
into new sbatch scripts — override the Hydra config instead.

Key files:
- `configs/train_auton.yaml` — the experiment config (composes over `ppo_trainer`).
- `configs/env/auton_admissions.yaml` — env params (`num_envs`, `env_config.*` such as
  `professor_ids`, `students_per_batch`, `token_budget`, `vote_threshold`, …).
- `slurm/train_auton.sbatch` — thin, generic wrapper. Never hardcode experiment params here.
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
- wandb **run name** = `auton_students7_<jobid>` (from `tag` -> `trainer.experiment_name`
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

A Hydra `--multirun` + Submitit path also exists (`configs/hydra/launcher/slurm.yaml`),
but it's more experimental here — see `slurm/README.md` before using it.

### Before running / reporting

- Runs need `slurm/auton.env` (copy from `slurm/auton.env.example`: `ENV_PATH`,
  `DATA_DIR`, `WANDB_API_KEY`). It's git-ignored — never commit it or a real API key.
- When reporting an ablation, cite the **wandb run name** (`auton_<tag>_<jobid>`) and the
  exact override(s) used, so the run is reproducible from the report alone.
- The legacy `train_auton_frank.sbatch` is kept only until the Hydra path is
  cluster-validated. Don't extend it; add to the config-based path instead.
