# Haiku-to-Qwen3 SFT sweep plan

## Goal

Test whether supervised fine-tuning Qwen3-4B on clean, socially optimal Haiku
self-play improves the socially optimal outcome rate before RL, and determine
whether the main constraint is teacher-data volume, training exposure, or the
length of the teacher's private reasoning.

This is a screening study, not a final benchmark. The primary model-selection
metric is socially optimal rate in fresh environment rollouts. Validation loss
is a stability guardrail and debugging signal, not the selection target.

## Fixed data and experimental unit

- Teacher collection: 500 environment scenarios beginning at seed 10000.
- Accepted data: 351 clean socially optimal episodes; 316 training scenarios
  and 35 validation scenarios.
- SFT unit: one professor decision. The full 316-scenario training set contains
  1,028 decision rows; validation contains 114 rows.
- A scenario is one resolved environment configuration plus one seed. All turns
  from a scenario remain in the same split.
- Training subsets are deterministic and nested: `raw25` (79 scenarios) is a
  subset of `raw50` (158), which is a subset of `raw100` (316).
- Every arm uses the same 35 held-out validation scenarios. `compact100` uses
  compact targets for those scenarios, so its validation loss is not directly
  comparable in scale to raw-target validation loss.
- Training seeds (10000 and above) and evaluation seeds (0 through 499) do not
  overlap.

## Initial sweep

All arms use Qwen/Qwen3-4B, full-parameter FSDP2 bf16 training, global batch
size 32, micro-batch size 1 per GPU, maximum sequence length 4608, cosine
schedule, 3% warmup, and learning rate 5e-6.

| Arm | Dataset | Exposure | Purpose |
|---|---|---:|---|
| A | `raw25` | 1 epoch / 7 steps | Small-data point |
| B | `raw50` | 1 epoch / 16 steps | Medium-data point |
| C8 | `raw100` | 8 steps | Existing smoke checkpoint |
| C16 | `raw100` | 16 steps | Mid-epoch exposure point |
| C32 | `raw100` | 1 epoch / 32 steps | Full-data point |
| D | `compact100` | 1 epoch / 32 steps | Compact-target ablation |

C16 and C32 resume from the existing C8 checkpoint, whose optimizer and
scheduler state is retained. The smoke run initialized the scheduler for the
full 32-step epoch, so this continuation is schedule-consistent. C16/C32 and
all other sweep arms save model shards only. Optimizer state is not retained
for runs that are not intended to resume.

The compact ablation changes only assistant targets. Later prompts still
contain the raw teacher thoughts captured during the original trajectory, so
this is a cheap, deliberately labeled target-only ablation rather than a fully
trajectory-consistent compact rollout. If it performs well, the next step is a
new teacher collection in which compacted outputs are passed to `env.step`,
because private reasoning changes ticker time and therefore turn order.

## Compact-target construction

For each teacher output:

1. Use only the final well-formed `<THINK>...</THINK>` block.
2. Parse the unchanged action suffix and its voted/proposed student.
3. Split reasoning into sentences and bullet clauses; discard headings,
   bookkeeping fragments, and meta-planning such as "let me analyze."
4. Score action-relevant rationale, favoring the selected student, decision
   verbs, consensus language, and explicit utility/welfare reasoning.
5. Keep at most two coherent sentences within 64 Qwen tokens. Never keep an
   arbitrary token tail that starts or ends mid-fragment.
6. Preserve the action suffix exactly.

The dataset build emits an audit file with raw/compact examples and verifies
that every action suffix is unchanged.

## Evaluation protocol

Use one stochastic sample per scenario, the same seed for every model, the
non-`corr0` hiring configuration, Qwen3 tokenization for environment dynamics,
temperature 1.0, and no best-of-N selection.

1. Run 20 seeds for serving, format, and gross-behavior sanity.
2. Extend every surviving arm and the unfine-tuned Qwen3-4B baseline to the
   same 200 seeds.
3. Select the best one or two SFT checkpoints using paired outcomes and extend
   only those checkpoints plus the baseline to 500 seeds. Resume the same
   output files so the first 200 seeds are not rerun.

Primary metric: socially optimal rate. Secondary metrics: consensus rate,
action-valid episode rate, welfare efficiency, mean turns, public tokens, and
model output tokens. Report Wilson intervals per model and paired differences
against the baseline (paired bootstrap interval plus discordant-pair test).

## Conditional follow-ups

- Train the best raw-data arm for two epochs from the base model only if C32
  clearly improves over C16. This must be a fresh 64-step run so the cosine
  schedule is correct; do not resume the one-epoch schedule.
- Add learning-rate arms at 2e-6 and 1e-5 only if the 5e-6 results are poor or
  ambiguous. The first sweep is a data/exposure sweep, not a factorial search.
- If `raw25`, `raw50`, and `raw100` are statistically indistinguishable, more
  teacher collection is low priority.
- If performance rises with data size, collect beyond 500 scenarios.
- If C16 beats C32, prefer less exposure and investigate overfitting.
- If compact targets win or preserve quality with substantially fewer output
  tokens, collect trajectory-consistent compact teacher rollouts next.

## Storage and reproducibility

- Existing resumable C8 checkpoint: approximately 23 GB including optimizer.
- Model-only FSDP checkpoint: approximately 8 GB each.
- Initial expected checkpoint use: approximately 63 GB for C8 plus A, B, C16,
  C32, and D. Merged Hugging Face copies require approximately another 8 GB
  each while retained.
- Dataset reports record source hashes, selected scenario IDs, row counts,
  target-token statistics, and expected optimizer steps.
- Use a stable sweep tag for checkpoint, merged-model, evaluation, and log
  paths. Launchers refuse to overwrite nonempty outputs by default.
- Four-GPU training jobs include a GPU-topology guard. Cross-NUMA FSDP
  allocations are rejected/requeued because the smoke run landed across CPU
  sockets and its 41-minute timing is not representative of a good placement.

## Execution order

1. Build and inspect `raw25`, `raw50`, `raw100`, and `compact100`.
2. Submit the four-arm initial training array.
3. Merge A, B, C8, C16, C32, and D model checkpoints to Hugging Face format.
4. Run 20-seed sanity evaluation, then the common 200-seed screen.
5. Compare paired results and extend the baseline plus the best one or two
   checkpoints to 500 seeds.
6. Decide whether any conditional follow-up is justified.
