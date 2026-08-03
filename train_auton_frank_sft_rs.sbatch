#!/bin/bash
#SBATCH --job-name=marl_frank
#SBATCH --output=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/frank_%j.out
#SBATCH --error=/zfsauton2/home/frankwu2/unscripted/Verlog/logs/frank_%j.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=200G
#SBATCH --time=47:59:00
#SBATCH --gres=gpu:a6000:4
#SBATCH --exclude=gpu25
#SBATCH --gres-flags=enforce-binding
#SBATCH --requeue

set -euo pipefail

# ============================================================================
# EXPERIMENT NOTES
# Edit these strings before submitting a run. They are printed at the top of
# logs/frank_<jobid>.out so each run documents what changed.
# ============================================================================

EXP_NOTES=(
    "Model: Qwen3-4B initialized from the merged Qwen self-rejection-sampled SFT raw100 step-16 checkpoint (316 training scenarios / 1,809 decision turns)."
    "Locked 500-seed RL-decoding evaluation: 46.6% socially optimal and 99.2% valid episodes versus 45.0% SO for base (+1.6 pp; paired 95% CI -2.6 to +5.8 pp); user-selected for exploratory RL."
    "Environment and objective settings match train_auton_frank.sbatch (no termination on all-voted-no consensus, random-permutation professor preferences)."
    "Episode jsonl sharded per worker"
    "Critic model-only snapshots saved at steps 1, 5, 10, 30, and 75; the actor model, optimizer, and extra state are saved at steps 30 and 75."
    # "Retains the SFT launcher performance settings: ppo_epochs=1, ppo_max_token_len=12288, and critic_warmup=5."
)

echo "=== Experiment Notes ==="
if [ "${#EXP_NOTES[@]}" -eq 0 ]; then
    echo "- (none)"
else
    for note in "${EXP_NOTES[@]}"; do
        echo "- $note"
    done
fi
echo "========================"

echo "=== Job Information ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
echo "Start time: $(date)"
echo "Working directory: $SLURM_SUBMIT_DIR"
echo "======================="

# ============================================================================
# PATHS
# ============================================================================

PROJECT_DIR="/zfsauton2/home/frankwu2/unscripted/Verlog"
ENV_PATH="/zfsauton/scratch/cpulling/conda_envs/verlog"
DATA_DIR="/zfsauton/scratch/cpulling/data/gsm8k"
CHECKPOINT_ROOT="/zfsauton/scratch/frankwu2/unscripted/Verlog/checkpoints"

cd "$PROJECT_DIR"

export PATH="$ENV_PATH/bin:$PATH"
export CONDA_PREFIX="$ENV_PATH"

PYTHON_BIN="$ENV_PATH/bin/python3"

export HF_HOME="/zfsauton/scratch/frankwu2/.cache/huggingface"
export TMPDIR="/zfsauton/scratch/frankwu2/tmp"
# Ray's session dir (Unix-domain sockets + many small files) must live on fast
# node-local disk, NOT the NFS $TMPDIR: NFS socket/metadata latency makes the
# raylet/GCS/dashboard startup time out ("node timed out during startup", job
# 22425). /tmp is node-local tmpfs here. Job-scoped so co-tenant jobs on a shared
# node never collide -- the sibling launchers used RAY_TMPDIR="$TMPDIR", one path
# shared by every run, which is what made the `rm -rf` in the old cleanup below
# destructive to a co-tenant job (job 23033). Removed on exit by the trap so tmpfs
# does not accumulate stale dirs across jobs. Ray appends /ray/session_* here.
export RAY_TMPDIR="/tmp/ray_${USER:-$(id -un)}_${SLURM_JOB_ID:-$$}"
trap 'rm -rf "$RAY_TMPDIR" 2>/dev/null || true' EXIT
mkdir -p "$HF_HOME" "$TMPDIR" "$CHECKPOINT_ROOT" logs

export WANDB_API_KEY="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"
# wandb-core writes its handshake port file under $TMPDIR (NFS here); the parent
# polls it for only 30s by default and intermittently times out under NFS
# close-to-open latency (ServicePollForTokenError, e.g. job 22316). Give the
# service backend more slack.
export WANDB__SERVICE_WAIT="${WANDB__SERVICE_WAIT:-300}"

# ============================================================================
# SYSTEM LIMITS & RAY
# ============================================================================

ulimit -n 65535 || true
ulimit -u 65535 || true

echo "=== Cleaning up stale Ray processes ==="
# ----------------------------------------------------------------------------
# Job 23033 was SIGKILLed 2 s after job 23086 -- another of this user's runs --
# started on the other half of gpu25 (23033 held GPUs IDX 0-3, 23086 got 4-7).
# The old cleanup here ran `ray stop --force` plus bare `pkill -9 -f <pattern>`.
# Both are node-wide and user-wide: SLURM cgroups constrain devices and memory,
# they do not hide our own PIDs from our own signals. So a starting job reaped
# the Ray actors, raylet and GCS of a sibling job 7.5 h into training, and
# `pkill -9 -f dashboard` matched the sibling's *driver*, whose argv contains
# `+ray_kwargs.ray_init.include_dashboard=False` -- pkill -f matches the whole
# command line, so the flag that disables the dashboard is what killed it.
#
# Scope every kill by cgroup instead. /proc/<pid>/cgroup (cgroup v2 here) reads
# 0::/system.slice/slurmstepd.scope/job_23350/step_extern/user/task_special, so a
# live SLURM job is identifiable by its /job_<id>/ component:
#   /job_$SLURM_JOB_ID/ -> ours (e.g. a requeue reusing this JobId) -> kill
#   /job_<other>/       -> co-tenant job, possibly another user's  -> NEVER kill
#   no /job_<n>/        -> outside any job cgroup, a real orphan   -> kill
# The last class is the one worth catching: it is what held 43.9 GiB of our card
# in job 22807 while SLURM still believed the GPU was free.
#
# `ray stop --force` is gone -- it also kills by node-wide process name, and at
# this point in the script we own no Ray processes for it to clean up, so it
# could only ever hit a co-tenant. The bare "dashboard" pattern is narrowed to
# Ray's own dashboard module. Set SKIP_RAY_CLEANUP=1 to skip the sweep entirely.
# ----------------------------------------------------------------------------
if [ "${SKIP_RAY_CLEANUP:-0}" != "1" ]; then
    RAY_KILLED=0
    RAY_SPARED=0
    for pat in 'ray::' 'raylet' 'gcs_server' 'plasma_store' 'ray[./]dashboard'; do
        for pid in $(pgrep -u "$(id -u)" -f "$pat" 2>/dev/null || true); do
            if [ "$pid" = "$$" ]; then continue; fi
            # newlines -> "/" so every cgroup line ends in a slash and the
            # /job_<id>/ patterns below cannot match a prefix (job_2303 vs 23033)
            cg=$(tr '\n' '/' 2>/dev/null < "/proc/$pid/cgroup") || continue
            case "$cg" in
                *"/job_${SLURM_JOB_ID:-none}/"*)
                    if kill -9 "$pid" 2>/dev/null; then RAY_KILLED=$((RAY_KILLED + 1)); fi
                    ;;
                */job_[0-9]*/*)
                    RAY_SPARED=$((RAY_SPARED + 1))
                    ;;
                *)
                    echo "  orphan outside any SLURM cgroup: pid=$pid pattern=$pat -> killing"
                    if kill -9 "$pid" 2>/dev/null; then RAY_KILLED=$((RAY_KILLED + 1)); fi
                    ;;
            esac
        done
    done
    echo "Ray cleanup: killed $RAY_KILLED, spared $RAY_SPARED owned by other live SLURM jobs."
    if [ "$RAY_KILLED" -gt 0 ]; then
        sleep 3  # give the OS time to release ports before starting a fresh Ray
    fi
fi

# Start from a clean node-local Ray dir (also covers a requeue reusing this
# JobId). Only this job's own dir is touched -- never the shared /tmp/ray or
# "$TMPDIR/ray" that the old cleanup wiped, which a co-tenant job may still be
# using: jobs launched from an older snapshot of this script run with
# RAY_TMPDIR="$TMPDIR", so `rm -rf "$TMPDIR/ray"` deletes their live session dir.
rm -rf "$RAY_TMPDIR" 2>/dev/null || true
mkdir -p "$RAY_TMPDIR"

export RAY_NUM_CPUS=${SLURM_CPUS_PER_TASK}
# NOTE: these two are NOT honored by this Ray version (the dashboard still starts
# and crashes). The reliable disable is include_dashboard=False passed to
# ray.init via the +ray_kwargs.ray_init.include_dashboard=False override below.
export RAY_INCLUDE_DASHBOARD=0
export RAY_DISABLE_DASHBOARD=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
# On busy nodes the raylet is CPU-starved and misses the default node-registration
# window ("GCS cannot find the node ... registration may not be complete before
# the timeout", jobs 22425/22526). Give startup more slack.
export RAY_raylet_startup_timeout_ms=300000
export RAY_raylet_start_wait_time_s=300
export RAY_gcs_server_request_timeout_seconds=60
export RAY_BACKEND_LOG_LEVEL=warning

# ============================================================================
# GPU & vLLM
# ============================================================================

NUM_GPUS_PER_NODE=4
unset ROCR_VISIBLE_DEVICES
if [ -z "${CUDA_VISIBLE_DEVICES:-}" ]; then
    export CUDA_VISIBLE_DEVICES=$(seq -s, 0 $((NUM_GPUS_PER_NODE-1)))
    echo "WARN: SLURM did not set CUDA_VISIBLE_DEVICES; falling back to ${CUDA_VISIBLE_DEVICES}."
else
    echo "Using SLURM-provided CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES}"
fi

export VLLM_USE_V1=1
export VERL_AUTO_PADDING=TRUE
export PYTHONUNBUFFERED=1  # flush Python stdout immediately so .out logs are readable

echo "Job CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"
nvidia-smi -L || echo "WARN: nvidia-smi failed"

# ============================================================================
# GPU TOPOLOGY GUARD
# Jobs 15930/16085 were allocated GPUs split across the node's two NUMA/PCIe
# domains (GRES IDX 2-3,5-6 on gpu29). FSDP all-gather/reduce-scatter then
# crosses the socket interconnect. Measured on job 20539 (IDX 1,4,6-7, a 1+3
# split) against 17323 (IDX 0-3, same socket): per-token update_critic 3.1x,
# critic forward 2.5x, ref forward 1.9x, while vLLM generation (TP=1, no
# cross-GPU collectives) was unaffected -- i.e. the cost scales with collective
# volume, and update_critic alone was 78% of step time.
# Abort early instead of burning the full walltime; ALLOW_SPLIT_GPUS=1 skips.
# ============================================================================

echo "=== GPU topology ==="
scontrol show job -d "$SLURM_JOB_ID" 2>/dev/null | grep -oE 'GRES=[^ ]+' || true
echo "SLURM_JOB_GPUS=${SLURM_JOB_GPUS:-unset}"
nvidia-smi topo -m || true

# Query ALL visible GPUs (no -i selector). SLURM's cgroup already restricts
# nvidia-smi to this job's cards AND renumbers them 0..N-1, so selecting by the
# global SLURM_JOB_GPUS ids read the wrong devices, or none: with IDX 4-7 every
# id was out of range and the loop yielded "?" (job 22807); with IDX 1,4,6-7 and
# IDX 2-3,5-6 only the in-range ids resolved, collapsing to a single NUMA node
# so the guard passed on genuinely split allocations (jobs 20539, 23016).
GPU_NUMA_NODES=$( { nvidia-smi --query-gpu=pci.bus_id --format=csv,noheader | while read -r bus; do
    dev="0000:$(echo "$bus" | cut -d: -f2- | tr '[:upper:]' '[:lower:]')"
    cat "/sys/bus/pci/devices/$dev/numa_node" 2>/dev/null || echo "?"
done | sort -u; } || true )
echo "Distinct GPU NUMA nodes: $(echo "$GPU_NUMA_NODES" | tr '\n' ' ')"

if [ "$(echo "$GPU_NUMA_NODES" | grep -cE '^[0-9]+$')" -gt 1 ] && [ "${ALLOW_SPLIT_GPUS:-0}" != "1" ]; then
    echo "FATAL: allocated GPUs span multiple NUMA domains; training would be ~5-10x slower."
    # SLURM on this cluster cannot honor same-socket GPU requests (gres.conf
    # pools all 8 GPUs across both sockets, 'S:0-1', so
    # --gres-flags=enforce-binding is a no-op). Reroll instead: requeue this
    # job excluding the fragmented node, up to MAX_SPLIT_GPU_REQUEUES times.
    RESTARTS="${SLURM_RESTART_COUNT:-0}"
    if [ "$RESTARTS" -lt "${MAX_SPLIT_GPU_REQUEUES:-5}" ]; then
        PREV_EXC=$(scontrol show job "$SLURM_JOB_ID" | grep -oE 'ExcNodeList=[^ ]+' | cut -d= -f2 || true)
        NEW_EXC="$SLURMD_NODENAME"
        if [ -n "$PREV_EXC" ] && [ "$PREV_EXC" != "(null)" ]; then
            NEW_EXC="$PREV_EXC,$SLURMD_NODENAME"
        fi
        echo "Requeue attempt $((RESTARTS + 1)): excluding node(s) $NEW_EXC"
        # Plain requeue (no hold): job 17323 got stuck in held state for a day
        # when SLURM killed the script between requeuehold and release. The
        # ExcNodeList update below is best-effort in the brief pending window;
        # if it loses the race the retry may land on this node again and simply
        # re-roll (costs one attempt), which beats sticking in hold.
        if scontrol requeue "$SLURM_JOB_ID"; then
            scontrol update JobId="$SLURM_JOB_ID" ExcNodeList="$NEW_EXC" \
                || echo "WARN: could not set ExcNodeList; retry may land on the same node"
            sleep 30  # let SLURM tear down this (now-requeued) run
            exit 0
        fi
        echo "WARN: requeue failed"
    else
        echo "Giving up after $RESTARTS requeue attempts."
    fi
    echo "Resubmit manually (sbatch --exclude=...), or set ALLOW_SPLIT_GPUS=1 to proceed anyway."
    exit 1
fi

# ============================================================================
# GPU CONTENTION GUARD
# Job 22807 died at critic init on gpu29 when a foreign process (PID 105945)
# held 43.9/47.4 GiB of our GPU 0, leaving 59 MiB free. SLURM *does* allocate
# GPUs exclusively here (cgroup.conf ConstrainDevices=yes, PrologFlags=Contain,
# gres.conf maps each GPU to its own /dev/nvidiaN), but that is enforced at
# device-file open, not by memory accounting: a process that outlives its job
# (e.g. wedged in D-state on NFS, so SIGKILL cannot reap it) or that enters the
# node outside any job cgroup keeps its CUDA context while SLURM believes the
# card is free. Our colocated actor+critic+ref+vLLM footprint needs almost the
# whole card, so bail out early and reroll to a clean node instead of burning
# ~3 min of startup only to OOM. Reuses the NUMA guard's requeue/ExcNodeList
# mechanism and shares its reroll budget (SLURM_RESTART_COUNT /
# MAX_SPLIT_GPU_REQUEUES). Tune the bar with GPU_MIN_FREE_MIB; skip the check
# with ALLOW_BUSY_GPUS=1.
# NOTE: best-effort — a process that grabs memory AFTER this check but before
# our critic init can still cause an OOM; this catches the already-resident
# case (as in 22807). Query all visible GPUs (no -i) for the same reason as the
# NUMA guard above; memory.free is device-level, so it reflects any other
# process resident on the physical card.
# ============================================================================

if [ "${ALLOW_BUSY_GPUS:-0}" != "1" ]; then
    GPU_MIN_FREE_MIB="${GPU_MIN_FREE_MIB:-40000}"
    BUSY_GPUS=""
    while read -r idx free; do
        [ -z "$free" ] && continue
        case "$free" in ''|*[!0-9]*) continue ;; esac
        if [ "$free" -lt "$GPU_MIN_FREE_MIB" ]; then
            BUSY_GPUS="$BUSY_GPUS ${idx}:${free}MiB"
        fi
    done < <(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits 2>/dev/null | tr -d ' ' | tr ',' ' ')

    if [ -n "$BUSY_GPUS" ]; then
        echo "FATAL: allocated GPU(s) already busy (free < ${GPU_MIN_FREE_MIB}MiB):$BUSY_GPUS"
        echo "A foreign process is resident on our physical GPU; critic init would OOM."
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
                sleep 30  # let SLURM tear down this (now-requeued) run
                exit 0
            fi
            echo "WARN: requeue failed"
        else
            echo "Giving up after $RESTARTS requeue attempts."
        fi
        echo "Resubmit manually (sbatch --exclude=...), or set ALLOW_BUSY_GPUS=1 to proceed anyway."
        exit 1
    fi
    echo "GPU contention check passed (all allocated GPUs have >= ${GPU_MIN_FREE_MIB}MiB free)."
fi

# ============================================================================
# AGENT I/O & GAME LOGGING
# ============================================================================

LOG_PATH="$PROJECT_DIR/logs/agent_model_train_auton_${SLURM_JOB_ID}.log"
mkdir -p "$(dirname "$LOG_PATH")"
: > "$LOG_PATH"
export VERL_AGENT_IO_LOG_PATH="$LOG_PATH"
export VERL_AGENT_IO_LOG_FULL_PROMPT=0
# Episode rows are sharded per worker under a run-specific directory to avoid
# NFS flock contention; merge with `cat episode_log_<id>/*.worker*.jsonl`.
export VERL_AGENT_EPISODE_LOG_PATH="$PROJECT_DIR/logs/episode_log_train_auton_${SLURM_JOB_ID}.jsonl"
export VERL_GAME_LOG_PATH="$PROJECT_DIR/logs/game_log_train_auton_${SLURM_JOB_ID}.log"
# Per-episode phase timing ([AGENT_LOOP_PROFILE ...] lines in .out, ~1/episode)
# to verify where rollout time goes; set 0 once gen speed is confirmed healthy.
export VERL_PROFILE_AGENT_LOOP="${VERL_PROFILE_AGENT_LOOP:-1}"

# ============================================================================
# HYPERPARAMETERS
# ============================================================================

NUM_ENVS=32
MODEL_PATH="${MODEL_PATH:-/zfsauton/scratch/frankwu2/unscripted/Verlog/models/sft/qwen3_self_rs_sweep_v1/raw100_step16}"
ENABLE_THINKING="${ENABLE_THINKING:-false}"
VAL_BATCH_SIZE="${VAL_BATCH_SIZE:-64}"
VAL_BEFORE_TRAIN="${VAL_BEFORE_TRAIN:-false}"
BATCH_SIZE="${BATCH_SIZE:-256}"
MINI_BATCH_SIZE=$((BATCH_SIZE))
ACTOR_MICRO_BATCH_SIZE="${ACTOR_MICRO_BATCH_SIZE:-2}"
CRITIC_MICRO_BATCH_SIZE="${CRITIC_MICRO_BATCH_SIZE:-4}"
FORWARD_BATCH_SIZE="${FORWARD_BATCH_SIZE:-16}"
# Token-based micro-batching: micro batch sizes above are ignored while this is
# true; each micro-batch is packed up to PPO_MAX_TOKEN_LEN tokens instead.
# 12288 (up from 8192): fewer, larger micro-batches -> less per-batch FSDP
# all-gather/reduce-scatter overhead on the update phases (~83% of step time
# under the verbose SFT checkpoint, cf. job 20539). Watch the first post-warmup
# actor update for OOM on the 48GB A6000s (micro=4 OOMed update_actor backward
# in 15856); drop back to 8192 if it OOMs.
USE_DYNAMIC_BSZ="${USE_DYNAMIC_BSZ:-True}"
PPO_MAX_TOKEN_LEN="${PPO_MAX_TOKEN_LEN:-8192}"
OFFLOAD=false
# 1 (down from 2): each PPO epoch is a full fwd+bwd over the whole batch, and
# ppo_mini_batch_size==train_batch_size so there is one minibatch -> the epoch
# count multiplies the dominant update phases directly. 1 ~halves update time;
# costs reusing each rollout once instead of twice.
PPO_EPOCHS=2
# 5 (down from 10): critic vf_loss plateaus by warmup step 5 in job 20539
# (0.44->0.073->0.037->0.024->0.019, flat/rising after); steps 6-10 were ~18h
# of near-zero marginal critic gain under the long SFT sequences.
CRITIC_WARMUP="${CRITIC_WARMUP:-10}"
# repeat=10/divide=1: generate exactly what the critic trains on (2,560
# samples/step). The old 40/4 combo generated 4x more and dropped 3/4 of it -
# a leftover from when warmup generated once at step 1 and reused the pool.
CRITIC_WARMUP_BATCH_REPEAT_TIMES="${CRITIC_WARMUP_BATCH_REPEAT_TIMES:-10}"
CRITIC_WARMUP_BATCH_DIVIDE_RATIO="${CRITIC_WARMUP_BATCH_DIVIDE_RATIO:-1}"
STUDENTS_PER_BATCH="${STUDENTS_PER_BATCH:-5}"
TERMINATE_ON_ALL_VOTED_NO_CONSENSUS="${TERMINATE_ON_ALL_VOTED_NO_CONSENSUS:-false}"
PROFESSOR_PREFERENCE_MODE="${PROFESSOR_PREFERENCE_MODE:-random_permutation}"
PREFERENCE_CORRELATION_THRESHOLD="${PREFERENCE_CORRELATION_THRESHOLD:-0.0}"
PREFERENCE_REJECTION_MAX_ATTEMPTS="${PREFERENCE_REJECTION_MAX_ATTEMPTS:-1000}"

echo "=== Training Configuration ==="
echo "GPUs: $NUM_GPUS_PER_NODE"
echo "CPUs: $SLURM_CPUS_PER_TASK"
echo "Model path: $MODEL_PATH"
echo "Chat template enable_thinking: $ENABLE_THINKING"
echo "Validation batch size: $VAL_BATCH_SIZE"
echo "Validation before train: $VAL_BEFORE_TRAIN"
echo "Num Envs: $NUM_ENVS"
echo "Batch Size: $BATCH_SIZE"
echo "Actor PPO Micro Batch Size: $ACTOR_MICRO_BATCH_SIZE"
echo "Critic PPO Micro Batch Size: $CRITIC_MICRO_BATCH_SIZE"
echo "Forward Micro Batch Size: $FORWARD_BATCH_SIZE"
echo "Use dynamic batch size: $USE_DYNAMIC_BSZ"
echo "PPO max token len per GPU: $PPO_MAX_TOKEN_LEN"
echo "PPO Epochs: $PPO_EPOCHS"
echo "Critic warmup: $CRITIC_WARMUP"
echo "Critic warmup batch repeat times: $CRITIC_WARMUP_BATCH_REPEAT_TIMES"
echo "Critic warmup batch divide ratio: $CRITIC_WARMUP_BATCH_DIVIDE_RATIO"
echo "Students per batch: $STUDENTS_PER_BATCH"
echo "Terminate on all voted no consensus: $TERMINATE_ON_ALL_VOTED_NO_CONSENSUS"
echo "Professor preference mode: $PROFESSOR_PREFERENCE_MODE"
echo "Preference correlation threshold: $PREFERENCE_CORRELATION_THRESHOLD"
echo "Preference rejection max attempts: $PREFERENCE_REJECTION_MAX_ATTEMPTS"
echo "=============================="

# ============================================================================
# EXP LOGGING (requires claude-tools submodule)
# ============================================================================

# source "$PROJECT_DIR/claude-tools/exp_logging/sbatch_logging.sh"
# EXP_WHAT_CHANGED="train_auton full run"
# EXP_WANDB_PROJECT=wait_ratio_exps
# EXP_NAME="train_auton_frank_${SLURM_JOB_ID}"
# EXP_PROJECT_DIR="$PROJECT_DIR"
# EXP_MODEL=$MODEL_PATH
# EXP_ADV_ESTIMATOR=gae
# EXP_BATCH_SIZE=$BATCH_SIZE
# EXP_NUM_ENVS=$NUM_ENVS
# EXP_GPUS=$NUM_GPUS_PER_NODE
# EXP_ACTOR_LR=1e-6
# EXP_CRITIC_LR=1e-5
# EXP_PPO_EPOCHS=$PPO_EPOCHS
# EXP_CRITIC_WARMUP_STEPS=10
# EXP_CRITIC_WARMUP_REPEAT=40
# EXP_ROLLOUT_N=1
# EXP_TOKEN_BUDGET=1000
# EXP_STUDENTS_PER_BATCH=5
# EXP_FEATURE_DIM=5
# exp_log_start
# trap exp_log_finalize EXIT

# ============================================================================
# TRAINING
# ============================================================================

$PYTHON_BIN -m verl.trainer.main_ppo \
    --config-path="$PROJECT_DIR/examples/sglang_multiturn/config" \
    --config-name='gsm8k_multiturn_grpo' \
    algorithm.adv_estimator=gae \
    data.train_batch_size=${BATCH_SIZE} \
    data.max_prompt_length=4096 \
    data.max_response_length=512 \
    data.val_batch_size=${VAL_BATCH_SIZE} \
    data.filter_overlong_prompts=True \
    data.truncation='error' \
    data.return_raw_chat=True \
    +data.apply_chat_template_kwargs.enable_thinking=${ENABLE_THINKING} \
    data.train_files="$DATA_DIR/train.parquet" \
    data.val_files="$DATA_DIR/test.parquet" \
    actor_rollout_ref.rollout.mode=async \
    actor_rollout_ref.rollout.agent.default_agent_loop=multi_tool_agent_loop \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.4 \
    actor_rollout_ref.rollout.n=1 \
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=${FORWARD_BATCH_SIZE} \
    actor_rollout_ref.rollout.log_prob_max_token_len_per_gpu=16384 \
    actor_rollout_ref.rollout.agent.num_workers=${NUM_ENVS} \
    actor_rollout_ref.model.path=${MODEL_PATH} \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.actor.ppo_mini_batch_size=${MINI_BATCH_SIZE} \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=${ACTOR_MICRO_BATCH_SIZE} \
    actor_rollout_ref.actor.use_dynamic_bsz=${USE_DYNAMIC_BSZ} \
    actor_rollout_ref.actor.ppo_max_token_len_per_gpu=${PPO_MAX_TOKEN_LEN} \
    actor_rollout_ref.actor.use_kl_loss=False \
    actor_rollout_ref.actor.ppo_epochs=${PPO_EPOCHS} \
    actor_rollout_ref.actor.entropy_coeff=0.001 \
    actor_rollout_ref.actor.fsdp_config.param_offload=${OFFLOAD} \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=${OFFLOAD} \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=${FORWARD_BATCH_SIZE} \
    actor_rollout_ref.ref.log_prob_max_token_len_per_gpu=16384 \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    algorithm.use_kl_in_reward=True \
    +ray_kwargs.ray_init.include_dashboard=False \
    trainer.balance_batch=False \
    trainer.critic_warmup=${CRITIC_WARMUP} \
    trainer.critic_warmup_batch_repeat_times=${CRITIC_WARMUP_BATCH_REPEAT_TIMES} \
    trainer.critic_warmup_batch_divide_ratio=${CRITIC_WARMUP_BATCH_DIVIDE_RATIO} \
    trainer.logger='["console","wandb"]' \
    trainer.project_name=wait_ratio_exps \
    trainer.experiment_name="frank_auton_${SLURM_JOB_ID}" \
    trainer.default_local_dir="${CHECKPOINT_ROOT}/wait_ratio_exps/frank_auton_${SLURM_JOB_ID}" \
    trainer.n_gpus_per_node=${NUM_GPUS_PER_NODE} \
    trainer.nnodes=1 \
    trainer.save_freq=-1 \
    trainer.actor_save_steps='[30,75]' \
    trainer.critic_save_steps='[1,5,10,30,75]' \
    trainer.save_actor_checkpoint=True \
    trainer.save_critic_checkpoint=True \
    critic.checkpoint.save_contents='["model"]' \
    critic.checkpoint.load_contents='["model"]' \
    trainer.test_freq=-1 \
    trainer.total_epochs=15 \
    trainer.total_training_steps=75 \
    trainer.val_before_train=${VAL_BEFORE_TRAIN} \
    envs.num_envs=${NUM_ENVS} \
    envs.env_name=async_ticker_admissions \
    +envs.env_config.professor_ids='["prof_1","prof_2","prof_3"]' \
    +envs.env_config.students_per_batch=${STUDENTS_PER_BATCH} \
    +envs.env_config.token_budget=500 \
    +envs.env_config.feature_dim=5 \
    +envs.env_config.vote_threshold=0.5 \
    +envs.env_config.max_steps=50 \
    +envs.env_config.terminate_on_all_voted_no_consensus=${TERMINATE_ON_ALL_VOTED_NO_CONSENSUS} \
    +envs.env_config.professor_preference_mode=${PROFESSOR_PREFERENCE_MODE} \
    +envs.env_config.preference_correlation_threshold=${PREFERENCE_CORRELATION_THRESHOLD} \
    +envs.env_config.preference_rejection_max_attempts=${PREFERENCE_REJECTION_MAX_ATTEMPTS} \
    critic.optim.lr=1e-5 \
    critic.model.use_remove_padding=True \
    critic.model.path=${MODEL_PATH} \
    critic.model.enable_gradient_checkpointing=True \
    critic.ppo_epochs=${PPO_EPOCHS} \
    critic.ppo_micro_batch_size_per_gpu=${CRITIC_MICRO_BATCH_SIZE} \
    critic.ppo_mini_batch_size=${MINI_BATCH_SIZE} \
    critic.use_dynamic_bsz=${USE_DYNAMIC_BSZ} \
    critic.ppo_max_token_len_per_gpu=${PPO_MAX_TOKEN_LEN} \
    critic.forward_max_token_len_per_gpu=16384 \
    critic.forward_micro_batch_size_per_gpu=${FORWARD_BATCH_SIZE} \
    critic.model.fsdp_config.param_offload=${OFFLOAD} \
    critic.model.fsdp_config.optimizer_offload=${OFFLOAD} \
    "$@"

EXIT_CODE=$?

echo "=== Job Completion ==="
echo "End time: $(date)"
echo "Exit code: $EXIT_CODE"
echo "======================"

exit $EXIT_CODE
