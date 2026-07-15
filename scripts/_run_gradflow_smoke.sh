#!/bin/bash
cd /zfsauton2/home/cpulling/Verlog_v08
export HF_HOME=/zfsauton/scratch/cpulling/.cache/huggingface
export TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 FLA_TILELANG=0 PYTHONUNBUFFERED=1
export TRITON_CACHE_DIR=/zfsauton/scratch/cpulling/.triton_cache
export PYTHONPATH=$PWD
/zfsauton/scratch/cpulling/conda_envs/qwen35/bin/python3 scripts/smoke_qwen35_gradflow.py --model Qwen/Qwen3.5-0.8B --steps 12
