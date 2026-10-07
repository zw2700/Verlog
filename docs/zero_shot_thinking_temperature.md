# Qwen3-4B zero-shot thinking × temperature runbook

This is an inference-only 2×2 experiment for `async_ticker_admissions`. It does
not train or update model weights.

The primary comparison is qualitative: does Qwen's native private thinking
produce a different interaction strategy from the literal `<THINK>...</THINK>`
reasoning protocol enforced by the environment? Temperature is the second
factor. Matrix jobs retain private reasoning in their private research
artifacts for paired trace comparison, but native reasoning is stripped before
the visible action is sent back to the environment.

## Fixed defaults

- model: `Qwen/Qwen3-4B`
- base temperature: `1.0` (the canonical training rollout temperature)
- high temperature: `1.3`
- top-p: `1.0`
- max output tokens: `4096`, shared by all cells
- vLLM context length: `16384`, shared by all cells
- concurrent episodes per model server: `8` (explicit `--episode-workers`)
- seeds: consecutive and paired across all cells
- environment: 3 professors, 5 students, 500 shared tokens, 5 features,
  vote threshold 0.5, 50 steps, fixed turn order, random-permutation
  preferences, and no termination merely because everyone voted without
  consensus

The historical job 14988 analysis identifies a Qwen3-4B baseline but does not
contain complete run provenance. Temperature 1.0 is therefore anchored to the
canonical training rollout config and current local-vLLM launcher rather than
claimed as a fully reconstructed historical setting.

## Build commands without submission

Each command creates a manifest and prints the four independent `sbatch`
commands. Add `--submit` only on Rhea when jobs should actually be submitted.

```bash
python3 scripts/launch_zero_shot_matrix.py --preset smoke --run-id zs-smoke
python3 scripts/launch_zero_shot_matrix.py --preset pilot --run-id zs-pilot
python3 scripts/launch_zero_shot_matrix.py --preset full --run-id zs-full
```

Preset sizes are 3, 100, and 500 paired seeds per cell. Override with
`--num-episodes N` without changing code.

The 3-seed smoke is only an interface check; it is not evidence about model
quality. The first decision-grade comparison uses the 100-seed pilot (400
episodes total). The shared 4096-token output allowance was selected after
diagnostic runs at 512 and 1024 tokens showed native Qwen generations
repeatedly exhausting the allowance before emitting a visible action.

All experiment presets, including smoke, use `general / qos_general`. Do not
submit these experiment cells to the debug partition.

## Rhea execution

From the project checkout:

```bash
mkdir -p logs artifacts/zero-shot-thinking
python3 scripts/launch_zero_shot_matrix.py \
  --preset smoke \
  --run-id zs-smoke \
  --submit
```

After all four cells complete:

```bash
python3 analysis/compute_zero_shot_matrix.py \
  --manifest artifacts/zero-shot-thinking/zs-smoke/manifest.json
```

Inspect `analysis/matrix_summary.md`, the four metadata files, and
`analysis/qualitative_trace_pairs.json`. Native cells must show
`result_summary.native_reasoning_observed=true` and must still produce visible
action tags. If native generations frequently use the full output allowance
before an action, increase `--max-output-tokens` and rerun all four cells.

Once the smoke is healthy:

```bash
python3 scripts/launch_zero_shot_matrix.py \
  --preset pilot \
  --run-id zs-pilot \
  --submit
```

Analyze it with the same command, pointing `--manifest` at the pilot manifest.

## Decision rule

Use the `no_pair_shares_top` rows as the primary result. A condition succeeds
only if it reduces instant decisions and improves welfare or social optimality
without materially increasing stalls, format errors, or invalid actions.
Longer discussion by itself is not a success.
