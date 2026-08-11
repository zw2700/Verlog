---
name: slurm
description: Operate this repo on the Rhea/Auton Slurm cluster for Verlog hiring-env work. Use when Codex needs to SSH to Rhea, inspect or submit Slurm jobs, read remote logs, use srun/tmux, check Auton partitions, connect to allocated gpu*/lov* nodes, set up hiring/async_ticker_admissions launchers, or reason about shared Auton network filesystems such as /zfsauton and /zfsauton2. Do not use for standalone W&B metrics, histories, URLs, or ETA queries; use the repo-local wandb skill for W&B API work.
---

# Slurm

Use this skill for Auton cluster operations for `codebase-skills` / Verlog hiring-env work: Rhea Slurm jobs, remote logs, shared cluster filesystems, and allocated Slurm nodes.

When a task also needs W&B run state, metrics, history, URLs, or ETA, use `$wandb` for that part. This skill may report W&B run IDs or URLs found in logs, but should not call the W&B API.

## Connection Model

The Rhea head/login node is:

```text
rhea.int.autonlab.org
```

Use the local SSH aliases:

```bash
ssh auton '<remote command>'       # external gateway, upload.autonlab.org
ssh rhea '<remote command>'        # Rhea Slurm head/login node
ssh gpuN '<remote command>'        # allocated Slurm GPU node, via auton
ssh lovN '<remote command>'        # allocated Slurm node, via auton
```

Prefer short non-interactive commands. Request escalated/network permissions when the shell tool requires them for SSH or remote package/network access.

If SSH multiplexing reports a stale socket, try:

```bash
ssh -O exit rhea
ssh rhea 'hostname'
```

If a fresh connection asks for credentials, stop and tell the user; do not guess passwords, passcodes, or tokens.

Expected SSH shape:

```sshconfig
Host auton
  HostName upload.autonlab.org
  User <andrewID-or-cluster-user>
  Port 22
  ServerAliveInterval 30
  IdentityFile ~/.ssh/id_ed25519

Host rhea gpu* lov*
  HostName %h.int.autonlab.org
  User <andrewID-or-cluster-user>
  ProxyJump auton
```

Some setups may use `lop2.autonlab.org` instead of `upload.autonlab.org` as the external gateway. Use `ssh [options] <auton|rhea|node_name>`.

## Important Paths

Local repo:

```bash
/Users/michalwilinski/Work/unscripted-llms/codebase-skills
```

Default project-owned Rhea paths:

```bash
PROJECT_DIR="/zfsauton/scratch/$USER/unscripted/Verlog"
ENV_PATH="/zfsauton/scratch/cpulling/conda_envs/verlog"
DATA_DIR="/zfsauton/scratch/cpulling/data/gsm8k"
HF_HOME="/zfsauton/scratch/$USER/.cache/huggingface"
TMPDIR="/zfsauton/scratch/$USER/tmp"
```

This is a hiring-env training run. The actual task environment is `envs.env_name=async_ticker_admissions`, backed by the repo's hiring env (`AsyncTickerAdmissionsEnv`). The `gsm8k` config name and `DATA_DIR` are inherited VERL dataloader plumbing, not the project objective. Prefer project-owned copies of the runtime env and seed dataset when available; otherwise verify the shared paths on Rhea before submitting.

If those paths fail, discover the remote repo before running repo-relative commands:

```bash
ssh rhea 'for d in "/zfsauton/scratch/$USER/unscripted/Verlog" "$HOME/codebase-skills" "$HOME/unscripted-llms/codebase-skills" "$HOME/Work/unscripted-llms/codebase-skills" "/zfsauton2/home/$USER/unscripted-llms/codebase-skills" "/zfsauton2/home/$USER/unscripted/Verlog"; do [ -d "$d/.git" ] && echo "$d"; done'
```

Use `/zfsauton/scratch` for the project checkout, datasets, caches, checkpoints, logs, and temporary files rather than filling home directories.

Common log names in this repo include:

```text
logs/*.out
logs/*.err
logs/agent_model_train_auton_*.log
logs/episode_log_*.jsonl
logs/game_log_*.log
logs/vllm_server_*.log
```

## Filesystem Model

Rhea and the Slurm compute nodes are the only supported infrastructure for this project.

- Rhea and Slurm compute nodes share network filesystems such as `/zfsauton` and `/zfsauton2`, so a repo, conda env, dataset, cache, or log path created there is normally visible from Rhea and allocated `gpu*`/`lov*` nodes.
- Install or update once from Rhea in a shared path, then test inside a Slurm allocation.
- Keep large artifacts on shared Auton storage. Prefer `/zfsauton/scratch` for datasets, caches, checkpoints, temporary files, and other high-volume outputs.
- Keep host-specific env files out of Git. Prefer one per-host private env file for secrets and paths, then source it from launchers.

Read-only probes before setup:

```bash
ssh rhea 'hostname; id -un; df -h /zfsauton /zfsauton2 2>/dev/null || true; ls -ld /zfsauton /zfsauton2 2>/dev/null || true'
```

## Safety Rules

- Never print tokens, `.env` contents, `WANDB_API_KEY`, `.wandb_key`, `.netrc`, or `secrets.env`.
- Do not use TACC/Vista commands, accounts, queues, or paths for this repo.
- Do not create, copy, or extend alternate project launchers. Use `slurm/train_auton.sbatch` with explicit Hydra overrides.
- Do not inspect, print, or propagate credentials from runtime files. Keep optional secrets in the private `slurm/auton.env`.
- Do not set up or run this project on non-Slurm Auton machines; this project uses Rhea/Auton Slurm only.
- Do not kill processes on shared machines unless the user asked and you have identified that the process belongs to the user or the current job.
- Use `--gres=gpu:gpu_model:number` rather than pinning `--nodelist` unless the user explicitly needs a specific node.
- Use `debug` for short interactive tests; use checkpoints for `preempt`.

## Rhea Slurm

Rhea is an internal server. Use it for Slurm commands, job submission, queue inspection, and connecting onward to allocated cluster nodes.

## Partitions

Use partition and QOS together. Matching QOS to partition gives the expected priority.

| Partition | Use | Default Time | Max Time | Max GPUs | Max CPUs | QOS | GPU Models |
|---|---|---:|---:|---:|---:|---|---|
| `debug` | short tests and debugging | 0.5h | 12h | 2 | 32 | `qos_debug` | `rtx_2080_ti`, `v100`, `a6000` |
| `general` | general use, standard jobs; default GPU partition | 4h | 2d | 8 | 128 | `qos_general` | `a5000`, `a6000` |
| `legacy` | older GPU nodes | 4h | 2d | 12 | 120 | `qos_legacy` | `rtx_2080_ti`, `v100` |
| `preempt` | long, low-priority GPU jobs | 4h | 7d | 8 | 128 | `qos_preempt` | `a6000` |
| `cpu` | CPU-only tasks | 6h | 2d | 0 | 352 | `qos_cpu` | none |

Start status checks with queue state:

```bash
ssh rhea 'squeue -u "$USER" -o "%.18i %.24j %.10P %.2t %.12M %.20R"'
ssh rhea 'sinfo'
ssh rhea 'sinfo -Nl'
ssh rhea 'scontrol show part'
ssh rhea 'scontrol show part debug'
```

For a specific job:

```bash
ssh rhea 'sacct -j JOBID --format=JobID,JobName%28,Partition,State,Elapsed,ExitCode,NodeList%24 -P'
```

Useful Slurm commands:

```bash
sinfo
sinfo -Nl
scontrol show part
scontrol show part optional_partition_name
squeue
squeue -u username
sbatch my_script.sh
scancel job_id
scancel -u username
srun --jobid N --overlap --pty bash
```

`--help` is available on Slurm commands. Use it instead of guessing rarely used flags.

Read logs after discovering the remote repo path:

```bash
ssh rhea 'cd REMOTE_REPO && tail -n 120 logs/JOB_LOG.err'
ssh rhea 'cd REMOTE_REPO && tr "\r" "\n" < logs/JOB_LOG.out | grep -aE "Traceback|RuntimeError|CUDA out|OutOfMemory|failed|[0-9]+%\|" | tail -n 80'
```

## Interactive Jobs

Use `debug` for tests even though interactive mode is possible on all partitions. Use `tmux` for `srun`.

Start an interactive shell:

```bash
ssh -t rhea 'tmux new -A -s verlog'
# Inside the tmux session on rhea:
srun --partition=debug --qos=qos_debug --gres=gpu:1 --time=30:00 --pty bash
```

Model-specific examples:

```bash
srun -p debug --qos=qos_debug --gres=gpu:rtx_2080_ti:1 --time=30:00 --mem-per-gpu=10G --pty bash
srun --partition=debug --qos=qos_debug --gres=gpu:v100:2 --cpus-per-task=8 python my_test_script.py
srun --partition=general --gres=gpu:a6000:1 nvidia-smi
```

If `srun` uses `--pty bash`, the shell lands on the compute node immediately. Otherwise, connect to the assigned node from another terminal or VSCode after Slurm allocates it.

Attach to a running job allocation:

```bash
srun --jobid N --overlap --pty bash
```

## Non-Interactive Jobs

Prefer non-interactive `sbatch` jobs for real runs.

Submit a reviewed project-owned launcher from Rhea:

```bash
ssh rhea 'cd /zfsauton/scratch/$USER/unscripted/Verlog && mkdir -p logs && sbatch path/to/launcher.sbatch'
```

Recommended hiring-env training shape:

```text
job name: marl_unscripted
logs: logs/unscripted_%j.out and logs/unscripted_%j.err
partition/qos: general / qos_general
resources: 1 node, 4 a6000 GPUs, 32 CPUs, 200G RAM, 47:59:00
environment: /zfsauton/scratch/cpulling/conda_envs/verlog
task env: async_ticker_admissions / hiring env
VERL seed dataset: /zfsauton/scratch/cpulling/data/gsm8k
model default: Qwen/Qwen3-4B
W&B entity: active user W&B entity, or explicit WANDB_ENTITY
W&B project: unscripted
W&B run name: unscripted_auton_base_${SLURM_JOB_ID}
training length: trainer.total_training_steps=75
```

All project training runs must use the canonical launcher:

```text
slurm/train_auton.sbatch
```

Configure private paths and optional secrets in the git-ignored `slurm/auton.env`; install it from `slurm/auton.env.example` and verify the values before submitting. The launcher preserves Slurm's `CUDA_VISIBLE_DEVICES`, passes `SLURM_CPUS_PER_TASK` explicitly to Ray, and isolates Ray temporary state by job. Do not run global `ray stop`, `pkill`, or `/tmp/ray` cleanup from a shared-node launcher because another allocation owned by the same user may be active on that node.

This is the only supported Rhea training entrypoint. Put experiment changes in Hydra overrides after the launcher path; do not create copied sbatch files or alternate submission paths.

Environment overrides read by the canonical config include:

```bash
# Optional: export WANDB_ENTITY=your-wandb-entity
MODEL_PATH=Qwen/Qwen3-4B
ENABLE_THINKING=false
VAL_BATCH_SIZE=64
VAL_BEFORE_TRAIN=false
```

Pass experiment and environment changes as Hydra overrides after the sbatch path:

```bash
sbatch slurm/train_auton.sbatch \
  tag=students7 \
  envs.env_config.students_per_batch=7 \
  envs.env_config.terminate_on_all_voted_no_consensus=false \
  envs.env_config.professor_preference_mode=random_permutation \
  trainer.total_training_steps=75
```

The launcher writes project logs under `logs/agent_model_${SLURM_JOB_ID}.log`, `logs/episode_log_${SLURM_JOB_ID}.jsonl`, and `logs/game_log_${SLURM_JOB_ID}.log`.

Submit an existing, reviewed launcher:

```bash
ssh rhea 'cd REMOTE_REPO && sbatch path/to/launcher.sbatch'
```

For a one-off job, send an sbatch script over stdin:

```bash
ssh rhea 'cd REMOTE_REPO && sbatch --parsable' <<'SBATCH'
#!/bin/bash
#SBATCH --job-name=verlog-test
#SBATCH --output=logs/verlog-test_%j.out
#SBATCH --error=logs/verlog-test_%j.err
#SBATCH --partition=debug
#SBATCH --qos=qos_debug
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --gres=gpu:a6000:1

set -euo pipefail
mkdir -p logs
nvidia-smi -L

# Activate the project environment here, then run the requested command.
SBATCH
```

Sbatch file pattern:

```bash
#!/bin/bash
#SBATCH --job-name=job_name
#SBATCH --output=logs/job_%j.out
#SBATCH --error=logs/job_%j.err
#SBATCH --partition=debug
#SBATCH --qos=qos_debug
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --time=02:00:00
#SBATCH --gres=gpu:a6000:1

set -euo pipefail
mkdir -p logs

# Envs
conda activate my_env

# Commands
srun python train_model.py
```

Use `%j` in log filenames for the Slurm job ID. Time format is `D-HH:MM:SS` or `HH:MM:SS`.

Typical non-interactive flow:

```bash
ssh rhea
sbatch my_script.sh
```

Wait for completion, then inspect results and logs.

Typical interactive flow:

```bash
ssh rhea
tmux
srun <options>
```

## Good Practices

- Use `--gres=gpu:gpu_model:number` instead of `--nodelist=gpu_name`.
- Use `/zfsauton/scratch` instead of home directories for data, caches, checkpoints, and temporary files.
- Avoid over-requesting resources, such as requesting 128 CPU cores for a single-GPU job.
- Use `debug` for short tests and debugging.
- Prefer non-interactive `sbatch` jobs for real runs.
- Use checkpoints, especially on `preempt`.
- Use Slurm array jobs when running the same script multiple times with different parameters.
- Use `tmux` for long interactive `srun` sessions.
- Create `logs/` before job launch so Slurm can open stdout/stderr files.
- Keep W&B/HF/API secrets out of committed sbatch files; source private env files or use host-local key files.

## Preempt Partition

Jobs on `preempt` run at the lowest priority. Nodes are shared between partitions, so a low-priority `preempt` job can be killed by a higher-priority job.

`preempt` has a 2 minute grace period. Use it to catch `SIGTERM` and write a checkpoint. If you request a node currently running a preempt job, you may wait up to about 2 minutes before the node is freed. Preempted jobs are requeued after termination.

## Connecting To Allocated Nodes

Once Slurm assigns a node, connect directly with the `gpu*` or `lov*` SSH alias from another terminal or VSCode:

```bash
ssh gpuN
ssh lovN
```

Use this for log inspection, lightweight debugging inside an allocation, or VSCode Remote SSH. Do not bypass Slurm to start unmanaged jobs on cluster compute nodes.

For VSCode, connect to the assigned node directly over SSH after Slurm allocates it. Alternatively, SSH to the node, start a code tunnel, then connect through that tunnel.

## Auton Slurm Setup Checklist

1. Probe shared paths from `rhea`.
2. Confirm the project repo, runtime env, and seed dataset paths. Prefer the project checkout and high-volume outputs under `/zfsauton/scratch`.
3. Submit only from Rhea with `sbatch`; validate compute-node behavior with a short `debug` allocation.
4. Keep launchers and logs in the shared repo path so Rhea and allocated nodes see the same files.
5. Run every project training job through `slurm/train_auton.sbatch`, with private site configuration in `slurm/auton.env` and experiment changes expressed as Hydra overrides.

## Reporting Back

Be concrete and brief:

- Say which host or allocation was checked: `rhea`, `gpu*`, `lov*`, or a Slurm job allocation.
- Include Slurm job id, job name, partition, state, elapsed time, node, and log path when applicable.
- Include the exact launcher or command submitted.
- Include W&B URLs only if found in logs or returned by `$wandb`.
- If something failed, quote the first meaningful error line and the file or command it came from.
