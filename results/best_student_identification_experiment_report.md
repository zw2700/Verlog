# Best-Student Identification Experiment Report

This report summarizes the private-best-student diagnostic we ran for the
Verlog hiring/admissions environment.

## Why We Ran This

In full Verlog rollouts, professors sometimes converge on suboptimal students.
Before treating that as a collaboration failure, we need to answer a simpler
question:

> When a professor sees its own private utility column, can the model identify
> which student is best for that professor?

This matters because a group-level failure can come from at least two different
places:

- Individual identification failure: a professor cannot read or reason over its
own utility table and therefore does not know what it personally should vote
for.
- Collaboration failure: each professor knows its own preference, but the group
fails to aggregate private preferences, communicate efficiently, compromise,
wait, or vote at the right time.

The diagnostic isolates the first problem. It uses the real environment prompt,
but asks a narrow question: identify the highest-private-utility student.

## Environment And Prompt Setup

The probe instantiates the real hiring environment:

- Environment class: `AsyncTickerAdmissionsEnv`
- Prompt source: `AsyncTickerAdmissionsEnv._build_chat_messages`
- Student table: exactly the environment's observation table, including the
professor-private `Utility` column
- Student count: 5
- Feature dimension: 5
- Token budget shown in prompt: 1000
- Vote threshold shown in prompt: 0.5
- Professors: `prof_1`, `prof_2`, `prof_3`
- Professor tested per trial: cycles through professors by trial index
- Seeds: 0-99 for the 100-trial runs

The prompt shape matters. The final/valid runs use one system message and one
user message. The diagnostic instruction is appended to the env's existing user
observation instead of added as a second user message. Result files from the
valid prompt shape use the suffix `mergedprompt`.

The environment displays utilities rounded to one decimal place. The report
therefore tracks both:

- Exact env top-1: whether the chosen index equals the env's exact argmax.
- Displayed-table top: whether the chosen index is one of the top utilities as displayed to the model after rounding. (we have rounding to 1 decimal place in prompt).

Displayed-table top is important because some exact misses are harmless ties in
the visible prompt.

## Model Serving Setup

The same local vLLM setup was used for the 3B and 7B 100-trial comparisons:

- Serving stack: vLLM OpenAI-compatible server
- Endpoint during runs: `http://127.0.0.1:8000/v1`
- Max model length: 4096
- Prompt source and seeds: identical across model sizes

Models:

- `Qwen/Qwen2.5-3B-Instruct`
- `Qwen/Qwen2.5-7B-Instruct`
- `Qwen/Qwen3-4B`
- `Qwen/Qwen3-8B`
- `Qwen/Qwen3.5-4B`
- `Qwen/Qwen3.5-9B`

Qwen3 and Qwen3.5 used a separate serving setup because the repo's original
`vllm==0.10.0` stack does not support the new Qwen3.5 `qwen3_5`
architecture. These runs used an isolated nightly vLLM venv on `auton-dgx2`.
Qwen3.5 was served in text-only eager mode. The probe passed
`chat_template_kwargs={"enable_thinking": false}` via `--disable-thinking`;
without this, Qwen3/Qwen3.5 can spend the 128-token completion budget on a long
thinking preamble instead of a parseable final answer.

## Probe Variants

Two variants were run for each model.

### Vote Mode

The model is asked to behave like the professor and return an environment-style
action:

```text
<THINK>short private reason</THINK><VOTE>N</VOTE>
```

This tests whether the model can identify the best student while staying close
to the actual rollout action format.

### JSON / Direct-Answer Mode

The model is asked to identify the best student directly as JSON. This is meant
to reduce action-format burden and test the core table-reading ability.

In practice, especially for 3B, the model sometimes still returned env-style
actions instead of JSON. The parser extracts the selected student from JSON,
`<VOTE>N</VOTE>`, `Student N`, or a single unambiguous integer. So this metric is
best understood as "can we parse which student the model selected?", not strict
JSON compliance.

## Metrics

- Completed calls: API calls that finished without request error.
- Parseable answers: responses from which a student index could be extracted.
- Exact top-1 accuracy: selected index equals the exact highest-utility index.
- Displayed-table top accuracy: selected index is tied for best in the rounded
utility table visible to the model.
- Exact miss: selected index differs from exact env argmax.
- Real displayed-table miss: selected index is not a visible top utility.
- Utility regret: exact best utility minus selected student's exact utility.
- Max regret: largest utility regret across trials.



## Main 100-Trial Results


| Model               | Mode        | Exact Top-1 | Displayed-Top | Real Displayed Misses | Avg Regret | Max Regret |
| ------------------- | ----------- | ----------- | ------------- | --------------------- | ---------- | ---------- |
| Qwen2.5-3B-Instruct | vote        | 71/100      | 75/100        | 25/100                | 0.1340     | 1.6000     |
| Qwen2.5-3B-Instruct | JSON/direct | 68/100      | 71/100        | 29/100                | 0.1410     | 1.6000     |
| Qwen2.5-7B-Instruct | vote        | 90/100      | 92/100        | 8/100                 | 0.0210     | 0.6000     |
| Qwen2.5-7B-Instruct | JSON/direct | 96/100      | 97/100        | 3/100                 | 0.0090     | 0.6000     |
| Qwen3-4B            | vote        | 78/100      | 81/100        | 19/100                | 0.0740     | 1.2000     |
| Qwen3-4B            | JSON/direct | 80/100      | 83/100        | 17/100                | 0.0550     | 1.1000     |
| Qwen3-8B            | vote        | 85/100      | 87/100        | 13/100                | 0.0430     | 1.1000     |
| Qwen3-8B            | JSON/direct | 81/100      | 84/100        | 16/100                | 0.0560     | 1.1000     |
| Qwen3.5-4B          | vote        | 94/100      | 96/100        | 4/100                 | 0.0170     | 1.1000     |
| Qwen3.5-4B          | JSON/direct | 94/100      | 96/100        | 4/100                 | 0.0120     | 0.8000     |
| Qwen3.5-9B          | vote        | 93/100      | 94/100        | 6/100                 | 0.0140     | 0.5000     |
| Qwen3.5-9B          | JSON/direct | 96/100      | 97/100        | 3/100                 | 0.0040     | 0.2000     |




## Core Finding

The exact 3B training model has a substantial private-best identification
weakness. This is not only an action-formatting issue, because JSON/direct-answer
mode is also weak.

The 7B model mostly solves the problem under the same setup, though it is not
perfect. This means private-best identification is strongly model-size or
model-capability dependent.

Qwen3 alone does not solve the diagnostic: Qwen3-4B improves over Qwen2.5-3B,
and Qwen3-8B improves over Qwen3-4B, but both remain behind Qwen2.5-7B and
Qwen3.5 on this probe.

Qwen3.5 is strongest in this comparison. Qwen3.5-4B outperforms the exact
Qwen2.5-3B training model by a large margin and lands in roughly the same range
as Qwen2.5-7B. Qwen3.5-9B JSON/direct reaches 96/100 exact, 97/100
displayed-top, and only 0.0040 average regret. This supports the hypothesis
that bumping model generation/family can reduce the individual table-reading
bottleneck. It does not by itself answer whether full multi-agent collaboration
improves, because rollout-level timing, speaking, and social-welfare aggregation
still need to be measured.

For training runs with `Qwen/Qwen2.5-3B-Instruct`, we should not assume each
professor knows what it should vote for. That simpler failure can confound
downstream interpretations of negotiation, consensus, social welfare, and credit
assignment.

## Success Modes



### Clean Correct Vote

Example: 3B vote mode, seed 17, `prof_3`.

- Displayed utilities: `[1.1, 1.0, 1.0, 3.4, 2.4]`
- Gold student: 3
- Model voted: 3
- Regret: 0.0

Model response:

```text
<THINK>I need to consider the highest utility among the students. Student 3 has the highest utility at 3.4, but I should also look at the other students to ensure we're maximizing the group's overall benefit.</THINK><VOTE>3</VOTE>
```

This is a success despite some social-welfare language in the reasoning, because
the final vote matches the professor's private utility maximum.

### Harmless Tie / Zero-Regret Exact Miss

Example: 3B vote mode, seed 0, `prof_1`.

- Displayed utilities: `[1.0, 1.3, 1.5, 2.7, 2.7]`
- Exact env gold student: 3
- Visible top students: 3 and 4
- Model voted: 4
- Regret: 0.0

Model response:

```text
<THINK>I need to consider the highest utility among the students. Student 4 has the highest utility score at 2.7. I should vote for Student 4 to maximize my personal utility.</THINK><VOTE>4</VOTE>
```

This is counted as an exact-top-1 miss because the env tie-breaks to index 3,
but it is not a real behavioral failure from the model's point of view.

### 7B Corrects A 3B Failure

Seed 90, `prof_1`, same environment instance:

- Displayed utilities: `[3.0, 1.9, 2.6, 1.8, 1.4]`
- Gold student: 0

3B vote-mode response:

```text
<THINK>I need to consider the highest utility among the students. Student 4 has the highest utility of 1.4, but I should also look at the other students to ensure we're maximizing the group's utility.</THINK><VOTE>4</VOTE>
```

3B regret: 1.6.

7B vote-mode response:

```text
<THINK>Student 0 has the highest utility for me based on the provided scores.</THINK><VOTE>0</VOTE>
```

7B regret: 0.0.

This is the cleanest illustration of the model-size effect.

## Failure Modes



### Real Table-Reading Failure

Example: 3B vote mode, seed 97, `prof_2`.

- Displayed utilities: `[3.2, 1.1, 2.1, 1.1, 1.8]`
- Gold student: 0
- Model voted: 4
- Regret: 1.4

Model response:

```text
<THINK>I need to choose the student with the highest utility for me. Based on the given utilities, Student 4 has the highest utility of 1.8. I will vote for Student 4.</THINK><VOTE>4</VOTE>
```

This is not a negotiation failure. The model explicitly says a lower value is
the highest value.

### Direct-Answer Failure

Example: 3B JSON/direct-answer mode, seed 82, `prof_2`.

- Displayed utilities: `[3.3, 1.7, 1.7, 2.2, 1.6]`
- Gold student: 0
- Parsed student: 2
- Regret: 1.6

Model response:

```text
<THINK>My highest utility is for Student 2, with a utility of 1.7. Their ability vector closely aligns with my research interests, especially in AI/ML and HCI, which are key areas for me.</THINK><VOTE>2</VOTE>
```

This shows that the 3B failure persists even when the diagnostic asks for a
direct answer, not just a rollout-style vote.

### Shallow "Highest Utility" Template But Wrong Index

Example: 7B vote mode, seed 66, `prof_1`.

- Displayed utilities: `[1.4, 2.2, 1.2, 1.4, 1.6]`
- Gold student: 1
- Model voted: 4
- Regret: 0.6

Model response:

```text
<THINK>Voting for the student with the highest utility as per the table.</THINK><VOTE>4</VOTE>
```

The 7B model is much better overall, but this is a real visible-table mistake.
The reasoning is generic and does not name the actual top utility.

### Strategic/Group-Prompt Contamination

Some failures include language about group welfare or waiting even though the
diagnostic asks for the private best. This is expected because the base env
system prompt frames the professor as a strategic negotiator seeking consensus.

In the 3B failures, this can appear as the model mixing up private best with a
broader group decision or simply drifting into normal rollout behavior. The
diagnostic still captures the selected student, but strict output-format
compliance should be analyzed separately from best-student identification.

## What This Means For The Project

For 3B experiments:

- Private-best identification is a real bottleneck.
- Rollout failures can be caused by a professor not knowing its own best vote.
- We should log private-best recovery and vote regret before interpreting social
welfare failures as coordination or credit-assignment failures.

For 7B experiments:

- Private-best identification is mostly solved.
- If 7B still fails in full rollouts, downstream collaboration bottlenecks become
more plausible: timing, communication, waiting, compromise, herding, or credit
assignment.
- The remaining 7B mistakes are useful edge cases for prompt/debugging, but they
are far less frequent and lower-regret than 3B mistakes.

For scaling:

- The private-identification bottleneck itself scales with model capability.
- This suggests population-size/budget experiments should control for base-model
individual competence, otherwise budget/cooperation conclusions may be
confounded by simple table-reading failures.
- Qwen3.5 strengthens this point: a newer 4B model already approaches or
exceeds the older 7B result on private-best identification. Qwen3 is a useful
cautionary control because Qwen3-4B/8B improve over Qwen2.5-3B but remain
materially weaker than Qwen3.5 on this probe.



## Recommended Follow-Up Metrics

Add these to rollouts and training logs:

- Private-best recovery per professor per turn.
- Tie-aware private-best recovery.
- Utility regret of each vote relative to that professor's private best.
- Whether the final consensus student is each professor's private top, top-2,
or lower.
- Social-optimal recovery per step.
- Selected social-welfare rank over time.
- Whether conversation history improves or worsens private-best identification.
- Whether errors correlate with close top-two gaps or with specific professor
positions/turns.



## Where To Inspect Artifacts

Main files:

- Probe script:
`scripts/openrouter_best_student_probe.py`
- This report:
`results/best_student_identification_experiment_report.md`
- Main running note:
`results/best_student_probe_note.md`
- 3B 100-trial note:
`results/qwen25_3b_100trial_note.md`
- 7B 100-trial note:
`results/qwen25_7b_100trial_note.md`
- Qwen3.5-4B 100-trial note:
`results/qwen35_4b_100trial_note.md`
- Qwen generation comparison note:
`results/qwen_generation_comparison_note.md`
- Contribution/framing note:
`research_contribution_plan.md`

Raw 100-trial result files:

- 3B vote:
`results/best_student_probe_qwen25_3b_vllm_vote_seed0_99_mergedprompt.jsonl`
- 3B JSON/direct:
`results/best_student_probe_qwen25_3b_vllm_json_seed0_99_mergedprompt.jsonl`
- 7B vote:
`results/best_student_probe_qwen25_7b_vllm_vote_seed0_99_mergedprompt.jsonl`
- 7B JSON/direct:
`results/best_student_probe_qwen25_7b_vllm_json_seed0_99_mergedprompt.jsonl`
- Qwen3-4B vote:
`results/best_student_probe_qwen3_4b_vllm_vote_seed0_99_mergedprompt.jsonl`
- Qwen3-4B JSON/direct:
`results/best_student_probe_qwen3_4b_vllm_json_seed0_99_mergedprompt.jsonl`
- Qwen3-8B vote:
`results/best_student_probe_qwen3_8b_vllm_vote_seed0_99_mergedprompt.jsonl`
- Qwen3-8B JSON/direct:
`results/best_student_probe_qwen3_8b_vllm_json_seed0_99_mergedprompt.jsonl`
- Qwen3.5-4B vote:
`results/best_student_probe_qwen35_4b_vllm_vote_seed0_99_mergedprompt.jsonl`
- Qwen3.5-4B JSON/direct:
`results/best_student_probe_qwen35_4b_vllm_json_seed0_99_mergedprompt.jsonl`
- Qwen3.5-9B vote:
`results/best_student_probe_qwen35_9b_vllm_vote_seed0_99_mergedprompt.jsonl`
- Qwen3.5-9B JSON/direct:
`results/best_student_probe_qwen35_9b_vllm_json_seed0_99_mergedprompt.jsonl`

vLLM logs for Qwen3/Qwen3.5 runs:

- Qwen3-4B:
`results/vllm_qwen3_4b_nightly_noparser_eager_20260701.log`
- Qwen3-8B:
`results/vllm_qwen3_8b_nightly_noparser_eager_20260701.log`
- Qwen3.5-4B:
`results/vllm_qwen35_4b_nightly_noparser_eager_20260701.log`
- Qwen3.5-9B:
`results/vllm_qwen35_9b_nightly_noparser_eager_20260701.log`

Earlier comparison files:

- 7B OpenRouter JSON, seeds 0-9:
`results/best_student_probe_qwen25_7b_openrouter.jsonl`
- 7B OpenRouter vote, seeds 0-9:
`results/best_student_probe_qwen25_7b_vote_openrouter.jsonl`
- 7B OpenRouter vote, seeds 10-19:
`results/best_student_probe_qwen25_7b_vote_openrouter_seed10_19.jsonl`
- 3B vLLM 20-trial vote:
`results/best_student_probe_qwen25_3b_vllm_vote_seed0_19_mergedprompt.jsonl`
- 3B vLLM 20-trial JSON:
`results/best_student_probe_qwen25_3b_vllm_json_seed0_19_mergedprompt.jsonl`

