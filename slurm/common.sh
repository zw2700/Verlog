#!/bin/bash
# Shared setup for the canonical Auton Slurm job. Source it from the project
# directory because Slurm executes a spool copy of the sbatch script:
#   source "$PROJECT_DIR/slurm/common.sh"
#
# It sets up the conda env, caches, job-scoped Ray state, GPU + vLLM env vars, and the
# per-job log paths. Everything site-specific comes from environment variables
# (see slurm/auton.env.example), so the .sbatch and the Hydra config stay portable.
set -euo pipefail

# ---------------------------------------------------------------------------
# Site paths — override in slurm/auton.env or the submit environment.
# ---------------------------------------------------------------------------
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

# Load site config file if present (not committed; holds paths + secrets).
if [ -f "$PROJECT_DIR/slurm/auton.env" ]; then
    set -a; source "$PROJECT_DIR/slurm/auton.env"; set +a
fi

ENV_PATH="${ENV_PATH:?set ENV_PATH to your conda env prefix (e.g. in slurm/auton.env)}"
export DATA_DIR="${DATA_DIR:?set DATA_DIR to the dir holding train.parquet/test.parquet}"

cd "$PROJECT_DIR"

export PATH="$ENV_PATH/bin:$PATH"
export CONDA_PREFIX="$ENV_PATH"
PYTHON_BIN="$ENV_PATH/bin/python3"

JOB_ID="${SLURM_JOB_ID:-local_$(date +%s)}"
export HF_HOME="${HF_HOME:-$PROJECT_DIR/.cache/huggingface}"
TMPDIR_BASE="${TMPDIR:-$PROJECT_DIR/tmp}"
export TMPDIR="${TMPDIR_BASE%/}/${JOB_ID}"
export RAY_TMPDIR="$TMPDIR/ray"
mkdir -p "$HF_HOME" "$TMPDIR" "$PROJECT_DIR/logs"

# Accept either an explicit key or the standard credentials written by
# `wandb login`. Never copy a literal key into a committed launcher.
if [ -z "${WANDB_API_KEY:-}" ] && ! grep -qsE '^[[:space:]]*machine[[:space:]]+api\.wandb\.ai([[:space:]]|$)' "$HOME/.netrc"; then
    echo "ERROR: run 'wandb login' or set WANDB_API_KEY in slurm/auton.env" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# System limits + job-scoped Ray state
# ---------------------------------------------------------------------------
ulimit -n 65535 || true
ulimit -u 65535 || true

echo "=== Preparing job-scoped Ray state at $RAY_TMPDIR ==="
rm -rf "$RAY_TMPDIR"
mkdir -p "$RAY_TMPDIR"

# Compatibility for tools that inspect this environment variable. The sbatch
# also passes this value explicitly to ray.init() through Hydra.
export RAY_NUM_CPUS="${SLURM_CPUS_PER_TASK:-16}"
export RAY_INCLUDE_DASHBOARD=0
export RAY_DISABLE_DASHBOARD=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export RAY_raylet_startup_timeout_ms=120000
export RAY_gcs_server_request_timeout_seconds=60
export RAY_BACKEND_LOG_LEVEL=warning

# ---------------------------------------------------------------------------
# GPU + vLLM. NUM_GPUS_PER_NODE is exported so the Hydra config can read it via
# ${oc.env:NUM_GPUS_PER_NODE}.
# ---------------------------------------------------------------------------
: "${CUDA_VISIBLE_DEVICES:?Slurm did not set CUDA_VISIBLE_DEVICES for this GPU job}"
IFS=',' read -r -a CUDA_DEVICE_IDS <<< "$CUDA_VISIBLE_DEVICES"
ALLOCATED_GPU_COUNT="${#CUDA_DEVICE_IDS[@]}"
export NUM_GPUS_PER_NODE="${NUM_GPUS_PER_NODE:-$ALLOCATED_GPU_COUNT}"
if [ "$NUM_GPUS_PER_NODE" -ne "$ALLOCATED_GPU_COUNT" ]; then
    echo "ERROR: NUM_GPUS_PER_NODE=$NUM_GPUS_PER_NODE but Slurm exposed $ALLOCATED_GPU_COUNT GPUs" >&2
    exit 1
fi
unset ROCR_VISIBLE_DEVICES || true
export VLLM_USE_V1=1
export VERL_AUTO_PADDING=TRUE
export PYTHONUNBUFFERED=1

# ---------------------------------------------------------------------------
# Per-job agent I/O and game logs.
# ---------------------------------------------------------------------------
export VERL_AGENT_IO_LOG_PATH="$PROJECT_DIR/logs/agent_model_${JOB_ID}.log"
export VERL_AGENT_IO_LOG_FULL_PROMPT=0
export VERL_AGENT_EPISODE_LOG_PATH="$PROJECT_DIR/logs/episode_log_${JOB_ID}.jsonl"
export VERL_GAME_LOG_PATH="$PROJECT_DIR/logs/game_log_${JOB_ID}.log"
export VERL_CRITIC_ROW_LOG_PATH="$PROJECT_DIR/logs/critic_rows_${JOB_ID}.jsonl"
: > "$VERL_AGENT_IO_LOG_PATH"
: > "$VERL_CRITIC_ROW_LOG_PATH"

echo "=== Job ${JOB_ID} on ${SLURMD_NODENAME:-local} — $(date) ==="
echo "PROJECT_DIR=$PROJECT_DIR  ENV_PATH=$ENV_PATH  GPUs=$NUM_GPUS_PER_NODE  Ray CPUs=$RAY_NUM_CPUS"
echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
nvidia-smi -L 2>/dev/null || echo "WARN: nvidia-smi unavailable"
