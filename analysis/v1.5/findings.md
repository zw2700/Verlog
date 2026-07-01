# Admission Committee Rollout Findings

Source log:

`logs/episode_log_rollout_anthropic_claude-haiku-4-5-20251001_13799.jsonl`

Category labels are from `analysis/v1/compute_category_metrics.py`.

## Hypothesis 1: shared `prof_1`/`prof_2` top preference causes instant decision

Hypothesis: when `prof_1` and `prof_2` share a mutual top preference and the
early votes align on that shared preference, the episode tends to end as an
instant decision.

Observed:

- There are 28 `instant_decision` episodes.
- 24/28 instant-decision episodes have the first two vote events choosing the
  same student, where that student is a mutual top-ranked choice for the two
  voting professors.
- In all 24 of these episodes, consensus is reached immediately after those two
  aligned votes.
- This is consistent with the environment mechanics: with 3 professors and a
  50% vote threshold, two matching votes are enough to end the game.

Broader related pattern:

- 25/28 instant-decision episodes are explained if we include the case where
  `prof_1` and `prof_2` share a top choice, `prof_1` votes for it, `prof_2`
  publicly agrees but waits for `prof_3`, and `prof_3` casts the deciding vote.
- That extra episode is source line 11, zero-based index 10:
  `epoch-1:step0:env10:episode0`.

The 3 instant-decision episodes not explained by the aligned-first-two-votes
mutual-top pattern are:

| Source line | 0-based index | Episode UID | Vote sequence | Outcome |
|---:|---:|---|---|---|
| 15 | 14 | `epoch-1:step0:env14:episode0` | `prof_1 -> 1`, `prof_2 -> 0`, `prof_3 -> 0` | chosen `0`, optimal `0`, socially optimal |
| 29 | 28 | `epoch-1:step0:env28:episode0` | `prof_1 -> 4`, `prof_2 -> 2`, `prof_3 -> 2` | chosen `2`, optimal `2`, socially optimal |
| 77 | 76 | `epoch-1:step0:env12:episode2` | `prof_1 -> 3`, `prof_2 -> 4`, `prof_3 -> 3` | chosen `3`, optimal `1`, not socially optimal |

Turn-count detail:

- 24/28 instant-decision episodes have 2 recorded model turns.
- 4/28 instant-decision episodes have 3 recorded model turns.
- This uses the analysis script's turn notion: `len(ep["turns"])`.
- The raw logged `total_turns` field differs because it counts non-think action
  messages; composite turns can therefore produce larger raw counts.

## Hypothesis 2: no shared top preference causes no consensus

Hypothesis: when no two professors share the same top preference, the episode is
likely to end with no consensus.

Using "no two professors share the same preference" to mean no pair shares at
least one top-ranked student:

| Scope | Episodes | Consensus | No consensus |
|---|---:|---:|---:|
| All episodes with no pairwise shared top | 35 | 3/35 | 32/35 |
| Negotiation episodes with no pairwise shared top | 34 | 2/34 | 32/34 |

Observed no-consensus mechanism in negotiation episodes:

- 35/35 no-consensus negotiation episodes end with all three professors casting
  valid final votes for three different students.
- 35/35 also have the first three vote events on three different students.
- 30/35 no-consensus negotiation episodes are the especially clean form where
  all three professors vote for different students and each final vote is for
  that professor's own top-ranked student.

Interpretation:

- When there is no pairwise shared top choice, each professor's locally rational
  vote usually points to a different student.
- Under the current environment, the episode terminates with no consensus once
  all professors have valid votes and no student reaches threshold.
- That termination rule prevents repair negotiation after the distinct-vote
  state appears.

Consensus negotiation without any pairwise shared top choice:

| Source line | 0-based index | Episode UID | Vote sequence | Outcome |
|---:|---:|---|---|---|
| 57 | 56 | `epoch-1:step0:env24:episode1` | `prof_1 -> 3`, `prof_2 -> 1`, `prof_3 -> 1` | chosen `1`, optimal `1`, socially optimal |
| 67 | 66 | `epoch-1:step0:env2:episode2` | `prof_1 -> 1`, `prof_2 -> 0`, `prof_3 -> 1` | chosen `1`, optimal `0`, not socially optimal |

## Hypothesis 3: any shared top preference causes consensus

Hypothesis: when any pair of professors shares a top-ranked student, the episode
is likely to reach consensus.

Observed:

| Scope | Episodes | Consensus | No consensus |
|---|---:|---:|---:|
| All episodes with any pairwise shared top | 65 | 62/65 | 3/65 |
| Negotiation episodes with any pairwise shared top | 38 | 35/38 | 3/38 |

Related negotiation split:

| Feature | Consensus negotiation | No-consensus negotiation |
|---|---:|---:|
| Any pair of professors shares a top-ranked student | 35/37 | 3/35 |
| Socially optimal student is top-ranked for at least two professors | 31/37 | 3/35 |
| Final votes are all distinct | 0/37 | 35/35 |
| First three vote events are all distinct | 1/37 | 35/35 |

Interpretation:

- Consensus negotiation usually has a visible coordination target in the
  utility structure: at least two professors share a top choice.
- No-consensus negotiation rarely has such a target.
- Even when a shared-top target exists, the agents can miss it if their first
  valid votes split three ways and the current termination rule ends the game.

No-consensus negotiation despite a pairwise shared top choice:

| Source line | 0-based index | Episode UID | Vote sequence | Shared/optimal top target |
|---:|---:|---|---|---|
| 42 | 41 | `epoch-1:step0:env9:episode1` | `prof_1 -> 1`, `prof_2 -> 2`, `prof_3 -> 3` | student `3` is top for `prof_1` and `prof_3`, and is optimal |
| 52 | 51 | `epoch-1:step0:env19:episode1` | `prof_1 -> 2`, `prof_2 -> 3`, `prof_3 -> 4` | student `4` is top for `prof_1` and `prof_3`, and is optimal |
| 75 | 74 | `epoch-1:step0:env10:episode2` | `prof_1 -> 4`, `prof_2 -> 1`, `prof_3 -> 3` | student `1` is top for `prof_1` and `prof_2`, and is optimal |

## Exclusive pair patterns

This section partitions episodes by exactly which professor pairs share at
least one top-ranked student.

| Exclusive shared-top pattern | Episodes | Instant decision | Negotiation + consensus | Negotiation + no consensus |
|---|---:|---:|---:|---:|
| No pair shares top | 35 | 1 | 2 | 32 |
| Only `prof_1`/`prof_2` share top | 17 | 14 | 2 | 1 |
| Only `prof_1`/`prof_3` share top | 20 | 0 | 18 | 2 |
| Only `prof_2`/`prof_3` share top | 17 | 2 | 15 | 0 |
| All three pairings share top | 11 | 11 | 0 | 0 |

Interpretation:

- `prof_1`/`prof_2` shared top strongly predicts instant decision because those
  two professors usually act before `prof_3` under the default turn order.
- Shared top involving `prof_3`, without `prof_1`/`prof_2`, usually becomes
  negotiation with consensus.
- When all three pairings share top, the episode still becomes instant decision
  because the `prof_1`/`prof_2` early-action path is present.
