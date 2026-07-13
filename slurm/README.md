# Composable configs + thin sbatch for auton runs

**Goal:** stop copy-pasting the ~80-line wall of `key=value` overrides that lived
inside `train_auton_frank.sbatch`. Verl already runs on **Hydra**, so every one of
those `algorithm.adv_estimator=gae ...` args was a Hydra override. We move them
into a composable config and shrink the sbatch to resource requests + env setup.

## Layout

```
configs/
  train_auton.yaml            # experiment: composes ppo_trainer + env + all overrides
  env/auton_admissions.yaml   # env config group (num_envs, env_config.*)
  hydra/launcher/slurm.yaml   # optional: Submitit launcher (no-sbatch path)
slurm/
  common.sh                   # sourced env setup + Ray cleanup (was inline in the sbatch)
  train_auton.sbatch          # thin wrapper: SBATCH directives + one launch
  auton.env.example           # copy to auton.env; site paths + WANDB_API_KEY
```

## One-time setup

```bash
cp slurm/auton.env.example slurm/auton.env   # then edit ENV_PATH, DATA_DIR, WANDB_API_KEY
```

`slurm/auton.env` is git-ignored (it holds secrets). Site paths stay out of the
committed sbatch and config.

## Everyday use

```bash
# Baseline run — nothing to edit:
sbatch slurm/train_auton.sbatch

# Override any config value on the CLI (Hydra syntax); args flow through "$@":
sbatch slurm/train_auton.sbatch envs.env_config.students_per_batch=7 trainer.total_training_steps=100

# Add a brand-new key not in the schema — use the Hydra `+` prefix:
sbatch slurm/train_auton.sbatch +envs.env_config.some_new_flag=true
```

To make a variant permanent, add a small config that composes over this one
(e.g. `configs/train_auton_smoke.yaml` with `defaults: [train_auton, _self_]` and
a few overrides) and run `EXP=train_auton_smoke sbatch slurm/train_auton.sbatch`.

## Sweeps — two paths

### 1. Loop of sbatch jobs (recommended, robust)

Each config runs as its own Slurm allocation. Simple, and it reuses the thin
sbatch and `common.sh` exactly as-is:

```bash
for s in 3 5 7; do
  sbatch slurm/train_auton.sbatch \
    envs.env_config.students_per_batch=$s \
    trainer.experiment_name=auton_students_$s
done
```

### 2. Hydra `--multirun` + Submitit launcher (no sbatch)

`pip install hydra-submitit-launcher`, then Hydra submits one Slurm job per
sweep cell for you:

```bash
python -m verl.trainer.main_ppo --config-name=train_auton --multirun \
    hydra/launcher=slurm \
    envs.env_config.students_per_batch=3,5,7
```

Trade-off: cleaner sweep syntax, but the Ray/GPU/vLLM setup that `common.sh` does
must run *inside* the job. `configs/hydra/launcher/slurm.yaml` wires that via the
launcher's `setup:` hook. This path is more experimental here — validate a single
cell before launching a large grid. For most sweeps, path 1 is less fiddly.

> Note on Hydra multirun *within a single process* (`-m` without a Slurm
> launcher): Verl grabs a whole node's GPUs and Ray for each run, so sequential
> in-process multirun works but gives you no parallelism. Prefer one Slurm job
> per config (either path above).

## Does Ray/Verl already cover sweeps?

No. Verl is one training run per `main_ppo` invocation; it uses Ray internally
for actor/rollout placement, not for hyperparameter search. The sweep/run-
management layer is exactly what Hydra provides here.

## Migration / validation notes

- `configs/train_auton.yaml` is behavior-preserving vs. `train_auton_frank.sbatch`:
  it composes over `ppo_trainer` (not `gsm8k_multiturn_grpo`) because the only
  settings that base contributed and Frank didn't already override were
  `hybrid_engine` and the `multi_turn` block — both inlined.
- Composition was validated with `hydra.compose` (all former CLI overrides
  resolve to the same values, including `agent.num_workers` interpolated from
  `envs.num_envs`). Still smoke-test one real run on the cluster before deleting
  the old sbatch — keep `train_auton_frank.sbatch` around until then.
