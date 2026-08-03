# Haiku-to-Qwen SFT pipeline

This directory is an isolated pipeline for collecting successful Haiku self-play,
turning it into decision-level SFT examples, training Qwen with VERL, and evaluating
the resulting policy on locked seeds. It reuses the provider clients from
`scripts/rollout_frontier.py`; the only provider change is local-vLLM top-k support.

## Qwen self-rejection-sampling replication

The same infrastructure can train Qwen3-4B on clean socially optimal rollouts
sampled from the unfine-tuned Qwen3-4B policy. This experiment has its own paths
and does not modify the Haiku datasets or checkpoints.

Collect 500 training scenarios with up to four attempts each. The launcher starts
a local vLLM server and explicitly uses the RL sampling policy: temperature 1,
top-p 1, top-k -1, no chat-template thinking, and at most 512 output tokens.

```bash
sbatch scripts/sft/collect_self_rollouts.sbatch
```

The output summary is
`outputs/sft/qwen3_self_rs_v1/attempts.summary.json`. We want at least 375 clean
successful scenarios before selecting 351. If the four-attempt run falls short,
resume only the unresolved scenarios with four additional attempts:

```bash
MAX_ATTEMPTS_PER_SCENARIO=8 sbatch scripts/sft/collect_self_rollouts.sbatch
```

If eight attempts still produce fewer than 351 usable scenarios, extend the same
artifact to 600 seeds:

```bash
NUM_SCENARIOS=600 MAX_ATTEMPTS_PER_SCENARIO=8 \
  sbatch scripts/sft/collect_self_rollouts.sbatch
```

After collection, build exactly 351 selected trajectories (316 train and 35
validation), plus nested raw25/raw50/raw100 and compact100 arms. This is a CPU
step and normally runs directly on the login/CPU host:

```bash
bash scripts/sft/build_self_rs_datasets.sh
```

The builder selects the shortest clean success per scenario, hash-ranks excess
successful scenarios, refuses to proceed with fewer than 351, and writes an
overlap report against the Haiku scenario set. The sweep lives at
`outputs/sft/qwen3_self_rs_v1/sweep_datasets_v1`.

Train the four arms sequentially on four A6000s:

```bash
sbatch scripts/sft/train_self_rs_sweep.sbatch
```

The arms use the same fixed exposure as the Haiku sweep: raw25 step 7, raw50
step 16, raw100 steps 8/16/32 along one 32-step cosine-schedule trajectory, and
compact100 step 32. Fixed steps are intentional because Qwen's successful
trajectories may contain more decision rows than Haiku's.

Merge all six evaluation checkpoints with one array submission:

```bash
sbatch scripts/sft/merge_self_rs_sweep.sbatch
```

Then reuse the existing evaluation array under the self-RS tag:

```bash
MODEL_ROOT=/zfsauton/scratch/frankwu2/unscripted/Verlog/models/sft/qwen3_self_rs_sweep_v1 \
SWEEP_TAG=qwen3_self_rs_sweep_v1 NUM_SCENARIOS=20 \
  sbatch scripts/sft/evaluate_sweep.sbatch
```

## Experimental unit

A **scenario** is one `(resolved environment configuration, environment seed)` pair.
The seed fixes the student batch, professor utilities, and environment randomness.
An **attempt** reruns that same scenario with a fresh stochastic teacher completion.
All attempted episodes are retained in JSONL.

`--stop-on-socially-optimal` controls adaptive retries during collection. With the
default setting, a scenario stops after its first *clean* socially optimal attempt.
Clean means consensus on the global rank-1 student, welfare efficiency 1, no format
or invalid-action errors, nonempty outputs, and no provider length truncation. The
dataset builder applies the same strict predicate; the collection flag is not an
acceptance criterion by itself.

The target tokenizer is passed into the environment. This matters because the hiring
environment's shared 500-token communication budget counts public `<GROUP>` text,
while the asynchronous ticker advances using the full generated output, including
text in `<THINK>`. A rollout collected with Haiku's tokenizer would therefore not
reproduce the timing seen by a Qwen actor. Collect target-specific rollouts if the
candidate models use materially different tokenization.

## 1. Collect teacher attempts

Copy `sft.env.example` to `sft.env` and add the provider credential. The real
`sft.env` is ignored by git and is loaded automatically. You can instead reuse the
existing root configuration directly with `--env-file rollout_frontier.env`.
Explicit CLI arguments override values loaded from the file, while already-exported
process variables take precedence over file values.

Start with a 500-scenario pilot, then use about 2,000 successful scenarios for the
first full run. At a 72.7% per-attempt success rate, four adaptive attempts need about
1.37 raw episodes per scenario on average and cover about 99.4% of scenarios before
the stricter validity filters. Check the emitted summary rather than assuming those
rates transfer exactly.

```bash
python -m scripts.sft.collect_teacher_rollouts \
  --target-tokenizer Qwen/Qwen3-4B \
  --no-target-enable-thinking \
  --temperature 1.0 \
  --num-workers 8 \
  --seed-base 10000 \
  --num-scenarios 500 \
  --max-attempts-per-scenario 4 \
  --output-jsonl outputs/sft/haiku_qwen3_pilot/attempts.jsonl
```

Use `--resume` to continue an interrupted output file. The collector rejects a
resume if its environment-config hash differs. The checked-in
`configs/hiring_v1.json` is the default non-`corr0` setup; pass `--env-config` only
for an intentional, separately named experiment.

On the cluster, submit the equivalent 500-scenario pilot with:

```bash
sbatch scripts/sft/collect_teacher_rollouts.sbatch
```

The launcher defaults to `rollout_frontier.env`. Override settings at submission
time when needed, for example:

```bash
SFT_ENV_FILE="$PWD/scripts/sft/sft.env" NUM_WORKERS=4 \
  sbatch scripts/sft/collect_teacher_rollouts.sbatch --resume
```

## 2. Build SFT Parquet files

Each selected episode becomes one row per professor decision. A row contains the
exact captured system/user messages followed by one assistant target. Scenario-level
splitting keeps all decisions from an episode on the same side of the split. If a
scenario has multiple clean attempts, the builder selects the shortest one, breaking
ties by public tokens, output tokens, then attempt number.

```bash
python -m scripts.sft.build_dataset \
  --input outputs/sft/haiku_qwen3_pilot/attempts.jsonl \
  --output-dir outputs/sft/haiku_qwen3_pilot/dataset_raw \
  --target-tokenizer Qwen/Qwen3-4B \
  --no-target-enable-thinking \
  --target-format raw \
  --validation-fraction 0.1
```

The main run should begin with `raw`, which preserves the teacher output exactly.
`--target-format compact-think --max-think-tokens 64` is a useful target-only
ablation: it selects one or two action-aligned rationale sentences from the final
valid thinking block and preserves the post-`</THINK>` action text exactly. Later
prompts still contain the original raw teacher history, so this does not recreate
the ticker dynamics of a genuinely compact trajectory. The builder writes:

- `train.parquet` and `validation.parquet` for VERL's `MultiTurnSFTDataset`;
- `selected_episodes.jsonl`, an auditable scenario-to-split manifest;
- `dataset_report.json`, including coverage, filtering reasons, agent balance, and
  target-tokenizer length distributions.

## 3. Train

The launcher defaults to one epoch, full-parameter FSDP2, bf16, learning rate
`5e-6`, global batch 32, and sequence length 4608. All defaults can be changed with
environment variables or trailing Hydra overrides.

Before a full run, submit the eight-step four-A6000 smoke test:

```bash
sbatch scripts/sft/train_smoke.sbatch
```

It uses the full sequence-length and batch configuration, performs final validation
and checkpoint writing, and stores its checkpoint under scratch. The job aborts if
Slurm allocates GPUs across both NUMA domains because that would make the timing
estimate unrepresentative. Resubmit if that guard fires.

```bash
NPROC_PER_NODE=4 \
SFT_EXPERIMENT_NAME=qwen3-4b-haiku-raw-pilot \
scripts/sft/train_sft.sh \
  Qwen/Qwen3-4B \
  outputs/sft/haiku_qwen3_pilot/dataset_raw \
  outputs/sft/haiku_qwen3_pilot/checkpoints
```

For a low-cost sanity check, train both one epoch and a smaller data subset before
committing to more epochs. The primary risks are overfitting teacher phrasing and
degrading general language behavior, so the first sweep should vary data size or
format before increasing epochs.

## 4. Current four-arm sweep

The complete rationale and decision rules are in [`sft_plan.md`](../../sft_plan.md).
The derived datasets have already been built at
`outputs/sft/haiku_qwen3_pilot/sweep_datasets_v1`. Recreate them only under a new
output root—the builder refuses to overwrite an existing sweep:

```bash
python -m scripts.sft.make_sweep_datasets \
  --source-dir outputs/sft/haiku_qwen3_pilot/dataset_raw \
  --output-root outputs/sft/haiku_qwen3_pilot/sweep_datasets_v1 \
  --target-tokenizer Qwen/Qwen3-4B \
  --subset-seed 1 \
  --max-think-tokens 64
```

Submit A=`raw25`, B=`raw50`, C=`raw100` resumed from the existing step-8 smoke
checkpoint, and D=`compact100` as a sequential four-task array:

```bash
sbatch scripts/sft/train_sweep.sbatch
```

The expected final checkpoints are:

- A: `haiku_qwen3_sweep_v1/raw25/global_step_7`
- B: `haiku_qwen3_sweep_v1/raw50/global_step_16`
- C16/C32: `haiku_qwen3_sweep_v1/raw100_steps16_32/global_step_{16,32}`
- D: `haiku_qwen3_sweep_v1/compact100/global_step_32`

They live under `/zfsauton/scratch/frankwu2/unscripted/Verlog/checkpoints/sft`.
All new checkpoints are model-only; only the existing smoke step 8 retains
optimizer state. The array refuses cross-NUMA four-GPU placements and attempts up
to five requeues on different nodes. `ALLOW_SPLIT_GPUS=1` is available only as an
explicit slower fallback.

Merge all six evaluation points (including the existing step 8) on CPU. For
example:

```bash
CKPT=/zfsauton/scratch/frankwu2/unscripted/Verlog/checkpoints/sft
sbatch scripts/sft/merge_checkpoint.sbatch "$CKPT/haiku_qwen3_sweep_v1/raw25/global_step_7" raw25_step7
sbatch scripts/sft/merge_checkpoint.sbatch "$CKPT/haiku_qwen3_sweep_v1/raw50/global_step_16" raw50_step16
sbatch scripts/sft/merge_checkpoint.sbatch "$CKPT/haiku_qwen3_smoke_18999/global_step_8" raw100_step8
sbatch scripts/sft/merge_checkpoint.sbatch "$CKPT/haiku_qwen3_sweep_v1/raw100_steps16_32/global_step_16" raw100_step16
sbatch scripts/sft/merge_checkpoint.sbatch "$CKPT/haiku_qwen3_sweep_v1/raw100_steps16_32/global_step_32" raw100_step32
sbatch scripts/sft/merge_checkpoint.sbatch "$CKPT/haiku_qwen3_sweep_v1/compact100/global_step_32" compact100_step32
```

## 5. Locked-seed evaluation

Create one seed file and reuse it for the base model, SFT model, and subsequent RL
checkpoints. Evaluation performs no best-of-N selection or success-conditioned retry.

```bash
seq 0 499 > outputs/sft/eval_seeds.txt

python -m scripts.sft.evaluate_policy \
  --provider local-vllm \
  --base-url http://127.0.0.1:8000/v1 \
  --model Qwen/Qwen3-4B \
  --target-tokenizer Qwen/Qwen3-4B \
  --no-target-enable-thinking \
  --temperature 1.0 \
  --num-workers 8 \
  --seeds-file outputs/sft/eval_seeds.txt \
  --output-jsonl outputs/sft/eval_qwen3_base.jsonl
```

Repeat with the served SFT checkpoint and a different output path. The summary
reports socially optimal and consensus rates with Wilson 95% intervals, action
validity, welfare efficiency, turns, and token usage. Keep collection seeds disjoint
from these evaluation seeds.

The Slurm launcher starts and stops a one-GPU vLLM server itself. Begin with the
base-model sanity run and one command per merged checkpoint:

```bash
MODEL_ROOT=/zfsauton/scratch/frankwu2/unscripted/Verlog/models/sft/haiku_qwen3_sweep_v1
EVAL_NUM_SCENARIOS=20 sbatch scripts/sft/evaluate_sft.sbatch Qwen/Qwen3-4B base
EVAL_NUM_SCENARIOS=20 sbatch scripts/sft/evaluate_sft.sbatch "$MODEL_ROOT/raw25_step7" raw25_step7
```

After checking formatting and server logs, repeat the same commands with
`EVAL_NUM_SCENARIOS=200`. The stable evaluation names cause the launcher to resume
the existing JSONL and add seeds 20–199. Later, extend only the base and selected
models with `EVAL_NUM_SCENARIOS=500`.

The complete seven-model 200-seed screen can instead be submitted as one Slurm
array. Existing 20-seed JSONLs are resumed automatically:

```bash
sbatch scripts/sft/evaluate_sweep.sbatch
```

Array tasks 0–6 correspond to base, raw25 step 7, raw50 step 16, raw100 steps
8/16/32, and compact100 step 32. Each task requests one A6000. Override the stage
only when intentional, for example `NUM_SCENARIOS=500 sbatch ...`; the planned
500-seed stage should normally include only selected finalists rather than all
seven models.

Compare completed, same-sized runs on CPU with paired outcomes:

```bash
EVAL_ROOT=outputs/sft/evaluations/haiku_qwen3_sweep_v1
python -m scripts.sft.compare_evaluations \
  --baseline base="$EVAL_ROOT/base/episodes.jsonl" \
  --candidate raw25_step7="$EVAL_ROOT/raw25_step7/episodes.jsonl" \
  --candidate raw50_step16="$EVAL_ROOT/raw50_step16/episodes.jsonl" \
  --candidate raw100_step8="$EVAL_ROOT/raw100_step8/episodes.jsonl" \
  --candidate raw100_step16="$EVAL_ROOT/raw100_step16/episodes.jsonl" \
  --candidate raw100_step32="$EVAL_ROOT/raw100_step32/episodes.jsonl" \
  --candidate compact100_step32="$EVAL_ROOT/compact100_step32/episodes.jsonl" \
  --num-scenarios 200 \
  --output-prefix "$EVAL_ROOT/comparison_200"
```
