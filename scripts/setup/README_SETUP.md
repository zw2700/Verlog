# Qwen3.5 + verl-0.8 (Verlog) — environment setup

Reproduces the training/inference env with **no large files committed** — everything
is pip-installed/built. Exact versions are pinned in `requirements-qwen35.lock.txt`.

## 1. Clone (submodule is required!)

```bash
git clone --recurse-submodules -b verl_08_qwen35 git@github.com:zw2700/Verlog.git
cd Verlog
```

`--recurse-submodules` is **mandatory** — the environment (`verl/envs/hiring_env`) is a
git submodule. Without it you get `ModuleNotFoundError: verl.envs.hiring_env.env` at
rollout. If you already cloned without it: `git submodule update --init --recursive`.

## 2. Build the env

```bash
bash scripts/setup/setup_qwen35_env.sh            # creates conda env "qwen35"
conda activate qwen35
```

The script installs, in dependency order:

| step | what | why order matters |
|------|------|-------------------|
| 1 | conda env, python 3.12 | |
| 2 | **torch 2.11.0 + cu130** (`download.pytorch.org/whl/cu130`) | kernels compile against it — must be first |
| 3 | **transformers** @ git-main pin `1da9d1d…` | Qwen3.5 modeling code (not in a release yet) |
| 4 | vLLM 0.24 + flashinfer | rollout |
| 5 | **GDN/Mamba kernels**: flash-attn 2.8.3, flash-linear-attention 0.5.1, causal-conv1d 1.5.3 | Qwen3.5 hybrid attention; `--no-build-isolation` so they build against the torch from step 2 |
| 6 | rest of pins (`requirements-qwen35.lock.txt`) + `pip install -e .` | verl editable |

### CUDA toolkit for the kernels
`nvcc` is **not** required if prebuilt wheels exist for torch 2.11/cu130. If step 5
errors on a missing compiler, load a CUDA-13 toolkit and re-run (idempotent):

```bash
module load cuda-13        # cluster module, OR:
conda install -y -c nvidia cuda-toolkit=13
bash scripts/setup/setup_qwen35_env.sh
```

## 3. Runtime environment variables

Export these in your sbatch/launch (see the `sbatch_*` examples):

```bash
export VLLM_USE_V1=1          # vLLM v1 engine
export FLA_TILELANG=0         # skip tilelang JIT for flash-linear-attention (GDN)
export TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1   # if HF models are pre-cached
```

## 4. Qwen3.5-specific gotchas (already handled in the example sbatches)

- **GDN can't take packed sequences** → set `actor_rollout_ref.model.use_remove_padding=False`
  and `use_dynamic_bsz=False` (fixed micro-batch). Packing works for dense Qwen3 only.
- **Ray dashboard flakiness on shared nodes** → pass
  `+ray_kwargs.ray_init.include_dashboard=False` (see example sbatches) to avoid
  intermittent "node timed out during startup / GCS overloaded" at `ray.init`.
- Padded Qwen3.5 batches are VRAM-heavy: use `tensor_model_parallel_size≥2` to shard
  the vLLM replica across GPUs, or reduce batch, when OOMing in the actor update.

## 5. Verify

The setup script ends with an import check (torch/vllm/transformers/fla/verl → OK).
For an end-to-end check, run the 0.8B consensus smoke sbatch on 1–2 GPUs.
