# Qwen3.5-4B Best-Student Probe: 100-Trial vLLM Run

This note records the 100-trial diagnostic for `Qwen/Qwen3.5-4B`, served with an
isolated nightly vLLM environment on `auton-dgx2`.

The corresponding Qwen3.5 dense checkpoints for our previous 3B/7B question are
`Qwen/Qwen3.5-4B` and `Qwen/Qwen3.5-9B`. Their Hugging Face model cards list the
language-model parameter counts as 4B and 9B, respectively:
<https://huggingface.co/Qwen/Qwen3.5-4B> and
<https://huggingface.co/Qwen/Qwen3.5-9B>.

## Setup

- Date run: 2026-07-01
- Host: `auton-dgx2`
- Serving stack: isolated Python venv at `/home/mwilinsk/qwen35-vllm-venv`
- vLLM: `0.23.1rc1.dev693+g5c4db60f0`
- Model: `Qwen/Qwen3.5-4B`
- Endpoint during run: `http://127.0.0.1:8000/v1`
- Serving mode: `--language-model-only --enforce-eager`
- Prompt source: `AsyncTickerAdmissionsEnv._build_chat_messages`
- Prompt shape: one system message plus one user observation; the diagnostic
  instruction was appended to the env's existing user message.
- Trials: 100 distinct resets, seeds 0-99
- Professors: `prof_1`, `prof_2`, `prof_3`, cycled by trial
- Env config: 5 students, 5-dimensional profiles, token budget 1000,
  vote threshold 0.5

Two variants were run:

- Vote mode: ask the model to return
  `<THINK>short private reason</THINK><VOTE>N</VOTE>`.
- JSON/direct-answer mode: ask the model to identify the highest-utility
  student directly.

## Qwen3.5 Serving Notes

The previous repo vLLM stack (`vllm==0.10.0`, `transformers==4.55.4`) could not
serve Qwen3.5 because the checkpoint uses the new `qwen3_5` architecture. We
therefore used an isolated nightly vLLM venv rather than mutating the Verlog
training environment.

Two serving details mattered:

- Serving with `--reasoning-parser qwen3` returned `message.content = null` for
  this diagnostic while generated text appeared under `message.reasoning`; that
  made the original parser see every answer as unparseable.
- The clean run served without the reasoning parser and passed
  `chat_template_kwargs={"enable_thinking": false}` via the probe's
  `--disable-thinking` flag. This keeps the diagnostic comparable by preventing
  Qwen3.5 from spending the 128-token completion budget on a long hidden
  reasoning preamble.

## Results

### Vote Mode

- Completed calls: 100/100
- Parseable answers: 100/100
- Exact env top-1 accuracy: 94/100 = 0.94
- Displayed-table top accuracy: 96/100 = 0.96
- Exact misses: 6/100
- Real displayed-table misses: 4/100
- Displayed utility tie trials: 11/100
- Average utility regret: 0.0170
- Maximum utility regret: 1.1000

Real displayed-table misses:

- Seed 23, `prof_3`: gold 0, predicted 4, regret 0.1000.
- Seed 68, `prof_3`: gold 0, predicted 4, regret 0.1000.
- Seed 82, `prof_2`: gold 0, predicted 3, regret 1.1000.
- Seed 88, `prof_2`: gold 0, predicted 4, regret 0.4000.

### JSON / Direct-Answer Mode

- Completed calls: 100/100
- Parseable answers: 100/100
- Exact env top-1 accuracy: 94/100 = 0.94
- Displayed-table top accuracy: 96/100 = 0.96
- Exact misses: 6/100
- Real displayed-table misses: 4/100
- Displayed utility tie trials: 11/100
- Average utility regret: 0.0120
- Maximum utility regret: 0.8000

Real displayed-table misses:

- Seed 9, `prof_1`: gold 2, predicted 1, regret 0.8000.
- Seed 31, `prof_2`: gold 2, predicted 1, regret 0.2000.
- Seed 46, `prof_2`: gold 2, predicted 1, regret 0.1000.
- Seed 84, `prof_1`: gold 3, predicted 1, regret 0.1000.

## Comparison

Same-host 100-trial comparison at the time of this 4B run:

| Model | Mode | Exact Top-1 | Displayed-Top | Avg Regret | Max Regret |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen2.5-3B-Instruct | vote | 71/100 | 75/100 | 0.1340 | 1.6000 |
| Qwen2.5-3B-Instruct | JSON/direct | 68/100 | 71/100 | 0.1410 | 1.6000 |
| Qwen2.5-7B-Instruct | vote | 90/100 | 92/100 | 0.0210 | 0.6000 |
| Qwen2.5-7B-Instruct | JSON/direct | 96/100 | 97/100 | 0.0090 | 0.6000 |
| Qwen3.5-4B | vote | 94/100 | 96/100 | 0.0170 | 1.1000 |
| Qwen3.5-4B | JSON/direct | 94/100 | 96/100 | 0.0120 | 0.8000 |

Interpretation: moving from the exact Qwen2.5-3B training model to Qwen3.5-4B
substantially improves private-best identification. Qwen3.5-4B is already in the
same range as Qwen2.5-7B on this narrow diagnostic, though it still makes a few
real visible-table mistakes.

This supports the hypothesis that simply bumping model generation/model family
can reduce the individual private-utility identification bottleneck. It does not
yet prove that collaboration improves in full rollouts; that still needs the
same rollout-level metrics for timing, speaking, consensus, and social welfare.

## Follow-Up Status

The corresponding larger Qwen3.5 checkpoint, `Qwen/Qwen3.5-9B`, has now been
run on the same 100 seeds. We also added Qwen3-4B and Qwen3-8B controls.

Qwen3.5-9B results:

- Vote mode: 93/100 exact, 94/100 displayed-top, 6/100 real displayed misses,
  average regret 0.0140, maximum regret 0.5000.
- JSON/direct mode: 96/100 exact, 97/100 displayed-top, 3/100 real displayed
  misses, average regret 0.0040, maximum regret 0.2000.

The full generation comparison is in
`results/qwen_generation_comparison_note.md`.

## Artifacts

Result files, copied into the local repo from `auton-dgx2`:

- Vote-mode 100-trial results:
  `results/best_student_probe_qwen35_4b_vllm_vote_seed0_99_mergedprompt.jsonl`
- JSON/direct-answer 100-trial results:
  `results/best_student_probe_qwen35_4b_vllm_json_seed0_99_mergedprompt.jsonl`
- No-parser vLLM startup/serving log:
  `results/vllm_qwen35_4b_nightly_noparser_eager_20260701.log`
- Earlier invalid reasoning-parser attempt logs:
  `/home/mwilinsk/aj-verlog/results/vllm_qwen35_4b_nightly_eager_20260701.log`
  and related `vllm_qwen35_4b_*` logs.

Local repo files updated:

- Probe script:
  `scripts/openrouter_best_student_probe.py`
- Main report:
  `results/best_student_identification_experiment_report.md`
- Running note:
  `results/best_student_probe_note.md`
- Full generation comparison:
  `results/qwen_generation_comparison_note.md`
