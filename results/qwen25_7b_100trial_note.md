# Qwen2.5-7B Best-Student Probe: 100-Trial vLLM Run

This note records the 100-trial diagnostic for
`Qwen/Qwen2.5-7B-Instruct`, served locally with vLLM on `auton-dgx2`.

## Setup

- Date run: 2026-07-01
- Host: `auton-dgx2`
- Serving stack: local vLLM OpenAI-compatible endpoint
- Model: `Qwen/Qwen2.5-7B-Instruct`
- Endpoint during run: `http://127.0.0.1:8000/v1`
- Environment prompt source: `AsyncTickerAdmissionsEnv._build_chat_messages`
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

## Results

### Vote Mode

- Completed calls: 100/100
- Parseable answers: 100/100
- Exact env top-1 accuracy: 90/100 = 0.90
- Displayed-table top accuracy: 92/100 = 0.92
- Exact misses: 10/100
- Real displayed-table misses: 8/100
- Displayed utility tie trials: 11/100
- Average utility regret: 0.0210
- Maximum utility regret: 0.6000

Top regret cases:

- Seed 66, `prof_1`: gold 1, predicted 4, regret 0.6000.
- Seed 73, `prof_2`: gold 4, predicted 3, regret 0.5000.
- Seed 88, `prof_2`: gold 0, predicted 4, regret 0.4000.
- Seed 83, `prof_3`: gold 1, predicted 4, regret 0.2000.

### JSON / Direct-Answer Mode

- Completed calls: 100/100
- Parseable answers: 100/100
- Exact env top-1 accuracy: 96/100 = 0.96
- Displayed-table top accuracy: 97/100 = 0.97
- Exact misses: 4/100
- Real displayed-table misses: 3/100
- Displayed utility tie trials: 11/100
- Average utility regret: 0.0090
- Maximum utility regret: 0.6000

Top regret cases:

- Seed 66, `prof_1`: gold 1, predicted 4, regret 0.6000.
- Seed 83, `prof_3`: gold 1, predicted 4, regret 0.2000.
- Seed 84, `prof_1`: gold 3, predicted 1, regret 0.1000.

## Comparison To 3B

The 7B model is much stronger than the exact 3B training model under the same
local vLLM setup, same seeds, and same prompt shape.

| Model | Mode | Exact Top-1 | Displayed-Top | Avg Regret | Max Regret |
| --- | --- | ---: | ---: | ---: | ---: |
| Qwen2.5-3B-Instruct | vote | 71/100 | 75/100 | 0.1340 | 1.6000 |
| Qwen2.5-3B-Instruct | JSON/direct | 68/100 | 71/100 | 0.1410 | 1.6000 |
| Qwen2.5-7B-Instruct | vote | 90/100 | 92/100 | 0.0210 | 0.6000 |
| Qwen2.5-7B-Instruct | JSON/direct | 96/100 | 97/100 | 0.0090 | 0.6000 |

The capability gap is large enough that model size should be treated as an
important experimental variable. The 3B model has a substantial private-best
identification bottleneck; the 7B model mostly solves it, though it still makes
occasional visible-table mistakes.

## Interpretation

The 7B vLLM result partially confirms the earlier OpenRouter 7B proxy result:
the larger same-family model can usually identify the best private-utility
student from the prompt. However, the 100-trial vLLM run is not perfectly clean:
vote mode still has 8 real displayed-table misses and JSON/direct-answer mode
has 3 real displayed-table misses.

For the project, this suggests:

- Private-best identification is a serious bottleneck for 3B.
- Private-best identification is mostly solved by 7B, but not perfectly.
- If collaboration still fails at 7B, downstream bottlenecks such as timing,
  communication, compromise, and credit assignment become more plausible.
- If collaboration fails at 3B, we need to separate collaboration failures from
  simpler utility-table reading failures.

## Artifacts

- Vote-mode 100-trial results:
  `results/best_student_probe_qwen25_7b_vllm_vote_seed0_99_mergedprompt.jsonl`
- JSON/direct-answer 100-trial results:
  `results/best_student_probe_qwen25_7b_vllm_json_seed0_99_mergedprompt.jsonl`
- 3B comparison note:
  `results/qwen25_3b_100trial_note.md`
- Probe script:
  `scripts/openrouter_best_student_probe.py`
