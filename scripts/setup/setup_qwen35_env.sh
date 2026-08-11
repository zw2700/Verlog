#!/usr/bin/env bash
# =============================================================================
# setup_qwen35_env.sh — reproduce the Qwen3.5 + verl-0.8 (Verlog) training env.
#
# Stack:  Python 3.12 · torch 2.11.0+cu130 · vLLM 0.24 · transformers git-main(pin)
#         + Qwen3.5 hybrid GDN/Mamba kernels (flash-attn, flash-linear-attention,
#         causal-conv1d) · verl installed editable from this repo.
#
# Ships NO large files — everything is downloaded/built by pip. The exact
# transitive versions live in requirements-qwen35.lock.txt (next to this script).
#
# Usage:   bash scripts/setup/setup_qwen35_env.sh [env_name]      # default: qwen35
# Then:    conda activate <env_name>
# =============================================================================
set -euo pipefail
ENV_NAME="${1:-qwen35}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"        # this script lives in scripts/setup/
LOCK="$HERE/requirements-qwen35.lock.txt"
TF_PIN="1da9d1d433c301f59027668b25f42d317ec742df"   # transformers git-main commit w/ Qwen3.5

command -v conda >/dev/null 2>&1 || { echo "ERROR: conda not found on PATH."; exit 1; }
source "$(conda info --base)/etc/profile.d/conda.sh"

echo "[1/6] create conda env '$ENV_NAME' (python 3.12)"
conda create -y -n "$ENV_NAME" python=3.12
conda activate "$ENV_NAME"
python -m pip install -U pip wheel setuptools packaging ninja

echo "[2/6] torch 2.11.0 + CUDA 13.0  (install FIRST — the kernels compile against it)"
pip install torch==2.11.0 torchvision==0.26.0 torchaudio==2.11.0 \
    --index-url https://download.pytorch.org/whl/cu130

echo "[3/6] transformers @ git-main pin (Qwen3.5 modeling)"
pip install "transformers @ git+https://github.com/huggingface/transformers.git@${TF_PIN}"

echo "[4/6] vLLM 0.24 + flashinfer (rollout/inference)"
pip install vllm==0.24.0 flashinfer-python==0.6.12

echo "[5/6] Qwen3.5 hybrid kernels (GDN / Mamba)"
echo "      NOTE: these may source-build against torch 2.11/cu130. If the build"
echo "      errors on missing nvcc, load a CUDA-13 toolkit first, e.g.:"
echo "        module load cuda-13   ||   conda install -y -c nvidia cuda-toolkit=13"
echo "      then re-run this script (steps are idempotent)."
pip install --no-build-isolation \
    flash-attn==2.8.3 causal-conv1d==1.5.3 flash-linear-attention==0.5.1

echo "[6/6] remaining pinned deps (lock) + verl (editable, this repo)"
# Everything already installed above is 'already satisfied' and skipped by pip.
pip install -r "$LOCK"
pip install -e "$REPO_ROOT" --no-deps

echo
echo "=============================================================================="
echo " DONE.  conda activate $ENV_NAME"
echo " Export these at runtime (see README_SETUP.md / your sbatch):"
echo "   export VLLM_USE_V1=1 FLA_TILELANG=0"
echo "   export TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1   # if models pre-cached"
echo "=============================================================================="
echo "Import sanity check:"
python - <<'PY'
import importlib, torch
print("  torch", torch.__version__, "| cuda", torch.version.cuda)
for m in ["vllm","transformers","fla","causal_conv1d","flash_attn","verl"]:
    try:
        importlib.import_module(m); print(f"  {m:14s} OK")
    except Exception as e:
        print(f"  {m:14s} FAIL: {e}")
PY
