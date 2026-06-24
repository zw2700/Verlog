# Base-Policy Categorization Memo: Episodes 175-232

## Range

Assigned range: episodes 175 through 232 inclusive, using `logs/game_log_train_auton_12993.log` before line 144892. Episodes are 1-indexed by `EPISODE DIAGNOSIS` blocks before the cutoff.

## Category Counts

- `coordination_theater`: 8
- `instant_consensus`: 8
- `negotiation_like`: 12
- `proposal_following`: 14
- `stalled_waiting_loop`: 2
- `thin_candidate_discussion`: 14

Outcome notes: 42 episodes reached consensus and 16 did not. Among the consensus episodes, 16 chose the visible social optimum, 25 chose a visible suboptimal candidate, and 1 had unknown social optimum. The remaining 16 `social_optimum_unknown` tags are the no-consensus episodes.

## Representative Episodes

- Episode 175 (`negotiation_like`): Student 4 and Student 2 compete, and prof_1 eventually offers Student 2 as a compromise while preserving Student 4 for later discussion.
- Episode 185 (`stalled_waiting_loop`): the agents keep asking to review the Student 2 voting situation and never make progress.
- Episode 198 (`negotiation_like`): Student 2 and Student 3 receive sustained arguments about group fit, but no consensus forms.
- Episode 224 (`negotiation_like`): prof_2 explicitly accepts Student 1 despite a lower preference to promote team cohesion.
- Episode 227 (`coordination_theater`): the public discussion loops on sharing utilities and waiting for prof_1 while Student 3 support accumulates.

## Borderline / Low Confidence Notes

No labels are low-confidence. Medium-confidence cases are: 175, 176, 177, 179, 180, 187, 188, 189, 191, 192, 196, 199, 200, 204, 205, 206, 210, 211, 212, 214, 216, 218, 220, 221, 222, 223, 225, 228, 231, 232.

- Episodes 179, 192, 199, 211, 218, and 221 are borderline `negotiation_like`: they contain compromise or vote-switch language, but the reasoning is often brief or messy.
- Episodes 187, 188, 205, 206, 210, 216, 228, and 232 are borderline `thin_candidate_discussion`: multiple candidates are named, but adaptation is too weak for `negotiation_like`.
- Episode 184 has `social_optimum_unknown` because prof_3 had zero turns, so their full utility vector was not visible.

## Suggested New Categories

No new primary category is suggested. The existing taxonomy covered the observed behaviors: quick focal votes, endorsement chains, process-heavy coordination loops, shallow candidate talk, stalled waiting, and a small number of negotiation-like exchanges.

## Desired Negotiation-Like Behavior

Negotiation-like behavior appears, but it is not dominant. The clearest examples are episodes 175, 183, 198, 211, 217, 224, and 229, where agents publicly compare alternatives or use compromise language. Even these rarely become robust socially optimal negotiation; many end in no consensus or choose a suboptimal candidate, and much of the range is dominated by proposal following, thin discussion, or coordination theater.
