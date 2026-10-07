# Rhea training standard

All project training on Rhea must use `slurm/train_auton.sbatch`. Training
behavior lives in `configs/train_auton.yaml`; the sbatch file owns only Slurm
resources, private environment setup, and the single training invocation.

Do not create copied sbatch launchers or alternate cluster entrypoints. Express
experiment changes as Hydra overrides after the canonical launcher path so the
resolved values are captured in W&B.

## Layout

```text
configs/
  train_auton.yaml                 # canonical training configuration
  env/auton_admissions.yaml        # hiring environment configuration
  checkpointing/critic_only.yaml   # optional sparse critic checkpoints
slurm/
  common.sh                   # private env, GPU, CPU, cache, and Ray setup
  train_auton.sbatch          # only supported Rhea training entrypoint
  auton.env.example           # template for private site configuration
```

## One-time Rhea setup

From the project checkout under `/zfsauton/scratch/$USER`:

```bash
install -m 600 slurm/auton.env.example slurm/auton.env
```

Review `ENV_PATH`, `DATA_DIR`, and `MODEL_PATH` in `slurm/auton.env` before the
first submission. The file is git-ignored and must remain private.

Authenticate W&B once with `wandb login`, which writes the standard
`~/.netrc` entry. `WANDB_API_KEY` in `slurm/auton.env` is only needed when that
login state is unavailable. Runs use W&B project `unscripted` and the active
user's entity unless `WANDB_ENTITY` is explicitly set.

## Submit runs

Submit the baseline from the repository root:

```bash
sbatch slurm/train_auton.sbatch
```

For an experiment, pass a descriptive `tag` and the matching Hydra override:

```bash
sbatch slurm/train_auton.sbatch \
  tag=students7 \
  envs.env_config.students_per_batch=7
```

The run name is `unscripted_auton_<tag>_<jobid>`. The complete resolved Hydra
configuration is stored in W&B, so the tag and override must describe the same
change. Use Hydra's `+` prefix only when adding a key that is not in the schema.

Examples:

```bash
sbatch slurm/train_auton.sbatch \
  tag=noconsensus \
  envs.env_config.terminate_on_all_voted_no_consensus=false

sbatch slurm/train_auton.sbatch \
  tag=profs5 \
  envs.env_config.professor_ids='["prof_1","prof_2","prof_3","prof_4","prof_5"]'
```

Keep one experimental change per job unless the experiment explicitly requires
a coupled intervention.

Dynamic token batching and the `repeat=10`, `divide=1` critic warmup safeguards
are baseline settings in `configs/train_auton.yaml`. To additionally save sparse
critic-model-only snapshots at steps 1, 5, 10, 30, and 75, compose the optional
checkpointing policy:

```bash
sbatch slurm/train_auton.sbatch tag=critic-only +checkpointing=critic_only
```

This produces `unscripted_auton_critic-only_<jobid>`. These checkpoints omit the
actor, optimizer, and trainer state and therefore cannot resume training. Add a
direct Hydra override after the policy only when intentionally changing one of
its values.

## Sweeps

Submit each sweep cell as an independent canonical Slurm job:

```bash
for s in 3 5 7; do
  sbatch slurm/train_auton.sbatch \
    tag=students$s \
    envs.env_config.students_per_batch=$s
done
```

This keeps every allocation, resolved config, W&B run, and failure independent.

## Runtime guarantees

`slurm/common.sh`:

- loads `slurm/auton.env` before validating required paths;
- preserves the GPU list assigned by Slurm;
- requeues allocations whose GPUs span NUMA sockets, excluding each fragmented
  node, unless `ALLOW_SPLIT_GPUS=1` is explicitly configured;
- derives `trainer.n_gpus_per_node` from the allocation;
- passes `SLURM_CPUS_PER_TASK` to `ray.init()`;
- creates job-scoped temporary and Ray directories;
- never stops or deletes Ray state belonging to another job;
- accepts standard W&B login state or `WANDB_API_KEY`.
- writes checkpoints under `CHECKPOINT_ROOT` when configured, otherwise under
  the project checkout.

The launcher writes Slurm output to `logs/auton_<jobid>.out` and
`logs/auton_<jobid>.err`. Training logs and artifacts remain under the shared
project checkout and configured scratch paths.

## Required review

Before submitting a production run, verify the branch, private paths, model,
dataset, requested Slurm resources, `tag`, and Hydra overrides. Changes to the
default model, allocation shape, or training length require explicit review;
they must not be hidden in a copied launcher.
