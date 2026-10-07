# Repeated unanimous admissions bargaining

## Replacement: hidden random horizon

The fixed-five-round run described below was cancelled at the user's request.
The active replacement uses `artifacts/prompt-hidden-horizon-20260916/` and
200 paired sessions with independent 80% continuation after each decision.
Session lengths are drawn once with Python Random seed 9162026 and matched
between prompts: 1129 decisions per prompt, longest session 29 decisions.
There is no fixed decision-count cap. The scheduler walltime is a safety limit,
not a terminal game outcome; interrupted sessions must not count as completed.

The original system prompt is retained, with only this addition in both variants:
"You interact with the same professors over multiple turns. Previous public
messages and decisions remain visible." No horizon, probability, counter,
cross-decision objective, or private payoff ledger is shown. The discussion
variant additionally retains the same discussion strategy as earlier studies.
Observations distinguish completed public interaction from current candidates
and votes. Past transcript headings carry no decision number. Preferences stay
fixed, with fresh students/votes/budgets as before. Cumulative selection utility
is recorded for analysis only, not disclosed as a new objective.

Model context is 32768 tokens to support longer histories. Before requests,
the exact cached model tokenizer checks available space, reserving output tokens;
only when necessary, oldest completed public transcripts are omitted, with an
explicit omission notice. Current decision text is retained. Such omissions
are visible in raw observations and should be considered when interpreting
long-session behavior. The original whitespace-counted message budget remains.

Four focused tests passed. The end-to-end fake-model check used lengths 7 and 1,
verified paired scenarios, and generated sixteen aggregate/per-decision plots.
The replacement requests one free H200, 16 CPUs, 64 GB RAM, and four hours.
Exact submission settings and source snapshots are saved alongside results.

## Archived fixed-five-round pilot

Scheduled as Slurm job **55152**, named `experiment`, on September 16, 2026.
Requests one A6000, 16 CPUs, 64 GB RAM, and eight hours in `general`, excluding
nodes shared with preemptible jobs. Remote checkout:
`/zfsauton/scratch/mwilinsk/unscripted/experiments/zero-shot-thinking-e888c0e2`.
Artifacts: `artifacts/prompt-repeated-unanimity-20260916/repeated-comparison/`.
The parent artifact directory stores the exact submission settings and job ID.

Validation: three focused environment tests passed; two five-round paired
fake-model sessions completed, verifying scenario pairing and generating all
12 expected plots (two aggregate, ten by round). Fake runs are excluded from
the real sampling results.

This is a five-round repeated bargaining session, not an iterated prisoner's
dilemma payoff matrix. The original strategic admissions actions and per-round
payoffs remain in place. There is no training or added cooperation reward.

Compare the original prompt with the same discussion guidance used in the
single-round studies. Both receive the repeated-session rules and maximize
the undiscounted sum of their own selection utilities. The horizon is known;
the fifth round has no future interaction, so end-of-session effects are
possible.

Use 200 independent sessions per prompt, five rounds each (1000 decisions per
condition), Qwen3-4B at its initial revision, and unanimous three-of-three voting.
The three identities and private preferences are fixed within each session.
Every round draws new students, resets the vote tally, scheduler, and 500-word
message budget, and permits at most 50 turns. The inherited inference runner
does not supply an environment tokenizer, so its existing 'token' budget is
counted by whitespace words. This convention matches the other two sampling
sets and should not be confused with model-token limits.

Consensus or exhaustion ends the round, never the entire session. Failure
gives zero selection utility for that round; later rounds still occur. Existing
format/action penalties remain unchanged and are logged separately from the
selection-utility totals. The outer runner records cumulative selection utility;
it does not implement cross-round training credit assignment.

Memory contains all earlier public GROUP messages, each round's final vote
tally, selected candidate's public profile or failure, and each agent's own
realized utilities. Intermediate vote changes remain in raw logs but are not
replayed as session memory. Private THINK text, others' utility values, and
future student batches are never inserted into shared memory. Numeric utility
nondisclosure remains an instruction to the agents; this is not an enforcement
mechanism against an agent choosing to disclose its own numbers publicly.

Scenario seed = session ID + 1000 * zero-based round. Both prompt conditions use
the same sequence and persistent preference vectors. The first round matches
the existing single-round experiment's scenario for that session ID. Public
history is generated independently in each condition because actions differ.
Condition order alternates by session ID; worker processes isolate random state.

Both conditions use a 16384-token model context and 512 generated tokens per
turn, with the existing temperature/top-p/manual-reasoning settings. The larger
context accommodates previous-round memory; it differs from the single-round
experiments. Sampling results are not a trained repeated-game policy.

Output includes raw round logs, per-session cumulative utility, aggregate
preference-scenario plots, and plots/metrics separately for rounds 1–5. Treat
the session as the independent statistical unit. A rise in discussion length
or later-round welfare alone does not prove reciprocity; persistent preferences
also allow agents to learn one another's interests. A later history-reset
control would help isolate the effect of remembered interaction.

Implementation: `scripts/repeated_admissions.py` adapts one round;
`scripts/rollout_repeated_comparison.py` manages sessions and invokes the existing
inference and plotting code. The ordinary environment and existing running
experiments are unchanged. For training, session transitions and cumulative
returns must be integrated into the training wrapper before running PPO.
