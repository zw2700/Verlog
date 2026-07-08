#!/bin/bash
# Shared setup for auton Slurm jobs. Source this from a thin .sbatch:
#   source "$(dirname "$0")/common.sh"   # (or an absolute path)
#
# It sets up the conda env, caches, Ray cleanup, GPU + vLLM env vars, and the
# per-job log paths. Everything site-specific comes from environment variables
# (see slurm/auton.env.example), so the .sbatch and the Hydra config stay portable.
set -euo pipefail

# ---------------------------------------------------------------------------
# Site paths — override in slurm/auton.env or the submit environment.
# ---------------------------------------------------------------------------
PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
ENV_PATH="${ENV_PATH:?set ENV_PATH to your conda env prefix (e.g. in slurm/auton.env)}"
export DATA_DIR="${DATA_DIR:?set DATA_DIR to the dir holding train.parquet/test.parquet}"

# Load site config file if present (not committed; holds paths + secrets).
if [ -f "$PROJECT_DIR/slurm/auton.env" ]; then
    set -a; source "$PROJECT_DIR/slurm/auton.env"; set +a
fi

cd "$PROJECT_DIR"

export PATH="$ENV_PATH/bin:$PATH"
export CONDA_PREFIX="$ENV_PATH"
PYTHON_BIN="$ENV_PATH/bin/python3"

export HF_HOME="${HF_HOME:-$PROJECT_DIR/.cache/huggingface}"
export TMPDIR="${TMPDIR:-$PROJECT_DIR/tmp}"
export RAY_TMPDIR="$TMPDIR"
mkdir -p "$HF_HOME" "$TMPDIR" "$PROJECT_DIR/logs"

# WANDB_API_KEY is expected from the environment / auton.env — do not hardcode it.
: "${WANDB_API_KEY:?set WANDB_API_KEY in slurm/auton.env or the submit env}"

# ---------------------------------------------------------------------------
# System limits + stale Ray cleanup
# ---------------------------------------------------------------------------
ulimit -n 65535 || true
ulimit -u 65535 || true

echo "=== Cleaning up stale Ray processes ==="
$PYTHON_BIN -m ray stop --force 2>/dev/null || true
for pat in "ray::" raylet gcs_server plasma_store dashboard; do
    pkill -9 -f "$pat" 2>/dev/null || true
done
sleep 3
rm -rf /tmp/ray "${TMPDIR}/ray" 2>/dev/null || true

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
export NUM_GPUS_PER_NODE="${NUM_GPUS_PER_NODE:-4}"
unset ROCR_VISIBLE_DEVICES || true
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-$(seq -s, 0 $((NUM_GPUS_PER_NODE-1)))}"
export VLLM_USE_V1=1
export VERL_AUTO_PADDING=TRUE
export PYTHONUNBUFFERED=1

# ---------------------------------------------------------------------------
# Per-job agent I/O + game logs (same convention as the old sbatch).
# ---------------------------------------------------------------------------
JOB_ID="${SLURM_JOB_ID:-local_$(date +%s)}"
export VERL_AGENT_IO_LOG_PATH="$PROJECT_DIR/logs/agent_model_${JOB_ID}.log"
export VERL_AGENT_IO_LOG_FULL_PROMPT=0
export VERL_AGENT_EPISODE_LOG_PATH="$PROJECT_DIR/logs/episode_log_${JOB_ID}.jsonl"
export VERL_GAME_LOG_PATH="$PROJECT_DIR/logs/game_log_${JOB_ID}.log"
: > "$VERL_AGENT_IO_LOG_PATH"

echo "=== Job ${JOB_ID} on ${SLURMD_NODENAME:-local} — $(date) ==="
echo "PROJECT_DIR=$PROJECT_DIR  ENV_PATH=$ENV_PATH  GPUs=$NUM_GPUS_PER_NODE"
nvidia-smi -L 2>/dev/null || echo "WARN: nvidia-smi unavailable"
