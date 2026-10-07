# Zero-shot Qwen3-4B thinking × temperature: consolidated conversation record

Consolidated on 2026-09-07 from the experiment brief, implementation, saved DGX2 artifacts, analysis outputs, slide deck, and decisions made in this conversation. This is a structured research record, not a verbatim transcript.

## Executive summary

- The study asked whether `Qwen/Qwen3-4B` already has a useful multi-agent discussion strategy that can be elicited by either native Qwen thinking or higher sampling temperature.
- It was an inference-only 2×2 experiment: manual literal `<THINK>` versus Qwen-native thinking, each at temperature 1.0 and 1.3.
- The final pilot used the same 100 seeds in all four conditions: 400 completed episodes in total.
- Native thinking was qualitatively different: it generated much more private reasoning but produced shorter social interactions, more immediate voting, less public communication, and more first-vote following.
- Native thinking improved aggregate consensus and welfare efficiency, but the social-optimality improvement disappeared in the all-unique top-choice stratum, where all three professors initially preferred different students.
- Higher temperature made the manual condition negotiate and communicate more. In the all-unique stratum, this extra discussion did not improve welfare efficiency or social optimality.
- The inference-time elicitation question is therefore provisionally answered: neither native thinking nor temperature 1.3 elicited reliably better aggregation under genuine preference conflict.
- The agreed next step is reward-shaped training that incentivizes useful, decision-relevant discussion and evaluates whether it improves social optimality and welfare efficiency—not merely communication volume or consensus.

## Research question and hypotheses

Primary question:

> Does native thinking or higher sampling temperature improve multi-agent discussion and group decisions?

Hypotheses used in the final presentation:

1. **Reasoning-mode hypothesis:** native thinking will elicit more substantive negotiation and improve group decisions.
2. **Sampling hypothesis:** higher temperature will increase exploration and reduce premature consensus.

The main scientific comparison is not merely response length. It is whether native model reasoning produces a qualitatively different interaction policy from an environment-enforced literal `<THINK>...</THINK>` block.

## Experimental design

### Four conditions

| Condition | Reasoning mode | Temperature | Episodes |
|---|---|---:|---:|
| `qwen3-4b-zs-base-manual` | Manual literal `<THINK>` | 1.0 | 100 |
| `qwen3-4b-zs-high-temp-manual` | Manual literal `<THINK>` | 1.3 | 100 |
| `qwen3-4b-zs-base-native` | Qwen-native thinking | 1.0 | 100 |
| `qwen3-4b-zs-high-temp-native` | Qwen-native thinking | 1.3 | 100 |

All conditions used seeds `0`–`99`. The pairing is a design property—each condition saw the same environments—but the presentation calls these **LM sampling experiments**, not a “paired study.”

### Fixed model and sampling configuration

- Model: `Qwen/Qwen3-4B`
- Resolved model revision: `1cfa9a7208912126459214e8b04321603b3df60c`
- Base temperature: `1.0`
- High temperature: `1.3`
- `top_p`: `1.0`
- Maximum generated tokens per LM call: `4096`
- vLLM context length: `16384`
- Parallel episode workers per model server: `8`
- Runtime recorded by the completed cells: Python `3.10.20`, vLLM `0.10.0`

Temperature 1.0 is the canonical training-rollout temperature and the inference baseline. Temperature 1.3 was an explicit elicitation probe, not a claim that 1.3 is intrinsically optimal. This inference-only experiment does not directly test the long-run learning effect of training with a different rollout temperature.

### Fixed environment configuration

- Environment: `async_ticker_admissions` / `AsyncTickerAdmissionsEnv`
- Professors: `prof_1`, `prof_2`, `prof_3`
- Students per batch: `5`
- Feature dimension: `5`
- Professor preference mode: `random_permutation`
- Turn order: fixed (`randomize_turn_order=false` in the manifest)
- Shared public communication budget: `500` tokens
- Vote threshold: `0.5`
- Maximum environment steps: `50`
- `terminate_on_all_voted_no_consensus=false`
- Preference correlation threshold: `0.0`
- Preference rejection maximum attempts: `1000`

With three professors and a 50% vote threshold, two matching votes terminate the episode. Under fixed turn order, this means the third professor often never acts when the first two votes match.

## Reasoning protocols

### Manual `<THINK>` condition

- Qwen-native thinking is disabled with `chat_template_kwargs={"enable_thinking": false}`.
- The prompt requires ordinary generated text inside a literal `<THINK>...</THINK>` block before the visible action tags.
- The literal private-reasoning block remains in that agent's own conversation history.
- The completion still must contain a parseable visible action such as `<GROUP>`, `<VOTE>`, `<WAIT>`, or `<WAIT_FOR>`.

### Native-thinking condition

- Qwen-native thinking is enabled with `chat_template_kwargs={"enable_thinking": true}`.
- The prompt is adapted so it does not request a second literal `<THINK>` block.
- Qwen produces model-native private reasoning followed by visible action text.
- Native reasoning is separated or stripped before the visible action is sent to the environment.
- Private reasoning is retained in research artifacts for diagnosis and paired qualitative inspection.

### What is and is not controlled

- The visible action grammar, model weights, environment, seeds, `top_p`, and output-token limit are held fixed.
- This is an end-to-end reasoning-protocol comparison, not a tokenizer-only ablation. The model sees a different chat-template mode and a correspondingly adapted reasoning instruction.
- Both manual and native private reasoning consume the LM call's generation allowance.
- Native reasoning can therefore exhaust `max_output_tokens` before a visible action is emitted.
- Neither form of private reasoning is charged to the environment's 500-token shared communication budget.
- Only public `<GROUP>` message tokens count against that shared environment budget.
- “Comm. tokens” in the results means shared public communication tokens used per episode.
- “LM calls” means logged agent inference calls, i.e. the number of entries in the episode's `turns` list.

The common 4096-token generation limit was selected after smaller 512- and 1024-token diagnostics frequently truncated native reasoning before a visible action. The limit was increased for all four conditions, not only native thinking.

## Implementation produced during the task

- `scripts/rollout_frontier.py`
  - Explicit `--reasoning-mode` with `manual-tags` and `native-thinking`.
  - Explicit chat-template kwargs and prompt adaptation.
  - Separation/logging of private reasoning and visible actions.
  - Explicit temperature, model, seeds, environment parameters, output budget, and metadata.
- `scripts/launch_zero_shot_matrix.py`
  - Reproducible four-cell launcher.
  - Dry-run unless `--submit` is supplied.
  - Separate artifact paths for every condition.
  - Presets: smoke = 3 seeds/cell, pilot = 100 seeds/cell, full = 500 seeds/cell.
- `analysis/compute_zero_shot_matrix.py`
  - Produces overall and preference-scenario summaries plus selected qualitative trace pairs.
- `tests/test_zero_shot_experiment.py`
  - Tests reasoning-mode prompt adaptation, chat-template kwargs, launcher manifest construction, and metadata.
- `docs/zero_shot_thinking_temperature.md`
  - Experiment runbook.
- `docs/zero_shot_thinking_temperature_slides.html`
  - Current HTML presentation.

The system Python on the current host does not have `pytest`, so the targeted tests were not rerun while producing this record. The attempted command failed at import time with `No module named pytest`; this is not a test failure.

## Execution history and operating constraints

- Initial planning considered Rhea/Auton Slurm.
- The runbook assigns all experiment presets, including smoke, to `general / qos_general`.
- The user explicitly rejected the debug partition for real experiments.
- The user also explicitly requested no repeated Stone-cluster polling, repeated SSH connections, or busy status querying because that can trigger cluster sanctions.
- The intended operating pattern is: sync once, submit once, let the job run, and inspect only when necessary.
- The user requested an ETA whenever experiment status is reported.
- The final 100-seed-per-condition pilot was synchronized to and executed on DGX2 because it had immediate capacity and was substantially faster than the initial estimate.
- During execution, three processes were visible concurrently after some work had already completed; all four conditions ultimately completed.
- The final run started at approximately `2026-08-19T14:53:27Z`.
- Approximate per-condition wall times from metadata:
  - Manual, T=1.0: 2m27s
  - Manual, T=1.3: 2m36s
  - Native, T=1.0: 11m34s
  - Native, T=1.3: 8m10s
- The native jobs took longer in wall time despite producing fewer social turns because every native call generated much longer private reasoning.
- All 400 episodes finished. The analysis found no invalid actions.

The prior authorization to sync code, push changes, and submit the experiment was specific to this completed task. It should not be treated as blanket authorization for future cluster mutations.

## Run provenance

- Run ID: `zs-pilot-dgx2-paired-4k-20260819c`
- Run manifest creation time: `2026-08-19T14:52:28Z`
- Recorded code commit: `e888c0e2c7ee27fee8ba8c5d93a7cfba06d86b90`
- The recorded checkout was dirty in all cell metadata.
- Model revision was resolved and fixed consistently across all cells.
- Each cell's metadata status is `complete`.
- The final artifacts are now copied locally under:
  - `artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/`

### Environment freshness caveat

The artifacts do not establish that the DGX2 checkout was the latest possible environment version: they identify a dirty code checkout rather than a clean reproducible tree. In the current local checkout, the hiring-env submodule points to:

`aa7da2bc9947289eb2261fc3d0bf6f1875f4a631`

and `verl/envs/hiring_env/env.py` currently has uncommitted modifications. Therefore, “up to date” versus “stale” cannot be claimed solely from the saved rollout metadata; it would require a deliberate comparison against the intended remote revision. No repeated cluster querying was performed for that question.

## Behavior-category definitions

The categories describe interaction process, not outcome quality.

### Instant decision

An episode is classified as `instant_decision` when it is not malformed or stalled and at least one of these holds:

- shared communication tokens used `<= 40`;
- logged LM calls `<= 2`; or
- logged LM calls `<= 3`, consensus is reached, and only one candidate appears.

This category can include consensus and no-consensus episodes. It means there was no meaningful back-and-forth use of the deliberation budget.

### Negotiation

`negotiation` is the broad residual category after malformed, stalled, and instant-decision checks. It does **not** guarantee high-quality or substantive negotiation. It can include productive bargaining, failed discussion, shallow proposal-following, verbosity, or disagreement.

This distinction matters: more episodes labeled “negotiation” are not automatically evidence of better aggregation.

## Outcome definitions

### Social optimality rate

- Compute each candidate's collective utility as the sum of its utilities across professors.
- Rank the chosen candidate by collective utility.
- An episode is socially optimal if the chosen candidate has global rank 1.
- Tied maxima count as rank 1 because rank is `1 + number of strictly greater values`.
- The reported social optimality rate is the fraction of all episodes choosing a rank-1 candidate.
- A no-consensus episode is not socially optimal.

This metric is binary at the episode level: exact best choice or not.

### Welfare efficiency

The deck uses the environment's raw utilitarian efficiency:

`actual total utility of chosen candidate / optimal total utility`

- It is continuous and measures how close the choice is to the best possible collective utility.
- A near-best but non-optimal candidate can therefore have high welfare efficiency while failing social optimality.
- If there is no valid final choice, actual utility is zero and welfare efficiency is zero.
- This is distinct from the environment's separately available min-normalized utility-efficiency variant; the deck does not use that variant.

Example: if the optimum has total utility 10 and the group chooses a candidate with utility 9, welfare efficiency is 90%, but social optimality is false.

### Standard deviations and uncertainty

- Slides 4 and 6 report episode-level **mean ± sample SD** for continuous metrics: welfare efficiency, LM calls, and communication tokens.
- The SDs were computed directly from the raw episode JSONL files.
- Percentage outcomes are rates, not continuous means with a reported SD.
- For inferential uncertainty on rates, binomial confidence intervals or paired-seed tests are more useful than reporting the Bernoulli SD.
- The current `matrix_summary.json` stores means and rates but not the added SD fields.

## Preference-overlap strata

The 100 environments were not restricted to a special 37-seed “diagnostic subset.” They form five exhaustive strata according to which professors initially share the same top candidate:

| Stratum | Seeds per condition |
|---|---:|
| All three share the same top choice | 10 |
| Prof. 1 and Prof. 2 share; Prof. 3 differs | 17 |
| Prof. 1 and Prof. 3 share; Prof. 2 differs | 19 |
| Prof. 2 and Prof. 3 share; Prof. 1 differs | 17 |
| All three top choices are unique | 37 |
| **Total** | **100** |

The 37 is simply the naturally occurring size of the all-unique top-choice stratum among seeds 0–99. It was not a separate sampled dataset or a post-hoc restriction.

The strata are small (`n=10`–`37`), so their results are descriptive. They should not be presented as statistically significant without an explicit paired uncertainty analysis or a larger replication.

## Overall results: all 100 environments per condition

Continuous metrics are mean ± sample SD. Communication tokens are shared public tokens per episode.

| Condition | Instant | Negotiation | Consensus | Welfare efficiency | Social optimality | LM calls | Comm. tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| Manual, T=1.0 | 42.0% | 56.0% | 91.0% | 85.1 ± 28.4% | 49.0% | 7.02 ± 8.22 | 115 ± 138 |
| Manual, T=1.3 | 30.0% | 70.0% | 93.0% | 87.2 ± 25.6% | 51.0% | 7.30 ± 6.66 | 129 ± 142 |
| Native, T=1.0 | 79.0% | 21.0% | 100.0% | 93.4 ± 10.3% | 55.0% | 2.76 ± 1.79 | 34 ± 26 |
| Native, T=1.3 | 85.0% | 15.0% | 100.0% | 93.4 ± 10.6% | 55.0% | 2.49 ± 0.95 | 32 ± 18 |

Additional rollout-quality diagnostics:

- Manual cells: no truncation and no missing visible actions.
- Native cells: 1.8–2.0% of logged calls were truncated and 1.4–1.6% lacked a visible action.
- No condition produced invalid environment actions.

Overall interpretation:

- Higher temperature modestly changed the manual aggregates: less instant behavior, more negotiation, slightly higher consensus, welfare efficiency, and social optimality.
- Native thinking produced 100% consensus with far fewer LM calls and public communication.
- The native conditions rarely negotiated according to the broad process taxonomy.
- Aggregate social optimality moved from 49–51% manual to 55% native, but the preference-stratified analysis shows that this is not a robust gain under all-unique preferences.

## Preference-stratified results

Condition order in all three tables:

1. Manual, T=1.0
2. Manual, T=1.3
3. Native, T=1.0
4. Native, T=1.3

### Socially optimal decision rate

| Preference stratum | n | Manual 1.0 | Manual 1.3 | Native 1.0 | Native 1.3 |
|---|---:|---:|---:|---:|---:|
| All share | 10 | 80.0% | 90.0% | 80.0% | 80.0% |
| P1+P2 share; P3 unique | 17 | 47.1% | 58.8% | 58.8% | 76.5% |
| P1+P3 share; P2 unique | 19 | 42.1% | 36.8% | 52.6% | 52.6% |
| P2+P3 share; P1 unique | 17 | 41.2% | 52.9% | 58.8% | 47.1% |
| All top choices unique | 37 | 48.6% | 43.2% | 45.9% | 43.2% |

### Instant-decision rate

| Preference stratum | n | Manual 1.0 | Manual 1.3 | Native 1.0 | Native 1.3 |
|---|---:|---:|---:|---:|---:|
| All share | 10 | 60.0% | 50.0% | 100.0% | 100.0% |
| P1+P2 share; P3 unique | 17 | 47.1% | 47.1% | 94.1% | 100.0% |
| P1+P3 share; P2 unique | 19 | 21.1% | 10.5% | 73.7% | 73.7% |
| P2+P3 share; P1 unique | 17 | 35.3% | 35.3% | 64.7% | 70.6% |
| All top choices unique | 37 | 48.6% | 24.3% | 75.7% | 86.5% |

### Mean LM calls

| Preference stratum | n | Manual 1.0 | Manual 1.3 | Native 1.0 | Native 1.3 |
|---|---:|---:|---:|---:|---:|
| All share | 10 | 4.00 | 5.10 | 2.00 | 2.10 |
| P1+P2 share; P3 unique | 17 | 4.76 | 7.00 | 2.18 | 2.12 |
| P1+P3 share; P2 unique | 19 | 9.00 | 8.26 | 2.63 | 2.89 |
| P2+P3 share; P1 unique | 17 | 9.76 | 5.76 | 2.94 | 2.65 |
| All top choices unique | 37 | 6.59 | 8.24 | 3.22 | 2.49 |

Across every stratum, native thinking is more likely to produce an instant decision and uses fewer LM calls. Temperature effects are non-monotonic across strata.

## Detailed all-unique top-choice stratum

This is one of the five strata, not a separate dataset. It is scientifically useful because no pair begins with the same privately preferred candidate, so immediate agreement cannot simply follow an already-shared top choice.

Continuous metrics are mean ± sample SD across `n=37` episodes per condition.

| Condition | Instant | Negotiation | Consensus | Welfare efficiency | Social optimality | LM calls | Comm. tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| Manual, T=1.0 | 48.6% | 48.6% | 91.9% | 86.4 ± 27.5% | 48.6% | 6.59 ± 8.97 | 100 ± 121 |
| Manual, T=1.3 | 24.3% | 75.7% | 91.9% | 86.7 ± 27.3% | 43.2% | 8.24 ± 7.54 | 154 ± 159 |
| Native, T=1.0 | 75.7% | 24.3% | 100.0% | 93.7 ± 8.3% | 45.9% | 3.22 ± 2.70 | 40 ± 36 |
| Native, T=1.3 | 86.5% | 13.5% | 100.0% | 92.7 ± 9.1% | 43.2% | 2.49 ± 0.61 | 29 ± 14 |

Key comparison:

- Raising manual temperature from 1.0 to 1.3 increased the negotiation rate by 27.1 percentage points.
- It increased mean communication use by about 53%: 100 to 154 shared tokens.
- Welfare efficiency remained essentially flat: 86.4% to 86.7%.
- Social optimality fell by 5.4 percentage points: 48.6% to 43.2%.
- Native thinking reached consensus in every episode, but its social optimality was 45.9% at T=1.0 and 43.2% at T=1.3—no improvement over the manual T=1.0 baseline.
- Therefore, additional discussion induced by temperature was not sufficient, and native rapid consensus was not evidence of better preference aggregation.

The very large SDs for manual LM calls and communication tokens reveal heavy episode-to-episode variation and long interaction tails. Native T=1.3 is much more behaviorally concentrated: 2.49 ± 0.61 LM calls and 29 ± 14 public tokens.

## Reasoning length and the short-native-episode question

Average private-reasoning characters per reasoning-bearing call:

| Condition | Mean reasoning characters |
|---|---:|
| Manual, T=1.0 | 263 |
| Manual, T=1.3 | 269 |
| Native, T=1.0 | 5,590 |
| Native, T=1.3 | 5,279 |

By that private-reasoning-character measure, native thinking produced roughly 20–21× more private reasoning. A separate per-response/token comparison discussed in the rollout analysis put native calls at approximately 12–13× the manual length; these are different denominators and should not be conflated.

The central length result is:

> Native episodes are socially short but computationally long.

Native episodes did not end early because the model lacked generation budget:

- Native generations were much longer per call.
- Only 1.8–2.0% of native calls hit the 4096-token generation cap.
- Truncation can create missing actions and extra calls; it does not explain the dominant early-consensus pattern.

The short social trajectories come primarily from immediate voting and the two-vote termination rule.

## First-mover anchoring

The qualitative rollout analysis found a strong first-vote focal-point effect:

1. Native agents usually voted immediately.
2. A later voter often copied the existing vote even when another candidate was privately preferable.
3. Two matching votes ended the episode before the third professor could contribute.

The current slide summarizes the mechanism as approximately:

- 89–93% immediate voting;
- 63–66% second-voter following against the second voter's own top choice;
- 57–64% consensus after two logged LM calls.

The last figure is directly visible in the logs as 57/100 native T=1.0 episodes and 64/100 native T=1.3 episodes with exactly two logged calls. The first two percentages are sensitive to the denominator—per turn, per agent's first call, per second vote, or conditional on a preference conflict. Before using them in a paper, the analysis should persist an explicit metric definition and numerator/denominator. The qualitative conclusion is robust, but the shorthand percentage label needs that formalization.

“Second voter” means the second professor to cast a vote, not necessarily the agent named `prof_2`. “Following against its own top choice” means matching the first vote even though the second voter's private utility table ranks another candidate highest.

## Main scientific interpretation

### What native thinking changes

- It is qualitatively different from literal environment-enforced `<THINK>` text.
- It changes much more than tokenization: chat-template mode, prompt wording, reasoning representation, reasoning retention, and environment-visible content all differ.
- It elicits far longer private deliberation.
- Despite that private deliberation, it makes the public policy more vote-heavy, less communicative, and more first-mover-sensitive.
- High consensus under native thinking should not be interpreted as deep multi-agent aggregation.

### What temperature changes

- In manual mode, T=1.3 reduces instant-decision classifications and increases discussion.
- The additional discussion does not translate into better decisions in the all-unique stratum.
- In native mode, T=1.3 makes the policy even more instant while leaving overall social optimality unchanged at 55% and slightly lowering all-unique welfare efficiency.
- Temperature effects vary across preference-overlap strata rather than moving monotonically in one favorable direction.

### Bottom line

- Native thinking exposes a different interaction policy, but not a reliably better conflict-resolution strategy.
- Temperature 1.3 can elicit more talking in manual mode, but more talking is not the same as useful information aggregation.
- The all-unique stratum is the clearest evidence: neither intervention improves exact socially optimal choice over manual T=1.0.
- There is no strong current reason to continue tuning these two inference-time knobs before testing training interventions.
- If a stronger statistical claim is required, the launcher already supports a 500-seed-per-condition full run. That would improve precision but is not required for the present qualitative conclusion.

## Agreed next experiment

Investigate reward shaping that incentivizes **useful discussion**, with the explicit goal of improving group decision quality.

Candidate intervention principles:

- Reward decision-relevant public communication and evidence integration.
- Do not reward raw message length.
- Do not reward consensus alone; rapid consensus can encode first-voter anchoring.
- Separate communication-process rewards from final-outcome rewards so their effects can be diagnosed.
- Keep the inference setup fixed enough to attribute changes to training rather than a simultaneous decoding change.

Primary outcome metrics:

1. Social optimality rate.
2. Welfare efficiency.

Report both overall and across the same five preference-overlap strata. Keep negotiation rate, consensus, stalls, invalid actions, LM calls, and communication tokens as secondary process diagnostics.

The key decision question is:

> Does incentivized discussion improve decisions, or only produce more communication?

## Presentation decisions made in the conversation

The requested presentation format is HTML only—no PDF. The style should be short, simple, scientific, graphically restrained, and easy to scan in a discussion with a professor.

Current slide order:

1. Main hypotheses and link to complete rollout workspace.
2. 2×2 experimental setup.
3. Reasoning-protocol comparison.
4. Overall results, including SDs for continuous metrics.
5. Bar charts stratified by all five preference-overlap structures: social optimality, instant-decision rate, and mean LM calls.
6. Detailed all-unique top-choice results, including SDs.
7. Mechanism behind short native episodes / first-mover anchoring.
8. Next reward-shaping experiment.

Specific editing decisions:

- The protocol slide was moved near the beginning.
- The title slide states hypotheses rather than revealing the result.
- Results come after hypotheses and setup.
- The prior generic final recommendation slide was removed.
- A concrete next-steps slide was later added.
- The rollout-workspace link was moved to slide 1.
- The run ID was removed from the visible slides.
- “Paired study” was replaced by “LM sampling experiments.”
- The small repeated footer `Qwen3-4B · 400 episodes` was removed from every slide.
- Decimal precision was made consistent within comparable columns.
- The 37 all-unique environments are presented as one exhaustive stratum, not a “diagnostic subset.”
- “All unique,” “conflicts,” and “no pair shares its top candidate” were standardized to the all-unique top-choice stratum.
- “Native stays short” was replaced with the more precise “native uses fewer LM calls.”
- `N`/`n` and “Negotiate”/“Negotiation” labels were standardized.
- Welfare efficiency and social optimality definitions were added.
- Slides 4 and 6 now report mean ± sample SD for continuous metrics.

## Artifact index

- Experiment brief: [`../ZERO_SHOT_EXPERIMENT_AGENT_BRIEF.md`](../ZERO_SHOT_EXPERIMENT_AGENT_BRIEF.md)
- Runbook: [`zero_shot_thinking_temperature.md`](zero_shot_thinking_temperature.md)
- HTML slides: [`zero_shot_thinking_temperature_slides.html`](zero_shot_thinking_temperature_slides.html)
- Complete local rollout folder: [`../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/`](../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/)
- VS Code workspace: [`../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/inspect-rollouts.code-workspace`](../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/inspect-rollouts.code-workspace)
- Experiment manifest: [`../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/manifest.json`](../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/manifest.json)
- Human-readable analysis: [`../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/analysis/matrix_summary.md`](../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/analysis/matrix_summary.md)
- Machine-readable analysis: [`../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/analysis/matrix_summary.json`](../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/analysis/matrix_summary.json)
- Selected paired qualitative traces: [`../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/analysis/qualitative_trace_pairs.json`](../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/analysis/qualitative_trace_pairs.json)
- Manual T=1.0 episodes: [`../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/qwen3-4b-zs-base-manual/episodes.jsonl`](../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/qwen3-4b-zs-base-manual/episodes.jsonl)
- Manual T=1.3 episodes: [`../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/qwen3-4b-zs-high-temp-manual/episodes.jsonl`](../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/qwen3-4b-zs-high-temp-manual/episodes.jsonl)
- Native T=1.0 episodes: [`../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/qwen3-4b-zs-base-native/episodes.jsonl`](../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/qwen3-4b-zs-base-native/episodes.jsonl)
- Native T=1.3 episodes: [`../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/qwen3-4b-zs-high-temp-native/episodes.jsonl`](../artifacts/zero-shot-thinking/zs-pilot-dgx2-paired-4k-20260819c/qwen3-4b-zs-high-temp-native/episodes.jsonl)

## Operational preferences to preserve in future work

- Never place real experiments on the debug partition.
- Prefer DGX2 for this kind of inference experiment when it is available without a queue.
- Do not repeatedly query Stone or open repeated SSH sessions merely to report progress.
- Submit jobs and allow them to run; inspect at meaningful checkpoints.
- Always include an ETA in experiment-status updates.
- Do not overstate tiny smoke runs; smoke results are interface checks, not scientific evidence.
- Report exact run configuration, number of seeds, denominators, and uncertainty.
- Keep presentations concise, scientific, visually simple, and easy to scan quickly.

