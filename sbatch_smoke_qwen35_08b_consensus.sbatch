#!/bin/bash
#SBATCH --job-name=q35_08b_consensus_smoke
#SBATCH --output=/zfsauton/scratch/cpulling/verlog_v08_data/logs/consensus_smoke_%j.out
#SBATCH --error=/zfsauton/scratch/cpulling/verlog_v08_data/logs/consensus_smoke_%j.err
#SBATCH --partition=general
#SBATCH --qos=qos_general
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=200G
#SBATCH --time=03:59:00
#SBATCH --gres=gpu:a6000:2
set -uo pipefail
# ============================================================================
# END-TO-END SMOKE for the verl-0.8 Qwen3.5 consensus port (0.8B, env-driven multi-agent).
# This is the RUNTIME VALIDATION of the full rebuild: gae_dual + consensus_multi_agent AgentLoop +
# env-driven rollout + fit()-env-branch + Qwen3.5 routing. Expect first-run bugs to iterate on
# (Ray + async vLLM + FSDP + the new env path). NOTE: num_envs MUST equal rollout.agent.num_workers.
# Qwen3.5 requirements baked in: use_remove_padding=False, use_dynamic_bsz=False (GDN packed-seq IMA
# fix, verl #6549), token-TIS, KL-in-loss, sampling temp1/top_p1. reward_mode=individual.
# TODO(first run): confirm a train dataset parquet path for the dataloader (env mode ignores its
# content but the trainer still iterates train_dataloader). Point data.train_files at any small parquet.
# ============================================================================
cd /zfsauton2/home/cpulling/Verlog_v08
ENV_ROOT=/zfsauton/scratch/cpulling/conda_envs/qwen35
export PATH="$ENV_ROOT/bin:$PATH"; PY="$ENV_ROOT/bin/python3"
export HF_HOME=/zfsauton/scratch/cpulling/.cache/huggingface
export TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 VLLM_USE_V1=1 PYTHONUNBUFFERED=1 FLA_TILELANG=0
export TRITON_CACHE_DIR=/zfsauton/scratch/cpulling/.triton_cache
export PYTHONPATH=$PWD
export RAY_TMPDIR=/tmp/r${SLURM_JOB_ID}
export WANDB_API_KEY=$(cat ~/.wandb_key 2>/dev/null)

MODEL="Qwen/Qwen3.5-0.8B"
NUM_ENVS=4
DATA=/zfsauton/scratch/cpulling/data

$PY -m verl.trainer.main_ppo \
  algorithm.adv_estimator=gae_dual \
  algorithm.step_gamma=0.99 \
  algorithm.step_lam=0.95 \
  algorithm.use_kl_in_reward=False \
  algorithm.rollout_correction.rollout_is=token \
  algorithm.rollout_correction.rollout_is_threshold=2.0 \
  actor_rollout_ref.model.path="$MODEL" \
  actor_rollout_ref.rollout.name=vllm \
  actor_rollout_ref.rollout.n=1 \
  actor_rollout_ref.rollout.calculate_log_probs=True \
  actor_rollout_ref.rollout.gpu_memory_utilization=0.3 \
  actor_rollout_ref.rollout.enforce_eager=False \
  actor_rollout_ref.rollout.prompt_length=4096 \
  actor_rollout_ref.rollout.response_length=512 \
  actor_rollout_ref.rollout.max_model_len=8192 \
  data.max_prompt_length=4096 \
  data.max_response_length=512 \
  actor_rollout_ref.rollout.agent.default_agent_loop=consensus_multi_agent \
  actor_rollout_ref.rollout.agent.num_workers=$NUM_ENVS \
  actor_rollout_ref.actor.use_kl_loss=True \
  actor_rollout_ref.actor.kl_loss_coef=0.01 \
  actor_rollout_ref.actor.use_remove_padding=False \
  actor_rollout_ref.actor.use_dynamic_bsz=False \
  actor_rollout_ref.actor.ppo_mini_batch_size=16 \
  actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=1 \
  actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=1 \
  actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=1 \
  actor_rollout_ref.actor.optim.lr=1e-6 \
  critic.model.path="$MODEL" \
  critic.enable=True \
  critic.model.use_remove_padding=False \
  critic.use_dynamic_bsz=False \
  critic.ppo_micro_batch_size_per_gpu=1 \
  envs.env_name=async_ticker_admissions \
  envs.num_envs=$NUM_ENVS \
  envs.env_config.reward_mode=individual \
  data.train_batch_size=64 \
  data.train_files=$DATA/consensus_dummy.parquet \
  data.val_files=$DATA/consensus_dummy.parquet \
  trainer.critic_warmup=1 \
  trainer.total_training_steps=2 \
  trainer.total_epochs=1 \
  trainer.val_before_train=False \
  trainer.test_freq=-1 \
  trainer.save_freq=-1 \
  trainer.balance_batch=False \
  trainer.n_gpus_per_node=2 \
  trainer.nnodes=1 \
  trainer.project_name=verlog_qwen35_v08 \
  trainer.experiment_name=consensus_smoke_${SLURM_JOB_ID} \
  trainer.logger=[console]
echo "=== SMOKE EXIT=$? ==="
