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

set -euo pipefail

# ============================================================================
# EXPERIMENT NOTES
# Edit these strings before submitting a run. They are printed at the top of
# logs/frank_<jobid>.out so each run documents what changed.
# ============================================================================

EXP_NOTES=(
    "Model: Qwen3-4B; Env changes: no termination on all voted no consensus"
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

cd "$PROJECT_DIR"

export PATH="$ENV_PATH/bin:$PATH"
export CONDA_PREFIX="$ENV_PATH"

PYTHON_BIN="$ENV_PATH/bin/python3"

export HF_HOME="/zfsauton/scratch/frankwu2/.cache/huggingface"
export TMPDIR="/zfsauton/scratch/frankwu2/tmp"
export RAY_TMPDIR="$TMPDIR"
mkdir -p "$HF_HOME" "$TMPDIR" logs

export WANDB_API_KEY="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"

# ============================================================================
# SYSTEM LIMITS & RAY
# ============================================================================

ulimit -n 65535 || true
ulimit -u 65535 || true

echo "=== Cleaning up stale Ray processes ==="
$PYTHON_BIN -m ray stop --force 2>/dev/null || true
# Kill all Ray-related processes by name (more robust than just "ray::")
pkill -9 -f "ray::"        2>/dev/null || true
pkill -9 -f "raylet"       2>/dev/null || true
pkill -9 -f "gcs_server"   2>/dev/null || true
pkill -9 -f "plasma_store" 2>/dev/null || true
pkill -9 -f "dashboard"    2>/dev/null || true
sleep 3  # give the OS time to release ports before starting a fresh Ray instance
rm -rf /tmp/ray 2>/dev/null || true
rm -rf "${TMPDIR}/ray" 2>/dev/null || true

export RAY_NUM_CPUS=${SLURM_CPUS_PER_TASK}
export RAY_INCLUDE_DASHBOARD=0
export RAY_DISABLE_DASHBOARD=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export RAY_raylet_startup_timeout_ms=120000
export RAY_gcs_server_request_timeout_seconds=60
export RAY_BACKEND_LOG_LEVEL=warning

# ============================================================================
# GPU & vLLM
# ============================================================================

NUM_GPUS_PER_NODE=4
unset ROCR_VISIBLE_DEVICES
export CUDA_VISIBLE_DEVICES=$(seq -s, 0 $((NUM_GPUS_PER_NODE-1)))

export VLLM_USE_V1=1
export VERL_AUTO_PADDING=TRUE
export PYTHONUNBUFFERED=1  # flush Python stdout immediately so .out logs are readable

echo "SLURM-assigned CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"
nvidia-smi -L || echo "WARN: nvidia-smi failed"

# ============================================================================
# AGENT I/O & GAME LOGGING
# ============================================================================

LOG_PATH="$PROJECT_DIR/logs/agent_model_train_auton_${SLURM_JOB_ID}.log"
mkdir -p "$(dirname "$LOG_PATH")"
: > "$LOG_PATH"
export VERL_AGENT_IO_LOG_PATH="$LOG_PATH"
export VERL_AGENT_IO_LOG_FULL_PROMPT=0
export VERL_AGENT_EPISODE_LOG_PATH="$PROJECT_DIR/logs/episode_log_train_auton_${SLURM_JOB_ID}.jsonl"
export VERL_GAME_LOG_PATH="$PROJECT_DIR/logs/game_log_train_auton_${SLURM_JOB_ID}.log"

# ============================================================================
# HYPERPARAMETERS
# ============================================================================

NUM_ENVS=32
MODEL_PATH="${MODEL_PATH:-Qwen/Qwen3-4B}"
ENABLE_THINKING="${ENABLE_THINKING:-false}"
VAL_BATCH_SIZE="${VAL_BATCH_SIZE:-64}"
VAL_BEFORE_TRAIN="${VAL_BEFORE_TRAIN:-false}"
BATCH_SIZE=256
MINI_BATCH_SIZE=$((BATCH_SIZE))
MICRO_BATCH_SIZE=4
FORWARD_BATCH_SIZE=$((4 * MICRO_BATCH_SIZE))
OFFLOAD=false
PPO_EPOCHS=2
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
echo "PPO Epochs: $PPO_EPOCHS"
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
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=${MICRO_BATCH_SIZE} \
    actor_rollout_ref.actor.ppo_max_token_len_per_gpu=16384 \
    actor_rollout_ref.actor.use_kl_loss=False \
    actor_rollout_ref.actor.ppo_epochs=${PPO_EPOCHS} \
    actor_rollout_ref.actor.entropy_coeff=0.001 \
    actor_rollout_ref.actor.fsdp_config.param_offload=${OFFLOAD} \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=${OFFLOAD} \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=${FORWARD_BATCH_SIZE} \
    actor_rollout_ref.ref.log_prob_max_token_len_per_gpu=16384 \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    algorithm.use_kl_in_reward=True \
    trainer.balance_batch=False \
    trainer.critic_warmup=10 \
    trainer.critic_warmup_batch_repeat_times=40 \
    trainer.critic_warmup_batch_divide_ratio=4 \
    trainer.logger='["console","wandb"]' \
    trainer.project_name=wait_ratio_exps \
    trainer.experiment_name="frank_auton_${SLURM_JOB_ID}" \
    trainer.n_gpus_per_node=${NUM_GPUS_PER_NODE} \
    trainer.nnodes=1 \
    trainer.save_freq=-1 \
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
    critic.ppo_micro_batch_size_per_gpu=${MICRO_BATCH_SIZE} \
    critic.ppo_mini_batch_size=${MINI_BATCH_SIZE} \
    critic.ppo_max_token_len_per_gpu=16384 \
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
