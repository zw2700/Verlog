#!/bin/bash
#SBATCH --job-name=q3_4b_old_parity_sync
#SBATCH --output=/zfsauton/scratch/cpulling/verlog_v08_data/logs/old_parity_sync_4b_%j.out
#SBATCH --error=/zfsauton/scratch/cpulling/verlog_v08_data/logs/old_parity_sync_4b_%j.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=400G
#SBATCH --time=11:59:00
#SBATCH --gres=gpu:a6000:4
set -uo pipefail
# ============================================================================
# TIER-2 NUMERICAL-STABILITY run: OLD BRANCH side (verl-0.6, Verlog merge-jun26-merged).
# Faithful replay of train_auton_frank.sbatch (dense Qwen3-4B) with 3 fixes:
#   (1) key read from ~/.wandb_key, never hardcoded;
#   (2) PYTHONPATH shadows the CORA/Verlog editable install so `verl` == cpulling/Verlog;
#   (3) project/experiment renamed for pairing with the port run.
# NO global ray-kill: jobs share a6000 nodes, so pkill raylet would kill co-tenant
# jobs (e.g. CORA). A unique RAY_TMPDIR is enough.
# Pair: sbatch_train_qwen3_4b_dense_parity.sbatch (port). Compare in verl_parity_qwen3_4b.
# ============================================================================
PROJECT_DIR=/zfsauton/scratch/cpulling/Verlog
ENV_PATH=/zfsauton/scratch/cpulling/conda_envs/verlog
DATA_DIR=/zfsauton/scratch/cpulling/data/gsm8k
cd "$PROJECT_DIR"
export PATH="$ENV_PATH/bin:$PATH"; PY="$ENV_PATH/bin/python3"
export PYTHONPATH="$PROJECT_DIR"                       # shadow the CORA/Verlog editable install
export HF_HOME=/zfsauton/scratch/cpulling/.cache/huggingface
export TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 VLLM_USE_V1=1 VERL_AUTO_PADDING=TRUE PYTHONUNBUFFERED=1
export RAY_TMPDIR=/tmp/r${SLURM_JOB_ID}
export RAY_INCLUDE_DASHBOARD=0 RAY_DISABLE_DASHBOARD=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export WANDB_API_KEY=$(cat ~/.wandb_key 2>/dev/null)   # never hardcode the key
export WANDB_START_METHOD=thread
export WANDB_ENTITY=aseo-carnegie-mellon-university
ulimit -n 65535 || true; ulimit -u 65535 || true

NUM_ENVS=32
MODEL_PATH="Qwen/Qwen3-4B"
BATCH_SIZE=256; MINI_BATCH_SIZE=256; MICRO_BATCH_SIZE=4; FORWARD_BATCH_SIZE=16
STUDENTS_PER_BATCH=5; PPO_EPOCHS=2
SEED=${SEED:-1}

echo "verl from: $($PY -c 'import verl,os;print(os.path.dirname(verl.__file__))' 2>/dev/null)"

$PY -m verl.trainer.main_ppo \
    --config-path="$PROJECT_DIR/examples/sglang_multiturn/config" \
    --config-name='gsm8k_multiturn_grpo' \
    algorithm.adv_estimator=gae \
    algorithm.use_kl_in_reward=True \
    data.train_batch_size=${BATCH_SIZE} \
    data.max_prompt_length=4096 \
    data.max_response_length=512 \
    data.val_batch_size=64 \
    data.filter_overlong_prompts=True \
    data.truncation='error' \
    data.return_raw_chat=True \
    +data.apply_chat_template_kwargs.enable_thinking=false \
    data.train_files="$DATA_DIR/train.parquet" \
    data.val_files="$DATA_DIR/test.parquet" \
    actor_rollout_ref.rollout.mode=sync \
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
    actor_rollout_ref.actor.fsdp_config.param_offload=false \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=false \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=${FORWARD_BATCH_SIZE} \
    actor_rollout_ref.ref.log_prob_max_token_len_per_gpu=16384 \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    trainer.balance_batch=False \
    trainer.critic_warmup=10 \
    trainer.critic_warmup_batch_repeat_times=40 \
    trainer.critic_warmup_batch_divide_ratio=4 \
    trainer.logger='["console","wandb"]' \
    trainer.project_name=verl_parity_qwen3_4b \
    trainer.experiment_name="old_dense4b_sync_${SLURM_JOB_ID}" \
    trainer.n_gpus_per_node=4 \
    trainer.nnodes=1 \
    trainer.save_freq=-1 \
    trainer.test_freq=-1 \
    trainer.total_epochs=15 \
    trainer.total_training_steps=75 \
    trainer.val_before_train=false \
    envs.num_envs=${NUM_ENVS} \
    envs.env_name=async_ticker_admissions \
    +envs.env_config.professor_ids='["prof_1","prof_2","prof_3"]' \
    +envs.env_config.students_per_batch=${STUDENTS_PER_BATCH} \
    +envs.env_config.token_budget=500 \
    +envs.env_config.feature_dim=5 \
    +envs.env_config.vote_threshold=0.5 \
    +envs.env_config.max_steps=50 \
    +envs.env_config.seed=${SEED} \
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
    critic.model.fsdp_config.param_offload=false \
    critic.model.fsdp_config.optimizer_offload=false
echo "=== OLD DENSE PARITY EXIT=$? ==="
