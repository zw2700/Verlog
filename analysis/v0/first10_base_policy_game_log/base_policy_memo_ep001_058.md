# Base Policy Categorization Memo: Episodes 1-58

## Scope

Assigned range: episodes 1 through 58 inclusive, using `logs/game_log_train_auton_12993.log` before line 144892. Episode IDs are 1-indexed by diagnosis blocks before the cutoff.

## Category Counts

- `negotiation_like`: 17
- `proposal_following`: 13
- `thin_candidate_discussion`: 13
- `instant_consensus`: 7
- `coordination_theater`: 5
- `stalled_waiting_loop`: 3

## Representative Episodes

- Episode 1 (`instant_consensus`): two immediate Student 2 votes produced consensus with no public deliberation.
- Episode 14 (`negotiation_like`): Students 0 and 2 were weighed as compromise options, and prof_3 shifted toward Student 2 to align with prof_1.
- Episode 33 (`coordination_theater`): the conversation became repeated requests for utility scores and vote preferences, with no useful candidate tradeoff.
- Episode 47 (`stalled_waiting_loop`): 47 turns of repeated proposals and wait-for loops eventually reached Student 2, but waiting/repetition dominated the behavior.
- Episode 55 (`negotiation_like`): prof_1 pushed Student 2, prof_3 pushed Student 0, and prof_1 switched to Student 0 to avoid no consensus.

## Low-Confidence Or Borderline Episodes

Low or medium confidence episodes: 13, 16, 20, 22, 31, 33, 36, 37, 40, 42, 44, 48, 52, 56, 58.

The main borderline pattern is shallow candidate comparison that uses negotiation vocabulary without much effective response. Episodes 13, 36, 42, 48, 56, and 58 contain counterproposals or fallback language, so I labeled them `negotiation_like`, but several are noisy or repetitive enough that they sit close to `thin_candidate_discussion`. Episode 20 is especially noisy because malformed multiple-vote outputs dominate, but enough candidate content remains to avoid the `execution_breakdown` override.

## Suggested New Categories

None. The fixed taxonomy covered the range. Some episodes show repetitive pseudo-bargaining or self-referential exchange offers, but `coordination_theater`, `thin_candidate_discussion`, and low-confidence `negotiation_like` were sufficient without adding a new category.

## Negotiation-Like Behavior

Negotiation-like behavior appears in 17 of 58 episodes. It is usually weak: agents name alternatives, propose fallbacks, or switch votes for consensus, but often do so with shallow or malformed reasoning. 10 of those negotiation-like episodes reached consensus. The clearest examples are episodes 14, 24, 25, 41, 45, and 55, where public messages explicitly compare candidates or use compromise/switching language.
