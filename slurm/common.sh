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
export CHECKPOINT_ROOT="${CHECKPOINT_ROOT:-$PROJECT_DIR/checkpoints}"
mkdir -p "$HF_HOME" "$TMPDIR" "$CHECKPOINT_ROOT" "$PROJECT_DIR/logs"

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

# Reject allocations whose GPUs span CPU/NUMA sockets. Such allocations made
# FSDP collectives 5-10x slower in prior runs. Requeue while excluding each
# fragmented node; ALLOW_SPLIT_GPUS=1 disables the guard for a deliberate run.
echo "=== GPU topology ==="
scontrol show job -d "$SLURM_JOB_ID" 2>/dev/null | grep -oE 'GRES=[^ ]+' || true
echo "SLURM_JOB_GPUS=${SLURM_JOB_GPUS:-unset}"
nvidia-smi topo -m || true

VISIBLE_GPU_SELECTOR=()
GPU_TOPOLOGY_IDS="${SLURM_JOB_GPUS:-$CUDA_VISIBLE_DEVICES}"
if [ -n "$GPU_TOPOLOGY_IDS" ] && [ "$GPU_TOPOLOGY_IDS" != "NoDevFiles" ]; then
    VISIBLE_GPU_SELECTOR=(-i "$GPU_TOPOLOGY_IDS")
fi

GPU_NUMA_NODES=$( { nvidia-smi "${VISIBLE_GPU_SELECTOR[@]}" --query-gpu=pci.bus_id --format=csv,noheader | while read -r bus; do
    dev="0000:$(echo "$bus" | cut -d: -f2- | tr '[:upper:]' '[:lower:]')"
    cat "/sys/bus/pci/devices/$dev/numa_node" 2>/dev/null || echo "?"
done | sort -u; } || true )
echo "Distinct GPU NUMA nodes: $(echo "$GPU_NUMA_NODES" | tr '\n' ' ')"

if [ "$(echo "$GPU_NUMA_NODES" | grep -cE '^[0-9]+$')" -gt 1 ] && [ "${ALLOW_SPLIT_GPUS:-0}" != "1" ]; then
    echo "FATAL: allocated GPUs span multiple NUMA domains; training would be ~5-10x slower."
    RESTARTS="${SLURM_RESTART_COUNT:-0}"
    if [ "$RESTARTS" -lt "${MAX_SPLIT_GPU_REQUEUES:-5}" ]; then
        PREV_EXC=$(scontrol show job "$SLURM_JOB_ID" | grep -oE 'ExcNodeList=[^ ]+' | cut -d= -f2 || true)
        NEW_EXC="$SLURMD_NODENAME"
        if [ -n "$PREV_EXC" ] && [ "$PREV_EXC" != "(null)" ]; then
            NEW_EXC="$PREV_EXC,$SLURMD_NODENAME"
        fi
        echo "Requeue attempt $((RESTARTS + 1)): excluding node(s) $NEW_EXC"
        if scontrol requeue "$SLURM_JOB_ID"; then
            scontrol update JobId="$SLURM_JOB_ID" ExcNodeList="$NEW_EXC" \
                || echo "WARN: could not set ExcNodeList; retry may land on the same node"
            sleep 30
            exit 0
        fi
        echo "WARN: requeue failed"
    else
        echo "Giving up after $RESTARTS requeue attempts."
    fi
    echo "Resubmit with an exclusion, or set ALLOW_SPLIT_GPUS=1 to accept this allocation."
    exit 1
fi

# ---------------------------------------------------------------------------
# Per-job agent I/O and game logs.
# ---------------------------------------------------------------------------
export VERL_AGENT_IO_LOG_PATH="$PROJECT_DIR/logs/agent_model_${JOB_ID}.log"
export VERL_AGENT_IO_LOG_FULL_PROMPT=0
export VERL_AGENT_EPISODE_LOG_PATH="$PROJECT_DIR/logs/episode_log_${JOB_ID}.jsonl"
export VERL_GAME_LOG_PATH="$PROJECT_DIR/logs/game_log_${JOB_ID}.log"
export VERL_PROFILE_AGENT_LOOP="${VERL_PROFILE_AGENT_LOOP:-1}"
: > "$VERL_AGENT_IO_LOG_PATH"

echo "=== Job ${JOB_ID} on ${SLURMD_NODENAME:-local} — $(date) ==="
echo "PROJECT_DIR=$PROJECT_DIR  ENV_PATH=$ENV_PATH  GPUs=$NUM_GPUS_PER_NODE  Ray CPUs=$RAY_NUM_CPUS"
echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
nvidia-smi -L 2>/dev/null || echo "WARN: nvidia-smi unavailable"
