# Final 10 Training Steps Behavior Analysis

## Scope

- Source: `logs/agent_model_train_auton_12993.log`
- Training steps: `global_steps=66..75`
- Episodes labeled: `716` complete bounded episodes
- Boundary fragments are excluded from category percentages.

## Category Summary

| Primary category | Count | Percent | Consensus yes | Consensus rate |
|---|---:|---:|---:|---:|
| `negotiation_like` | 1 | 0.1% | 1 | 100.0% |
| `proposal_following` | 109 | 15.2% | 109 | 100.0% |
| `thin_candidate_discussion` | 66 | 9.2% | 26 | 39.4% |
| `instant_consensus` | 467 | 65.2% | 450 | 96.4% |
| `coordination_theater` | 41 | 5.7% | 38 | 92.7% |
| `stalled_waiting_loop` | 31 | 4.3% | 6 | 19.4% |
| `execution_breakdown` | 1 | 0.1% | 0 | 0.0% |

## Main Readout

`negotiation_like` appears in 1/716 episodes (0.1%).
`instant_consensus` and `proposal_following` together account for 576/716 episodes (80.4%).
`vote_only` appears in 448 episodes and `no_public_messages` appears in 481 episodes.

## Confidence

| Confidence | Count | Percent |
|---|---:|---:|
| `high` | 612 | 85.5% |
| `medium` | 100 | 14.0% |
| `low` | 4 | 0.6% |

## Representative Episodes

### `negotiation_like`

- Episode 123 segment 297: consensus=True, chosen=2, confidence=medium. The episode included a visible shift toward another professor's preferred candidate, giving it limited compromise-like structure despite sparse rationale.
  Excerpt: "Let's go with Student 2 and support their preference."

### `proposal_following`

- Episode 3 segment 579: consensus=True, chosen=1, confidence=high. One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
  Excerpt: "Student 1 is the best fit for my research interests."
- Episode 12 segment 341: consensus=True, chosen=2, confidence=high. One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
  Excerpt: "Student 2 is the most promising candidate based on my preferences."
- Episode 19 segment 614: consensus=True, chosen=0, confidence=high. One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
  Excerpt: "I propose student 0"

### `thin_candidate_discussion`

- Episode 18 segment 412: consensus=False, chosen=none, confidence=high. Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
  Excerpt: "<VOTE>4</VOTE>"
- Episode 21 segment 293: consensus=True, chosen=4, confidence=medium. Candidate mentions or vote patterns stayed shallow and did not develop into clear tradeoff reasoning or compromise.
  Excerpt: "Let's make the case for Student 4"
- Episode 27 segment 550: consensus=False, chosen=none, confidence=medium. Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
  Excerpt: "Let's finalize Student 2 together"

### `instant_consensus`

- Episode 1 segment 674: consensus=True, chosen=1, confidence=high. Consensus formed within 2 turns through votes alone, with no public candidate comparison.
  Excerpt: "<VOTE>1</VOTE>"
- Episode 2 segment 516: consensus=True, chosen=2, confidence=high. Consensus formed within 3 turns through votes alone, with no public candidate comparison.
  Excerpt: "<VOTE>2</VOTE>"
- Episode 6 segment 411: consensus=True, chosen=2, confidence=high. Consensus formed within 2 turns through votes alone, with no public candidate comparison.
  Excerpt: "<VOTE>2</VOTE>"

### `coordination_theater`

- Episode 4 segment 45: consensus=True, chosen=3, confidence=high. The public behavior centered on checking reactions, waiting, or generic coordination language rather than useful candidate tradeoffs.
  Excerpt: "Let's see how prof_1 is feeling about this. If they prefer student 3, I'll consider that as well."
- Episode 5 segment 310: consensus=True, chosen=2, confidence=high. The public behavior centered on checking reactions, waiting, or generic coordination language rather than useful candidate tradeoffs.
  Excerpt: "Let's see how prof_1 reacts to this."
- Episode 11 segment 645: consensus=True, chosen=2, confidence=medium. The public behavior centered on checking reactions, waiting, or generic coordination language rather than useful candidate tradeoffs.
  Excerpt: "I will finalize my decision and vote for Student 4, as their high utility score aligns well with my research interest..."

### `stalled_waiting_loop`

- Episode 9 segment 644: consensus=False, chosen=none, confidence=high. Waiting or repeated wait-for behavior dominated the episode and delayed or prevented substantive progress.
  Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"
- Episode 15 segment 549: consensus=False, chosen=none, confidence=high. Waiting or repeated wait-for behavior dominated the episode and delayed or prevented substantive progress.
  Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"
- Episode 17 segment 600: consensus=False, chosen=none, confidence=high. Waiting or repeated wait-for behavior dominated the episode and delayed or prevented substantive progress.
  Excerpt: "<WAIT>"

### `execution_breakdown`

- Episode 84 segment 19: consensus=False, chosen=none, confidence=medium. The only public action was malformed or incoherent enough that normal deliberation behavior could not be classified reliably.
  Excerpt: "<VIEW>GROUP>Welcome, all. Let's start by sharing our initial thoughts and preferences. I will then use this informati..."

## Full Episode Appendix

### Complete Episode 1

- Segment/env: `674` / `28`
- Lines: `12887918-12891851`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 2

- Segment/env: `516` / `22`
- Lines: `12888010-12897242`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `preference_probe`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 3

- Segment/env: `579` / `24`
- Lines: `12888103-12896850`
- Steps: `66-66`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`, `preference_probe`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `1` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Student 1 is the best fit for my research interests."

### Complete Episode 4

- Segment/env: `45` / `2`
- Lines: `12888292-12895905`
- Steps: `66-66`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `candidate_comparison`, `preference_probe`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `1` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: The public behavior centered on checking reactions, waiting, or generic coordination language rather than useful candidate tradeoffs.
- Excerpt: "Let's see how prof_1 is feeling about this. If they prefer student 3, I'll consider that as well."

### Complete Episode 5

- Segment/env: `310` / `13`
- Lines: `12888384-12895807`
- Steps: `66-66`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `2`
- Waits/wait_for: `0` / `2`
- Confidence: `high`
- Rationale: The public behavior centered on checking reactions, waiting, or generic coordination language rather than useful candidate tradeoffs.
- Excerpt: "Let's see how prof_1 reacts to this."

### Complete Episode 6

- Segment/env: `411` / `17`
- Lines: `12888590-12892274`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 7

- Segment/env: `14` / `1`
- Lines: `12888682-12894177`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 8

- Segment/env: `599` / `25`
- Lines: `12888774-12891946`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 9

- Segment/env: `644` / `27`
- Lines: `12889885-12889885`
- Steps: `66-66`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or repeated wait-for behavior dominated the episode and delayed or prevented substantive progress.
- Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 10

- Segment/env: `292` / `12`
- Lines: `12889977-12893730`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE><WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 11

- Segment/env: `645` / `27`
- Lines: `12892576-12907048`
- Steps: `66-66`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `preference_probe`, `placeholder_output`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `4` / `1` / `4`
- Waits/wait_for: `0` / `3`
- Confidence: `medium`
- Rationale: The public behavior centered on checking reactions, waiting, or generic coordination language rather than useful candidate tradeoffs.
- Excerpt: "I will finalize my decision and vote for Student 4, as their high utility score aligns well with my research interest..."

### Complete Episode 12

- Segment/env: `341` / `14`
- Lines: `12892668-12896112`
- Steps: `66-66`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Student 2 is the most promising candidate based on my preferences."

### Complete Episode 13

- Segment/env: `245` / `10`
- Lines: `12893382-12896609`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 14

- Segment/env: `422` / `18`
- Lines: `12894085-12900735`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 15

- Segment/env: `549` / `23`
- Lines: `12894702-12894702`
- Steps: `66-66`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or repeated wait-for behavior dominated the episode and delayed or prevented substantive progress.
- Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 16

- Segment/env: `442` / `19`
- Lines: `12894794-12899136`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 17

- Segment/env: `600` / `25`
- Lines: `12894887-12894887`
- Steps: `66-66`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `1` / `0`
- Confidence: `high`
- Rationale: Waiting or repeated wait-for behavior dominated the episode and delayed or prevented substantive progress.
- Excerpt: "<WAIT>"

### Complete Episode 18

- Segment/env: `412` / `17`
- Lines: `12895151-12903272`
- Steps: `66-66`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 19

- Segment/env: `614` / `26`
- Lines: `12896208-12903774`
- Steps: `66-66`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`, `counterproposal`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "I propose student 0"

### Complete Episode 20

- Segment/env: `15` / `1`
- Lines: `12896300-12899857`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 21

- Segment/env: `293` / `12`
- Lines: `12897150-12904349`
- Steps: `66-66`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`, `counterproposal`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Candidate mentions or vote patterns stayed shallow and did not develop into clear tradeoff reasoning or compromise.
- Excerpt: "Let's make the case for Student 4"

### Complete Episode 22

- Segment/env: `115` / `5`
- Lines: `12897337-12900948`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 23

- Segment/env: `367` / `15`
- Lines: `12897525-12903870`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 24

- Segment/env: `675` / `28`
- Lines: `12897618-12901535`
- Steps: `66-66`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `2` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Let's go with Student 2"

### Complete Episode 25

- Segment/env: `601` / `25`
- Lines: `12897833-12902873`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 26

- Segment/env: `215` / `9`
- Lines: `12898287-12903678`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 27

- Segment/env: `550` / `23`
- Lines: `12898724-12911968`
- Steps: `66-66`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `4` / `2` / `4`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Let's finalize Student 2 together"

### Complete Episode 28

- Segment/env: `750` / `31`
- Lines: `12898911-12974006`
- Steps: `66-69`
- Category: `stalled_waiting_loop`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `counterproposal`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `placeholder_output`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `29` / `0` / `19`
- Waits/wait_for: `1` / `10`
- Confidence: `medium`
- Rationale: Waiting or repeated wait-for behavior dominated the episode and delayed or prevented substantive progress.
- Excerpt: "<VOTE>3</VOTE><WAIT>"

### Complete Episode 29

- Segment/env: `46` / `2`
- Lines: `12899348-12902453`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 30

- Segment/env: `311` / `13`
- Lines: `12899765-12907338`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 31

- Segment/env: `342` / `14`
- Lines: `12900154-12900154`
- Steps: `66-66`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or repeated wait-for behavior dominated the episode and delayed or prevented substantive progress.
- Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 32

- Segment/env: `383` / `16`
- Lines: `12900246-12904445`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 33

- Segment/env: `702` / `29`
- Lines: `12900458-12908250`
- Steps: `66-66`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Let's choose Student 2"

### Complete Episode 34

- Segment/env: `580` / `24`
- Lines: `12900550-12906106`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 35

- Segment/env: `246` / `10`
- Lines: `12900643-12904253`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 36

- Segment/env: `517` / `22`
- Lines: `12901867-12908612`
- Steps: `66-66`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The public behavior centered on checking reactions, waiting, or generic coordination language rather than useful candidate tradeoffs.
- Excerpt: "Let's see if we can come to a consensus."

### Complete Episode 37

- Segment/env: `443` / `19`
- Lines: `12902217-12905166`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 38

- Segment/env: `16` / `1`
- Lines: `12902660-12905792`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 39

- Segment/env: `159` / `7`
- Lines: `12902969-12906748`
- Steps: `66-66`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: The public behavior centered on checking reactions, waiting, or generic coordination language rather than useful candidate tradeoffs.
- Excerpt: "Let's see how other professors react and what they might prefer."

### Complete Episode 40

- Segment/env: `423` / `18`
- Lines: `12903179-12910654`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 41

- Segment/env: `343` / `14`
- Lines: `12903368-12985422`
- Steps: `66-69`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `24` / `19` / `19`
- Waits/wait_for: `0` / `6`
- Confidence: `medium`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Let's go with Student 2"

### Complete Episode 42

- Segment/env: `47` / `2`
- Lines: `12904649-12907959`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 43

- Segment/env: `676` / `28`
- Lines: `12904982-12912351`
- Steps: `66-66`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 44

- Segment/env: `116` / `5`
- Lines: `12905074-12909277`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 45

- Segment/env: `602` / `25`
- Lines: `12905700-12911137`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 46

- Segment/env: `413` / `17`
- Lines: `12905888-13076183`
- Steps: `66-73`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `50` / `24` / `43`
- Waits/wait_for: `1` / `2`
- Confidence: `medium`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Decision: Selected Student 3"

### Complete Episode 47

- Segment/env: `216` / `9`
- Lines: `12906322-12917322`
- Steps: `66-67`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Hello all, I believe Student 3 is very well-suited to our program. I value their comprehensive skill set. Let me know..."

### Complete Episode 48

- Segment/env: `444` / `19`
- Lines: `12906655-12976919`
- Steps: `66-69`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`, `counterproposal`, `preference_probe`, `vote_switch`, `repeated_proposal`, `compromise_language`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `18` / `2` / `14`
- Waits/wait_for: `0` / `9`
- Confidence: `medium`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Let's aim for consensus!"

### Complete Episode 49

- Segment/env: `247` / `10`
- Lines: `12906843-12917850`
- Steps: `66-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `counterproposal`, `preference_probe`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 50

- Segment/env: `368` / `15`
- Lines: `12907151-12910041`
- Steps: `66-66`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Let's focus on Student 2."

### Complete Episode 51

- Segment/env: `615` / `26`
- Lines: `12907543-12912889`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 52

- Segment/env: `294` / `12`
- Lines: `12907635-12915139`
- Steps: `66-67`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: Candidate mentions or vote patterns stayed shallow and did not develop into clear tradeoff reasoning or compromise.
- Excerpt: "I recommend Student 4 for the committee. Let's move forward with this selection."

### Complete Episode 53

- Segment/env: `384` / `16`
- Lines: `12907727-12917130`
- Steps: `66-67`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Let's focus on Student 3"

### Complete Episode 54

- Segment/env: `581` / `24`
- Lines: `12908803-12915235`
- Steps: `66-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `preference_probe`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 55

- Segment/env: `17` / `1`
- Lines: `12909000-12912698`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 56

- Segment/env: `160` / `7`
- Lines: `12909092-12915331`
- Steps: `66-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `candidate_comparison`, `counterproposal`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns after only a brief public statement and no substantive deliberation.
- Excerpt: "Student 2 is the top choice based on my preferences and the ability vectors."

### Complete Episode 57

- Segment/env: `646` / `27`
- Lines: `12909184-12925947`
- Steps: `66-67`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `5` / `1` / `4`
- Waits/wait_for: `0` / `2`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Student 2 is particularly strong in AI/ML and CompBio, which is beneficial for my research interests."

### Complete Episode 58

- Segment/env: `312` / `13`
- Lines: `12909495-12914621`
- Steps: `66-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 59

- Segment/env: `492` / `21`
- Lines: `12910470-12913618`
- Steps: `66-66`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 60

- Segment/env: `48` / `2`
- Lines: `12910562-12933277`
- Steps: `66-67`
- Category: `stalled_waiting_loop`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `candidate_comparison`, `counterproposal`, `preference_probe`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `8` / `1` / `5`
- Waits/wait_for: `1` / `3`
- Confidence: `medium`
- Rationale: Waiting or repeated wait-for behavior dominated the episode and delayed or prevented substantive progress.
- Excerpt: "Let's go with Student 3"

### Complete Episode 61

- Segment/env: `518` / `22`
- Lines: `12910852-12916357`
- Steps: `66-67`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Let's ensure we have a strong candidate. I'll also send a message to both prof_1 and prof_2 for their feedback."

### Complete Episode 62

- Segment/env: `273` / `11`
- Lines: `12911329-12920637`
- Steps: `66-67`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `candidate_comparison`, `counterproposal`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Candidate mentions or vote patterns stayed shallow and did not develop into clear tradeoff reasoning or compromise.
- Excerpt: "Let's focus on Student 3"

### Complete Episode 63

- Segment/env: `117` / `5`
- Lines: `12911421-12918966`
- Steps: `66-67`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Let's discuss the talented Student 2"

### Complete Episode 64

- Segment/env: `703` / `29`
- Lines: `12912164-12915520`
- Steps: `66-67`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`, `preference_probe`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Let's consider this strong candidate for our group."

### Complete Episode 65

- Segment/env: `369` / `15`
- Lines: `12912985-12918459`
- Steps: `66-67`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `counterproposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Let's bring in more AI/ML and CompBio expertise to our research team."

### Complete Episode 66

- Segment/env: `424` / `18`
- Lines: `12913172-12996980`
- Steps: `66-70`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `placeholder_output`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `21` / `12` / `14`
- Waits/wait_for: `0` / `10`
- Confidence: `medium`
- Rationale: Waiting or repeated wait-for behavior dominated the episode and delayed or prevented substantive progress.
- Excerpt: "Let's get this student on board."

### Complete Episode 67

- Segment/env: `551` / `23`
- Lines: `12914247-12919967`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 68

- Segment/env: `603` / `25`
- Lines: `12914340-12920441`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 69

- Segment/env: `18` / `1`
- Lines: `12914529-12917946`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 70

- Segment/env: `493` / `21`
- Lines: `12914951-12918042`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 71

- Segment/env: `616` / `26`
- Lines: `12915428-12923323`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `counterproposal`, `preference_probe`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: Consensus formed within 3 turns after only a brief public statement and no substantive deliberation.
- Excerpt: "Let's work together!"

### Complete Episode 72

- Segment/env: `677` / `28`
- Lines: `12915721-12919548`
- Steps: `67-67`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Vote for Student 4"

### Complete Episode 73

- Segment/env: `313` / `13`
- Lines: `12917758-12922602`
- Steps: `67-67`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Prof_1, please consider Student 2's strong utility and balanced skills. I stand by my vote if you're unsure."

### Complete Episode 74

- Segment/env: `295` / `12`
- Lines: `12918137-12921533`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 75

- Segment/env: `582` / `24`
- Lines: `12918367-12922034`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 76

- Segment/env: `161` / `7`
- Lines: `12918555-12921748`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 77

- Segment/env: `704` / `29`
- Lines: `12918648-12924617`
- Steps: `67-67`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 78

- Segment/env: `519` / `22`
- Lines: `12919063-12923603`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 79

- Segment/env: `385` / `16`
- Lines: `12919155-12921843`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 80

- Segment/env: `494` / `21`
- Lines: `12919767-12922984`
- Steps: `67-67`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Based on the utility scores, Student 3 seems to be the best match for my research interests."

### Complete Episode 81

- Segment/env: `118` / `5`
- Lines: `12920972-12927701`
- Steps: `67-67`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Let's focus on Quality Improvement."

### Complete Episode 82

- Segment/env: `217` / `9`
- Lines: `12921197-12927510`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 83

- Segment/env: `248` / `10`
- Lines: `12922129-12926660`
- Steps: `67-67`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Looking at the other students, Student 4 also seems very promising, especially in CompBio and Systems. I will also me..."

### Complete Episode 84

- Segment/env: `19` / `1`
- Lines: `12922221-12922221`
- Steps: `67-67`
- Category: `execution_breakdown`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `invalid_action`, `malformed_tags`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The only public action was malformed or incoherent enough that normal deliberation behavior could not be classified reliably.
- Excerpt: "<VIEW>GROUP>Welcome, all. Let's start by sharing our initial thoughts and preferences. I will then use this informati..."

### Complete Episode 85

- Segment/env: `552` / `23`
- Lines: `12922314-12926564`
- Steps: `67-67`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "My pick is Student 2, who excels in AI/ML and CompBio; do you share the same sentiment, prof_1?"

### Complete Episode 86

- Segment/env: `370` / `15`
- Lines: `12922407-12924714`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 87

- Segment/env: `604` / `25`
- Lines: `12922700-12926235`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 88

- Segment/env: `678` / `28`
- Lines: `12922892-12922892`
- Steps: `67-67`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or repeated wait-for behavior dominated the episode and delayed or prevented substantive progress.
- Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 89

- Segment/env: `162` / `7`
- Lines: `12923419-12929537`
- Steps: `67-67`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Lets consider Student 2's strengths carefully."

### Complete Episode 90

- Segment/env: `274` / `11`
- Lines: `12923511-12927415`
- Steps: `67-67`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Suggest voting for Student 1"

### Complete Episode 91

- Segment/env: `386` / `16`
- Lines: `12924096-12930241`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 92

- Segment/env: `296` / `12`
- Lines: `12924392-12933181`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `preference_probe`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 93

- Segment/env: `583` / `24`
- Lines: `12924810-12927932`
- Steps: `67-67`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Let's select Student 2"

### Complete Episode 94

- Segment/env: `314` / `13`
- Lines: `12925100-12960241`
- Steps: `67-68`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `10` / `1` / `8`
- Waits/wait_for: `0` / `2`
- Confidence: `medium`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Let's move Student 4 to the top of the pile and show my support."

### Complete Episode 95

- Segment/env: `20` / `1`
- Lines: `12925288-12939274`
- Steps: `67-67`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`, `placeholder_output`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `5` / `1` / `4`
- Waits/wait_for: `1` / `0`
- Confidence: `medium`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Based on the current utilities, Student 3 seems to be the best fit for maximizing my utility. Professors prof_2 and p..."

### Complete Episode 96

- Segment/env: `679` / `28`
- Lines: `12925380-12928123`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 97

- Segment/env: `495` / `21`
- Lines: `12926143-12931694`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 98

- Segment/env: `520` / `22`
- Lines: `12926330-12933085`
- Steps: `67-67`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 99

- Segment/env: `617` / `26`
- Lines: `12926756-12929635`
- Steps: `67-67`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Student 3 is highly qualified"

### Complete Episode 100

- Segment/env: `371` / `15`
- Lines: `12927214-12930146`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 101

- Segment/env: `705` / `29`
- Lines: `12928218-12933583`
- Steps: `67-67`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: Candidate mentions or vote patterns stayed shallow and did not develop into clear tradeoff reasoning or compromise.
- Excerpt: "Let's focus on Student 1"

### Complete Episode 102

- Segment/env: `724` / `30`
- Lines: `12928746-12934028`
- Steps: `67-67`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Let's leverage Student 4's strengths."

### Complete Episode 103

- Segment/env: `647` / `27`
- Lines: `12929147-12931374`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 104

- Segment/env: `605` / `25`
- Lines: `12929731-12932335`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 105

- Segment/env: `275` / `11`
- Lines: `12929961-12936274`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 106

- Segment/env: `553` / `23`
- Lines: `12930054-12932146`
- Steps: `67-67`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Let's choose Student 2"

### Complete Episode 107

- Segment/env: `249` / `10`
- Lines: `12930338-12933381`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 108

- Segment/env: `218` / `9`
- Lines: `12930430-12938594`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 109

- Segment/env: `680` / `28`
- Lines: `12930522-12933791`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 110

- Segment/env: `584` / `24`
- Lines: `12930950-12940008`
- Steps: `67-67`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `counterproposal`, `preference_probe`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The public behavior centered on checking reactions, waiting, or generic coordination language rather than useful candidate tradeoffs.
- Excerpt: "Let's see how I'm doing"

### Complete Episode 111

- Segment/env: `119` / `5`
- Lines: `12931469-12965757`
- Steps: `67-68`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `9` / `5` / `7`
- Waits/wait_for: `0` / `4`
- Confidence: `medium`
- Rationale: Waiting or repeated wait-for behavior dominated the episode and delayed or prevented substantive progress.
- Excerpt: "Let's go with Student 1"

### Complete Episode 112

- Segment/env: `372` / `15`
- Lines: `12932242-12937679`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 113

- Segment/env: `618` / `26`
- Lines: `12932665-12962510`
- Steps: `67-68`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `9` / `4` / `5`
- Waits/wait_for: `0` / `4`
- Confidence: `medium`
- Rationale: The public behavior centered on checking reactions, waiting, or generic coordination language rather than useful candidate tradeoffs.
- Excerpt: "Vote for Student 1"

### Complete Episode 114

- Segment/env: `163` / `7`
- Lines: `12932993-12965116`
- Steps: `67-68`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `9` / `2` / `6`
- Waits/wait_for: `0` / `3`
- Confidence: `medium`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Let's vote for Student 3 together to maximize our chances of reaching a consensus."

### Complete Episode 115

- Segment/env: `387` / `16`
- Lines: `12934124-12943038`
- Steps: `67-68`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Let's consider Student 4 the strongest initial choice."

### Complete Episode 116

- Segment/env: `648` / `27`
- Lines: `12934408-12940307`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 117

- Segment/env: `496` / `21`
- Lines: `12934500-12942942`
- Steps: `67-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 118

- Segment/env: `606` / `25`
- Lines: `12934796-12941073`
- Steps: `67-68`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `candidate_comparison`, `counterproposal`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Let's focus on Student 4 as they seem to match my preferences well."

### Complete Episode 119

- Segment/env: `554` / `23`
- Lines: `12934888-12941868`
- Steps: `67-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `preference_probe`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 120

- Segment/env: `250` / `10`
- Lines: `12935114-12938062`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 121

- Segment/env: `521` / `22`
- Lines: `12935397-12938783`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 122

- Segment/env: `49` / `2`
- Lines: `12935490-12942656`
- Steps: `67-68`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 123

- Segment/env: `297` / `12`
- Lines: `12935946-12967314`
- Steps: `67-68`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `candidate_comparison`, `counterproposal`, `preference_probe`, `vote_switch`, `compromise_language`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `10` / `1` / `5`
- Waits/wait_for: `0` / `5`
- Confidence: `medium`
- Rationale: The episode included a visible shift toward another professor's preferred candidate, giving it limited compromise-like structure despite sparse rationale.
- Excerpt: "Let's go with Student 2 and support their preference."

### Complete Episode 124

- Segment/env: `706` / `29`
- Lines: `12936465-12947016`
- Steps: `67-68`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`, `vote_switch`, `compromise_language`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `4` / `1` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "vote for Student 4"

### Complete Episode 125

- Segment/env: `681` / `28`
- Lines: `12936558-12939083`
- Steps: `67-67`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 126

- Segment/env: `725` / `30`
- Lines: `12937243-12937243`
- Steps: `67-67`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or repeated wait-for behavior dominated the episode and delayed or prevented substantive progress.
- Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 127

- Segment/env: `276` / `11`
- Lines: `12938691-12940977`
- Steps: `67-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 128

- Segment/env: `463` / `20`
- Lines: `12939916-12941262`
- Steps: `67-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 129

- Segment/env: `726` / `30`
- Lines: `12940105-12965867`
- Steps: `67-68`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`, `vote_switch`, `placeholder_output`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `13` / `1` / `12`
- Waits/wait_for: `0` / `2`
- Confidence: `medium`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Let's focus on Student 2"

### Complete Episode 130

- Segment/env: `682` / `28`
- Lines: `12940884-12947116`
- Steps: `68-68`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `candidate_comparison`, `counterproposal`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Let's focus on Student 4."

### Complete Episode 131

- Segment/env: `21` / `1`
- Lines: `12941170-12944023`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 132

- Segment/env: `522` / `22`
- Lines: `12941454-12948671`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 133

- Segment/env: `251` / `10`
- Lines: `12941684-12949997`
- Steps: `68-68`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Let's keep Student 3 as the top choice."

### Complete Episode 134

- Segment/env: `649` / `27`
- Lines: `12941776-12949075`
- Steps: `68-68`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 135

- Segment/env: `373` / `15`
- Lines: `12941964-12941964`
- Steps: `68-68`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `1` / `0`
- Confidence: `high`
- Rationale: Waiting or repeated wait-for behavior dominated the episode and delayed or prevented substantive progress.
- Excerpt: "<WAIT>"

### Complete Episode 136

- Segment/env: `219` / `9`
- Lines: `12942465-12948878`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 137

- Segment/env: `585` / `24`
- Lines: `12942753-12949900`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 138

- Segment/env: `464` / `20`
- Lines: `12943930-12946920`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 139

- Segment/env: `555` / `23`
- Lines: `12945021-12954284`
- Steps: `68-68`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `counterproposal`, `preference_probe`, `vote_switch`, `compromise_language`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `4` / `0` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 140

- Segment/env: `374` / `15`
- Lines: `12945347-13099931`
- Steps: `68-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `candidate_comparison`, `counterproposal`, `preference_probe`, `vote_switch`, `repeated_proposal`, `compromise_language`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `41` / `35` / `30`
- Waits/wait_for: `0` / `4`
- Confidence: `medium`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Let's support Student 2"

### Complete Episode 141

- Segment/env: `277` / `11`
- Lines: `12945677-12948576`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 142

- Segment/env: `607` / `25`
- Lines: `12946005-12952516`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 143

- Segment/env: `388` / `16`
- Lines: `12946097-12962096`
- Steps: `68-68`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `6` / `1` / `4`
- Waits/wait_for: `0` / `2`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Let's go with Student 4 for this round."

### Complete Episode 144

- Segment/env: `50` / `2`
- Lines: `12946189-12950187`
- Steps: `68-68`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Vote for Student 3"

### Complete Episode 145

- Segment/env: `497` / `21`
- Lines: `12946377-12952186`
- Steps: `68-68`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The public behavior centered on checking reactions, waiting, or generic coordination language rather than useful candidate tradeoffs.
- Excerpt: "Let's see how the others value Student 2."

### Complete Episode 146

- Segment/env: `22` / `1`
- Lines: `12947212-12950988`
- Steps: `68-68`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Vote for Student 2"

### Complete Episode 147

- Segment/env: `465` / `20`
- Lines: `12949617-12953357`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 148

- Segment/env: `707` / `29`
- Lines: `12950095-12953261`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 149

- Segment/env: `683` / `28`
- Lines: `12950378-12957137`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 150

- Segment/env: `523` / `22`
- Lines: `12950699-12958420`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 151

- Segment/env: `278` / `11`
- Lines: `12950895-12964027`
- Steps: `68-68`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `placeholder_output`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `7` / `1` / `6`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Student 2 is the best fit for my preferences."

### Complete Episode 152

- Segment/env: `650` / `27`
- Lines: `12951184-12954708`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 153

- Segment/env: `220` / `9`
- Lines: `12952283-12957649`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 154

- Segment/env: `586` / `24`
- Lines: `12952944-12955464`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 155

- Segment/env: `252` / `10`
- Lines: `12953453-12956741`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 156

- Segment/env: `51` / `2`
- Lines: `12953546-12956239`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 157

- Segment/env: `23` / `1`
- Lines: `12953940-12960348`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 158

- Segment/env: `498` / `21`
- Lines: `12954804-12962000`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 159

- Segment/env: `608` / `25`
- Lines: `12955135-12957745`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 160

- Segment/env: `708` / `29`
- Lines: `12956146-12960952`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 161

- Segment/env: `466` / `20`
- Lines: `12956438-12962619`
- Steps: `68-68`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`, `counterproposal`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Let's select Student 2 for their strong alignment with my research interests."

### Complete Episode 162

- Segment/env: `139` / `6`
- Lines: `12956532-12962848`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 163

- Segment/env: `651` / `27`
- Lines: `12956836-12974271`
- Steps: `68-69`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `6` / `1` / `5`
- Waits/wait_for: `0` / `3`
- Confidence: `medium`
- Rationale: The public behavior centered on checking reactions, waiting, or generic coordination language rather than useful candidate tradeoffs.
- Excerpt: "Making a strategic bet on Student 3"

### Complete Episode 164

- Segment/env: `556` / `23`
- Lines: `12957234-12966379`
- Steps: `68-68`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "I propose student 3"

### Complete Episode 165

- Segment/env: `587` / `24`
- Lines: `12958612-12961479`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 166

- Segment/env: `52` / `2`
- Lines: `12959704-12964927`
- Steps: `68-68`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 167

- Segment/env: `253` / `10`
- Lines: `12959899-12962944`
- Steps: `68-68`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "I recommend Student 2"

### Complete Episode 168

- Segment/env: `684` / `28`
- Lines: `12960444-12968647`
- Steps: `68-69`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `4` / `1` / `4`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "I propose student 3"

### Complete Episode 169

- Segment/env: `221` / `9`
- Lines: `12961048-12961048`
- Steps: `68-68`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or repeated wait-for behavior dominated the episode and delayed or prevented substantive progress.
- Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 170

- Segment/env: `609` / `25`
- Lines: `12961387-12969777`
- Steps: `68-69`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Candidate mentions or vote patterns stayed shallow and did not develop into clear tradeoff reasoning or compromise.
- Excerpt: "Student 3 is the top choice for me."

### Complete Episode 171

- Segment/env: `524` / `22`
- Lines: `12961698-12964551`
- Steps: `68-68`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "I'm suggesting we go with Student 3"

### Complete Episode 172

- Segment/env: `315` / `13`
- Lines: `12963040-12970060`
- Steps: `68-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `counterproposal`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 3 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 173

- Segment/env: `24` / `1`
- Lines: `12963132-12965977`
- Steps: `68-68`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: One candidate became focal through an early vote or short proposal, and another professor followed without meaningful bargaining.
- Excerpt: "Let's select Student 2."

### Complete Episode 174

- Segment/env: `709` / `29`
- Lines: `12963457-12966475`
- Steps: `68-68`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 175

- Segment/env: `222` / `9`
- Lines: `12963690-12976304`
- Steps: `68-69`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `counterproposal`, `preference_probe`, `repeated_proposal`, `placeholder_output`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `9` / `1` / `9`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: Professors cast split votes or shallow candidate claims without resolving the disagreement through bargaining or compromise.
- Excerpt: "Let's see what Professors prof_2 and prof_3 think."

### Complete Episode 176

- Segment/env: `588` / `24`
- Lines: `12964362-12970740`
- Steps: `68-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 177

- Segment/env: `389` / `16`
- Lines: `12964647-12968274`
- Steps: `68-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 178

- Segment/env: `619` / `26`
- Lines: `12964835-12972379`
- Steps: `68-69`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `counterproposal`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The public behavior centered on checking reactions, waiting, or generic coordination language rather than useful candidate tradeoffs.
- Excerpt: "Looking forward to hearing from my colleagues"

### Complete Episode 179

- Segment/env: `467` / `20`
- Lines: `12965024-12969064`
- Steps: `68-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed within 2 turns through votes alone, with no public candidate comparison.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 180

- Segment/env: `499` / `21`
- Lines: `12965445-12984287`
- Steps: `68-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`, `vote_switch`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `6` / `0` / `5`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 181

- Segment/env: `140` / `6`
- Lines: `12965664-12969589`
- Steps: `68-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 0 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 182

- Segment/env: `279` / `11`
- Lines: `12966072-12970836`
- Steps: `68-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `compromise_language`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "Vote for Student 2, aligning with their strong multi-disciplinary skills and high potential for collaborative research."

### Complete Episode 183

- Segment/env: `254` / `10`
- Lines: `12966572-12966572`
- Steps: `68-68`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `preference_probe`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominate the episode and block substantive progress. There is little or no concrete public negotiation.
- Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 184

- Segment/env: `298` / `12`
- Lines: `12967978-13018370`
- Steps: `69-70`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `16` / `1` / `13`
- Waits/wait_for: `0` / `3`
- Confidence: `medium`
- Rationale: The public/action behavior loops on waiting, alignment, or repeated voting rather than exchanging useful tradeoffs. Candidate reasoning is absent or too thin to count as negotiation.
- Excerpt: "Let's reconsider and ensure we maximize the overall utility."

### Complete Episode 185

- Segment/env: `255` / `10`
- Lines: `12968370-12973595`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 186

- Segment/env: `557` / `23`
- Lines: `12968463-12971079`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 0 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 187

- Segment/env: `710` / `29`
- Lines: `12968555-12972896`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "Let's give Student 2 a chance!"

### Complete Episode 188

- Segment/env: `164` / `7`
- Lines: `12968879-12972706`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 1 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 189

- Segment/env: `120` / `5`
- Lines: `12968971-12975614`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 190

- Segment/env: `727` / `30`
- Lines: `12969160-12974373`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "Let's see how Student 2 looks in comparison to the others."

### Complete Episode 191

- Segment/env: `53` / `2`
- Lines: `12969685-12976208`
- Steps: `69-69`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`, `private_reasoning_only`, `vote_only`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: The episode is driven by bare votes for candidates without public discussion, so there is no bargaining or substantive comparison.
- Excerpt: "<VOTE>4</VOTE><WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 192

- Segment/env: `525` / `22`
- Lines: `12969968-12972187`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 0 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 193

- Segment/env: `25` / `1`
- Lines: `12970282-12970282`
- Steps: `69-69`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `preference_probe`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominate the episode and block substantive progress. There is little or no concrete public negotiation.
- Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 194

- Segment/env: `685` / `28`
- Lines: `12971656-12973818`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 195

- Segment/env: `468` / `20`
- Lines: `12971871-12974957`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "Let's focus on Student 2"

### Complete Episode 196

- Segment/env: `610` / `25`
- Lines: `12972094-13133831`
- Steps: `69-75`
- Category: `coordination_theater`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `vote_only`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `50` / `0` / `48`
- Waits/wait_for: `0` / `2`
- Confidence: `medium`
- Rationale: The public/action behavior loops on waiting, alignment, or repeated voting rather than exchanging useful tradeoffs. Candidate reasoning is absent or too thin to count as negotiation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 197

- Segment/env: `390` / `16`
- Lines: `12972476-12974748`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `compromise_language`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "Student 4 is very strong across multiple fields, and my vote for them aligns with this strength."

### Complete Episode 198

- Segment/env: `589` / `24`
- Lines: `12972991-12979546`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 199

- Segment/env: `141` / `6`
- Lines: `12973179-12979449`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 1 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 200

- Segment/env: `558` / `23`
- Lines: `12973502-12980813`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 201

- Segment/env: `316` / `13`
- Lines: `12973914-12981136`
- Steps: `69-69`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: The episode contains brief candidate advocacy or conflicting candidate mentions, but the claims remain shallow and no effective compromise develops.
- Excerpt: "Great choice, I think Student 3 would be an excellent addition to our team."

### Complete Episode 202

- Segment/env: `280` / `11`
- Lines: `12974469-12978206`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 0 through votes, with no meaningful public deliberation.
- Excerpt: "I believe Student 0 is the strongest candidate based on my preferences and the data available."

### Complete Episode 203

- Segment/env: `526` / `22`
- Lines: `12974562-12977591`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 204

- Segment/env: `26` / `1`
- Lines: `12974655-12999478`
- Steps: `69-70`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `7` / `3` / `5`
- Waits/wait_for: `0` / `2`
- Confidence: `medium`
- Rationale: The public/action behavior loops on waiting, alignment, or repeated voting rather than exchanging useful tradeoffs. Candidate reasoning is absent or too thin to count as negotiation.
- Excerpt: "Let's hope prof_2 is considering alignment with my preferences."

### Complete Episode 205

- Segment/env: `620` / `26`
- Lines: `12975052-12978302`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 206

- Segment/env: `165` / `7`
- Lines: `12975384-12980331`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 207

- Segment/env: `711` / `29`
- Lines: `12975805-12982668`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 208

- Segment/env: `652` / `27`
- Lines: `12976115-12982572`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 209

- Segment/env: `256` / `10`
- Lines: `12976827-12983677`
- Steps: `69-69`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode contains brief candidate advocacy or conflicting candidate mentions, but the claims remain shallow and no effective compromise develops.
- Excerpt: "Let's target Student 2"

### Complete Episode 210

- Segment/env: `469` / `20`
- Lines: `12977140-12994239`
- Steps: `69-69`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`, `vote_switch`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `6` / `0` / `3`
- Waits/wait_for: `1` / `2`
- Confidence: `medium`
- Rationale: The public/action behavior loops on waiting, alignment, or repeated voting rather than exchanging useful tradeoffs. Candidate reasoning is absent or too thin to count as negotiation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 211

- Segment/env: `751` / `31`
- Lines: `12977233-12985230`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 212

- Segment/env: `728` / `30`
- Lines: `12977686-12991936`
- Steps: `69-69`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `5` / `1` / `4`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: One candidate becomes focal and a later professor follows with a matching vote for Student 2. Public rationale is brief and does not develop into bargaining.
- Excerpt: "Based on the current votes and the utilities, I lean towards Student 2 due to Prof_1's strong preference for them. However, I still need..."

### Complete Episode 213

- Segment/env: `391` / `16`
- Lines: `12978020-12984819`
- Steps: `69-69`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `private_reasoning_only`, `vote_only`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode is driven by bare votes for candidates without public discussion, so there is no bargaining or substantive comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 214

- Segment/env: `686` / `28`
- Lines: `12978113-12980909`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 215

- Segment/env: `54` / `2`
- Lines: `12978536-12983182`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 216

- Segment/env: `223` / `9`
- Lines: `12978959-12982765`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 217

- Segment/env: `121` / `5`
- Lines: `12979148-12985657`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 218

- Segment/env: `445` / `19`
- Lines: `12979240-12982861`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 219

- Segment/env: `527` / `22`
- Lines: `12981718-12984582`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 220

- Segment/env: `142` / `6`
- Lines: `12981810-12985327`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 221

- Segment/env: `621` / `26`
- Lines: `12981903-12987628`
- Steps: `69-69`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `private_reasoning_only`, `vote_only`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode is driven by bare votes for candidates without public discussion, so there is no bargaining or substantive comparison.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 222

- Segment/env: `281` / `11`
- Lines: `12982090-12988251`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "Strong advocate for Student 2"

### Complete Episode 223

- Segment/env: `590` / `24`
- Lines: `12982957-12989801`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `1` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 224

- Segment/env: `166` / `7`
- Lines: `12983277-12985945`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 225

- Segment/env: `559` / `23`
- Lines: `12983488-12986321`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 226

- Segment/env: `687` / `28`
- Lines: `12984003-12989328`
- Steps: `69-69`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `private_reasoning_only`, `vote_only`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode is driven by bare votes for candidates without public discussion, so there is no bargaining or substantive comparison.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 227

- Segment/env: `317` / `13`
- Lines: `12984195-12988775`
- Steps: `69-69`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `private_reasoning_only`, `vote_only`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode is driven by bare votes for candidates without public discussion, so there is no bargaining or substantive comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 228

- Segment/env: `446` / `19`
- Lines: `12984489-12987159`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 229

- Segment/env: `224` / `9`
- Lines: `12985011-12987724`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 230

- Segment/env: `712` / `29`
- Lines: `12985565-13009406`
- Steps: `69-70`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `6` / `2` / `5`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: One candidate becomes focal and a later professor follows with a matching vote for Student 4. Public rationale is brief and does not develop into bargaining.
- Excerpt: "Student 4 is a great fit for my team."

### Complete Episode 231

- Segment/env: `76` / `3`
- Lines: `12985755-12994140`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `2`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 232

- Segment/env: `55` / `2`
- Lines: `12986041-12988964`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 233

- Segment/env: `653` / `27`
- Lines: `12986229-12989705`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "Student 2 is the strongest candidate"

### Complete Episode 234

- Segment/env: `392` / `16`
- Lines: `12986848-12992636`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 235

- Segment/env: `752` / `31`
- Lines: `12987255-12991405`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 236

- Segment/env: `257` / `10`
- Lines: `12987348-12993292`
- Steps: `69-69`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode contains brief candidate advocacy or conflicting candidate mentions, but the claims remain shallow and no effective compromise develops.
- Excerpt: "I believe Student 4 is the best choice given their high utility and balanced skill set across all topics."

### Complete Episode 237

- Segment/env: `500` / `21`
- Lines: `12987442-12991021`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 238

- Segment/env: `528` / `22`
- Lines: `12987534-12990707`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "Let's start with Student 4. They have the highest utility and a strong compbio and ai/ML component."

### Complete Episode 239

- Segment/env: `344` / `14`
- Lines: `12987819-12989896`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 240

- Segment/env: `122` / `5`
- Lines: `12988007-12993065`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 241

- Segment/env: `143` / `6`
- Lines: `12988580-12995101`
- Steps: `69-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 242

- Segment/env: `447` / `19`
- Lines: `12988871-12995723`
- Steps: `69-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "Vote for Student 2"

### Complete Episode 243

- Segment/env: `560` / `23`
- Lines: `12989425-12997400`
- Steps: `69-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 244

- Segment/env: `167` / `7`
- Lines: `12989517-12993777`
- Steps: `69-69`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 245

- Segment/env: `622` / `26`
- Lines: `12990319-12996229`
- Steps: `69-70`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `private_reasoning_only`, `vote_only`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode is driven by bare votes for candidates without public discussion, so there is no bargaining or substantive comparison.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 246

- Segment/env: `225` / `9`
- Lines: `12990927-12996003`
- Steps: `69-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "Let's start with Student 2, as their ability vector seems well-rounded and their utility score is high."

### Complete Episode 247

- Segment/env: `282` / `11`
- Lines: `12991211-12991211`
- Steps: `69-69`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `preference_probe`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominate the episode and block substantive progress. There is little or no concrete public negotiation.
- Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 248

- Segment/env: `56` / `2`
- Lines: `12991597-12994729`
- Steps: `69-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 249

- Segment/env: `654` / `27`
- Lines: `12992038-13009508`
- Steps: `69-70`
- Category: `stalled_waiting_loop`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `6` / `0` / `4`
- Waits/wait_for: `0` / `4`
- Confidence: `medium`
- Rationale: Waiting or wait-for actions dominate the episode and block substantive progress. There is little or no concrete public negotiation.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 250

- Segment/env: `688` / `28`
- Lines: `12992359-12998103`
- Steps: `69-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 251

- Segment/env: `318` / `13`
- Lines: `12992451-12997208`
- Steps: `69-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 252

- Segment/env: `591` / `24`
- Lines: `12992544-12999585`
- Steps: `69-70`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode contains brief candidate advocacy or conflicting candidate mentions, but the claims remain shallow and no effective compromise develops.
- Excerpt: "Vote for Student 3"

### Complete Episode 253

- Segment/env: `345` / `14`
- Lines: `12992732-12994435`
- Steps: `69-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 1 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 254

- Segment/env: `529` / `22`
- Lines: `12993484-12997304`
- Steps: `69-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 255

- Segment/env: `729` / `30`
- Lines: `12994637-12998974`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "Let's select Student 4; they're our best bet for this batch!"

### Complete Episode 256

- Segment/env: `501` / `21`
- Lines: `12994825-12998387`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 1 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 257

- Segment/env: `283` / `11`
- Lines: `12994917-12998292`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 258

- Segment/env: `168` / `7`
- Lines: `12995009-13000581`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 1 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 259

- Segment/env: `393` / `16`
- Lines: `12995197-12998483`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 260

- Segment/env: `123` / `5`
- Lines: `12995819-12999681`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 261

- Segment/env: `753` / `31`
- Lines: `12995911-12998578`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 262

- Segment/env: `77` / `3`
- Lines: `12996430-13000192`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 263

- Segment/env: `470` / `20`
- Lines: `12996522-13003342`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE><WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 264

- Segment/env: `191` / `8`
- Lines: `12996614-13000005`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 265

- Segment/env: `258` / `10`
- Lines: `12997113-13057652`
- Steps: `70-72`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `17` / `13` / `12`
- Waits/wait_for: `0` / `7`
- Confidence: `high`
- Rationale: The episode contains brief candidate advocacy or conflicting candidate mentions, but the claims remain shallow and no effective compromise develops.
- Excerpt: "Let's see how they respond."

### Complete Episode 266

- Segment/env: `346` / `14`
- Lines: `12997689-13004564`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 267

- Segment/env: `144` / `6`
- Lines: `12997781-13037530`
- Steps: `70-71`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `12` / `0` / `9`
- Waits/wait_for: `0` / `3`
- Confidence: `medium`
- Rationale: One candidate becomes focal and a later professor follows with a matching vote for Student 4. Public rationale is brief and does not develop into bargaining.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 268

- Segment/env: `57` / `2`
- Lines: `12998010-13004366`
- Steps: `70-70`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode contains brief candidate advocacy or conflicting candidate mentions, but the claims remain shallow and no effective compromise develops.
- Excerpt: "Vote for Student 3"

### Complete Episode 269

- Segment/env: `623` / `26`
- Lines: `12998200-13001869`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 270

- Segment/env: `425` / `18`
- Lines: `12998782-13002288`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 1 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 271

- Segment/env: `448` / `19`
- Lines: `12999070-13002871`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 272

- Segment/env: `319` / `13`
- Lines: `12999162-13001398`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 1 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 273

- Segment/env: `226` / `9`
- Lines: `12999255-13006305`
- Steps: `70-70`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The public/action behavior loops on waiting, alignment, or repeated voting rather than exchanging useful tradeoffs. Candidate reasoning is absent or too thin to count as negotiation.
- Excerpt: "Let's see what the others think"

### Complete Episode 274

- Segment/env: `530` / `22`
- Lines: `13000100-13005597`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 275

- Segment/env: `561` / `23`
- Lines: `13000489-13003800`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 276

- Segment/env: `502` / `21`
- Lines: `13001009-13004176`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 277

- Segment/env: `394` / `16`
- Lines: `13001102-13007432`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 278

- Segment/env: `689` / `28`
- Lines: `13001195-13005008`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`, `format_error_light`, `malformed_tags`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<Vote>2</Vote>"

### Complete Episode 279

- Segment/env: `754` / `31`
- Lines: `13001588-13008234`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 280

- Segment/env: `284` / `11`
- Lines: `13001777-13007723`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 281

- Segment/env: `78` / `3`
- Lines: `13002102-13006690`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 282

- Segment/env: `592` / `24`
- Lines: `13002195-13007104`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 283

- Segment/env: `124` / `5`
- Lines: `13002591-13008705`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 284

- Segment/env: `192` / `8`
- Lines: `13002779-13005789`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 285

- Segment/env: `27` / `1`
- Lines: `13002967-13006073`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 286

- Segment/env: `169` / `7`
- Lines: `13003060-13006401`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 287

- Segment/env: `730` / `30`
- Lines: `13003153-13005693`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "Let's vote for Student 2, who has the highest utility score."

### Complete Episode 288

- Segment/env: `320` / `13`
- Lines: `13003992-13010123`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 289

- Segment/env: `624` / `26`
- Lines: `13004084-13007336`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 290

- Segment/env: `449` / `19`
- Lines: `13005412-13012889`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "Let's secure Student 2"

### Complete Episode 291

- Segment/env: `426` / `18`
- Lines: `13005504-13008330`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 292

- Segment/env: `471` / `20`
- Lines: `13005885-13007932`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 293

- Segment/env: `562` / `23`
- Lines: `13006597-13009219`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 294

- Segment/env: `58` / `2`
- Lines: `13006919-13009610`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 295

- Segment/env: `503` / `21`
- Lines: `13007012-13009706`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 1 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 296

- Segment/env: `347` / `14`
- Lines: `13008142-13011749`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 297

- Segment/env: `690` / `28`
- Lines: `13008425-13014317`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "Let's focus on the best candidate for our needs."

### Complete Episode 298

- Segment/env: `170` / `7`
- Lines: `13008612-13016067`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "Student 2 seems to be the best fit for our interests. What do you think, prof_1?"

### Complete Episode 299

- Segment/env: `193` / `8`
- Lines: `13008943-13011944`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 300

- Segment/env: `227` / `9`
- Lines: `13009035-13017896`
- Steps: `70-70`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode contains brief candidate advocacy or conflicting candidate mentions, but the claims remain shallow and no effective compromise develops.
- Excerpt: "Let's see how others feel about Student 2 as well."

### Complete Episode 301

- Segment/env: `531` / `22`
- Lines: `13009127-13012793`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 302

- Segment/env: `79` / `3`
- Lines: `13009314-13012227`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 303

- Segment/env: `731` / `30`
- Lines: `13009802-13014220`
- Steps: `70-70`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: The public/action behavior loops on waiting, alignment, or repeated voting rather than exchanging useful tradeoffs. Candidate reasoning is absent or too thin to count as negotiation.
- Excerpt: "Let's see what others think"

### Complete Episode 304

- Segment/env: `28` / `1`
- Lines: `13010031-13013984`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `2` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "Let's see how well Student 2 matches the other professors' preferences as well."

### Complete Episode 305

- Segment/env: `593` / `24`
- Lines: `13010219-13016164`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 306

- Segment/env: `395` / `16`
- Lines: `13010311-13017470`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "Let's hope Student 3 is intrigued by the research opportunities!"

### Complete Episode 307

- Segment/env: `625` / `26`
- Lines: `13010643-13018084`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 308

- Segment/env: `472` / `20`
- Lines: `13010985-13013548`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "Let's make Student 2 our choice."

### Complete Episode 309

- Segment/env: `427` / `18`
- Lines: `13011189-13014413`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 310

- Segment/env: `563` / `23`
- Lines: `13011281-13019053`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "Let's see how Student 4 matches their interests as well."

### Complete Episode 311

- Segment/env: `125` / `5`
- Lines: `13011374-13014794`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 312

- Segment/env: `59` / `2`
- Lines: `13011563-13017566`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 1 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 313

- Segment/env: `655` / `27`
- Lines: `13011656-13015592`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 314

- Segment/env: `285` / `11`
- Lines: `13012040-13016767`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 315

- Segment/env: `755` / `31`
- Lines: `13012133-13014603`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "Student 2 is the most matched with my preferences."

### Complete Episode 316

- Segment/env: `713` / `29`
- Lines: `13012418-13068369`
- Steps: `70-72`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `15` / `4` / `11`
- Waits/wait_for: `0` / `6`
- Confidence: `medium`
- Rationale: The public/action behavior loops on waiting, alignment, or repeated voting rather than exchanging useful tradeoffs. Candidate reasoning is absent or too thin to count as negotiation.
- Excerpt: "Let's go for student 4"

### Complete Episode 317

- Segment/env: `321` / `13`
- Lines: `13012605-13018587`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 318

- Segment/env: `504` / `21`
- Lines: `13013081-13015215`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 319

- Segment/env: `532` / `22`
- Lines: `13015406-13017663`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 320

- Segment/env: `450` / `19`
- Lines: `13015499-13020973`
- Steps: `70-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `4` / `0` / `4`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 321

- Segment/env: `194` / `8`
- Lines: `13015687-13018181`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 322

- Segment/env: `348` / `14`
- Lines: `13015975-13021448`
- Steps: `70-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 323

- Segment/env: `473` / `20`
- Lines: `13016261-13019837`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "DO SUM IT UP, STUDENT 3 HAS THE TOP UTILITY AND COMPETITIVE ABILITIES."

### Complete Episode 324

- Segment/env: `691` / `28`
- Lines: `13016354-13019457`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 325

- Segment/env: `80` / `3`
- Lines: `13016567-13019650`
- Steps: `70-70`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "I strongly prefer Student 3. Let's move forward with this recommendation."

### Complete Episode 326

- Segment/env: `428` / `18`
- Lines: `13016959-13025218`
- Steps: `70-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 327

- Segment/env: `732` / `30`
- Lines: `13017052-13027651`
- Steps: `70-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 328

- Segment/env: `29` / `1`
- Lines: `13017145-13021165`
- Steps: `70-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 1 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 329

- Segment/env: `126` / `5`
- Lines: `13017378-13022427`
- Steps: `70-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 330

- Segment/env: `756` / `31`
- Lines: `13017992-13021261`
- Steps: `70-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 331

- Segment/env: `505` / `21`
- Lines: `13018277-13025970`
- Steps: `70-71`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: The public/action behavior loops on waiting, alignment, or repeated voting rather than exchanging useful tradeoffs. Candidate reasoning is absent or too thin to count as negotiation.
- Excerpt: "Let's see what prof_1 and prof_3 think about this choice."

### Complete Episode 332

- Segment/env: `656` / `27`
- Lines: `13019150-13020785`
- Steps: `70-71`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `social_optimum_unknown`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The public/action behavior loops on waiting, alignment, or repeated voting rather than exchanging useful tradeoffs. Candidate reasoning is absent or too thin to count as negotiation.
- Excerpt: "Let's hear from prof_2 and prof_3 if they have any preferences or concerns."

### Complete Episode 333

- Segment/env: `171` / `7`
- Lines: `13019364-13020598`
- Steps: `70-71`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `social_optimum_unknown`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The public/action behavior loops on waiting, alignment, or repeated voting rather than exchanging useful tradeoffs. Candidate reasoning is absent or too thin to count as negotiation.
- Excerpt: "Let's consider if anyone else has different preferences."

### Complete Episode 334

- Segment/env: `594` / `24`
- Lines: `13019745-13026574`
- Steps: `70-71`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode contains brief candidate advocacy or conflicting candidate mentions, but the claims remain shallow and no effective compromise develops.
- Excerpt: "I believe Student 3 is the strongest candidate based on my preference vector."

### Complete Episode 335

- Segment/env: `322` / `13`
- Lines: `13020137-13023043`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 336

- Segment/env: `564` / `23`
- Lines: `13020230-13030055`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 337

- Segment/env: `60` / `2`
- Lines: `13020322-13023524`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 4 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 338

- Segment/env: `396` / `16`
- Lines: `13020414-13024422`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 339

- Segment/env: `474` / `20`
- Lines: `13020506-13023429`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 340

- Segment/env: `692` / `28`
- Lines: `13020693-13048565`
- Steps: `71-72`
- Category: `coordination_theater`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`, `repeated_proposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `8` / `2` / `5`
- Waits/wait_for: `0` / `4`
- Confidence: `medium`
- Rationale: The public/action behavior loops on waiting, alignment, or repeated voting rather than exchanging useful tradeoffs. Candidate reasoning is absent or too thin to count as negotiation.
- Excerpt: "Let's go with Student 1."

### Complete Episode 341

- Segment/env: `228` / `9`
- Lines: `13020881-13023952`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 342

- Segment/env: `626` / `26`
- Lines: `13021073-13027164`
- Steps: `71-71`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `private_reasoning_only`, `vote_only`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode is driven by bare votes for candidates without public discussion, so there is no bargaining or substantive comparison.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 343

- Segment/env: `81` / `3`
- Lines: `13021356-13024747`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 344

- Segment/env: `195` / `8`
- Lines: `13021681-13021681`
- Steps: `71-71`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `1` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominate the episode and block substantive progress. There is little or no concrete public negotiation.
- Excerpt: "Let's focus on Student 2 and Student 3"

### Complete Episode 345

- Segment/env: `299` / `12`
- Lines: `13021873-13028593`
- Steps: `71-71`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode contains brief candidate advocacy or conflicting candidate mentions, but the claims remain shallow and no effective compromise develops.
- Excerpt: "Let's consider student 2"

### Complete Episode 346

- Segment/env: `533` / `22`
- Lines: `13022202-13025639`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "Vote for Student 2"

### Complete Episode 347

- Segment/env: `286` / `11`
- Lines: `13022523-13027839`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 348

- Segment/env: `172` / `7`
- Lines: `13023243-13028404`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 349

- Segment/env: `30` / `1`
- Lines: `13023336-13029067`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 350

- Segment/env: `196` / `8`
- Lines: `13023714-13034913`
- Steps: `71-71`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `compromise_language`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `4` / `1` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: One candidate becomes focal and a later professor follows with a matching vote for Student 2. Public rationale is brief and does not develop into bargaining.
- Excerpt: "Let's stick with Student 2"

### Complete Episode 351

- Segment/env: `657` / `27`
- Lines: `13024048-13029960`
- Steps: `71-71`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: The public/action behavior loops on waiting, alignment, or repeated voting rather than exchanging useful tradeoffs. Candidate reasoning is absent or too thin to count as negotiation.
- Excerpt: "Let's see what others think."

### Complete Episode 352

- Segment/env: `757` / `31`
- Lines: `13024140-13029357`
- Steps: `71-71`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `private_reasoning_only`, `vote_only`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode is driven by bare votes for candidates without public discussion, so there is no bargaining or substantive comparison.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 353

- Segment/env: `451` / `19`
- Lines: `13024233-13027556`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 354

- Segment/env: `323` / `13`
- Lines: `13024654-13027365`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 355

- Segment/env: `127` / `5`
- Lines: `13024938-13028875`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 2 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 356

- Segment/env: `349` / `14`
- Lines: `13025031-13028027`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "I highly value Student 3"

### Complete Episode 357

- Segment/env: `229` / `9`
- Lines: `13025736-13032729`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `private_reasoning_only`, `early_focal_candidate`, `vote_only`, `no_public_messages`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Consensus formed quickly around Student 3 through votes, with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 358

- Segment/env: `475` / `20`
- Lines: `13026289-13033145`
- Steps: `71-71`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode contains brief candidate advocacy or conflicting candidate mentions, but the claims remain shallow and no effective compromise develops.
- Excerpt: "Let's focus on Student 4 as they have the highest utility and align well with my preferences."

### Complete Episode 359

- Segment/env: `61` / `2`
- Lines: `13026670-13032825`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 360

- Segment/env: `82` / `3`
- Lines: `13026875-13032442`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 361

- Segment/env: `429` / `18`
- Lines: `13027747-13033625`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 362

- Segment/env: `397` / `16`
- Lines: `13027935-13030541`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 363

- Segment/env: `595` / `24`
- Lines: `13028500-13031923`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 0 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 364

- Segment/env: `534` / `22`
- Lines: `13028690-13031642`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 365

- Segment/env: `627` / `26`
- Lines: `13028782-13030961`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 366

- Segment/env: `506` / `21`
- Lines: `13029587-13037871`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 367

- Segment/env: `452` / `19`
- Lines: `13029775-13058446`
- Steps: `71-72`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `repeated_proposal`, `preference_probe`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `9` / `2` / `7`
- Waits/wait_for: `0` / `2`
- Confidence: `medium`
- Rationale: Public talk centered on checking support, seeing where others stood, or generic coordination rather than substantive candidate tradeoffs.
- Excerpt: "Let's show the support to the other professors"

### Complete Episode 368

- Segment/env: `324` / `13`
- Lines: `13029868-13029868`
- Steps: `71-71`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominated or halted progress, with little substantive public negotiation.
- Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 369

- Segment/env: `287` / `11`
- Lines: `13030449-13032634`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 370

- Segment/env: `350` / `14`
- Lines: `13030637-13033529`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 371

- Segment/env: `733` / `30`
- Lines: `13031173-13036773`
- Steps: `71-71`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Let's get this one selected."

### Complete Episode 372

- Segment/env: `173` / `7`
- Lines: `13031738-13036581`
- Steps: `71-71`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode includes shallow candidate claims or competing proposals, but no developed comparison, concession, or response to concerns.
- Excerpt: "Let's get Student 3."

### Complete Episode 373

- Segment/env: `300` / `12`
- Lines: `13031830-13034818`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 374

- Segment/env: `128` / `5`
- Lines: `13032164-13034631`
- Steps: `71-71`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Public talk centered on checking support, seeing where others stood, or generic coordination rather than substantive candidate tradeoffs.
- Excerpt: "Let's see what others think."

### Complete Episode 375

- Segment/env: `658` / `27`
- Lines: `13032256-13037968`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 376

- Segment/env: `31` / `1`
- Lines: `13032349-13040875`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 377

- Segment/env: `565` / `23`
- Lines: `13032920-13039157`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 378

- Segment/env: `325` / `13`
- Lines: `13033242-13037435`
- Steps: `71-71`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Let's aim for Student 4's selection."

### Complete Episode 379

- Segment/env: `398` / `16`
- Lines: `13033721-13036393`
- Steps: `71-71`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "I highly recommend Student 3. He has the highest utility and is well-rounded."

### Complete Episode 380

- Segment/env: `628` / `26`
- Lines: `13034016-13038963`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 381

- Segment/env: `758` / `31`
- Lines: `13034108-13036678`
- Steps: `71-71`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Public talk centered on checking support, seeing where others stood, or generic coordination rather than substantive candidate tradeoffs.
- Excerpt: "Let's see how Student 2 fits with my priorities"

### Complete Episode 382

- Segment/env: `535` / `22`
- Lines: `13034539-13039985`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 383

- Segment/env: `596` / `24`
- Lines: `13034726-13036870`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 384

- Segment/env: `83` / `3`
- Lines: `13035240-13038480`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 1 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 385

- Segment/env: `476` / `20`
- Lines: `13035333-13043269`
- Steps: `71-71`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `compromise_language`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `low`
- Rationale: Public talk centered on checking support, seeing where others stood, or generic coordination rather than substantive candidate tradeoffs.
- Excerpt: "I don't have a strong preference yet, but I like Student 4 and could make a partial offer if they're open to negotiation. This rounding out "

### Complete Episode 386

- Segment/env: `288` / `11`
- Lines: `13035876-13042109`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors immediately cast conflicting votes with no public messages, bargaining, or adaptation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 387

- Segment/env: `351` / `14`
- Lines: `13036063-13040972`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors immediately cast conflicting votes with no public messages, bargaining, or adaptation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 388

- Segment/env: `230` / `9`
- Lines: `13036156-13042301`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 389

- Segment/env: `430` / `18`
- Lines: `13036488-13043462`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 390

- Segment/env: `197` / `8`
- Lines: `13036965-13043172`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `malformed_tags`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 0 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<THINK>First, I'll review the utility scores to understand how my preferences align with the other professors' likely votes. Student 0 stand"

### Complete Episode 391

- Segment/env: `99` / `4`
- Lines: `13037058-13040454`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 392

- Segment/env: `129` / `5`
- Lines: `13037150-13042779`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors immediately cast conflicting votes with no public messages, bargaining, or adaptation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 393

- Segment/env: `62` / `2`
- Lines: `13037242-13043696`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 394

- Segment/env: `301` / `12`
- Lines: `13038256-13044856`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 395

- Segment/env: `734` / `30`
- Lines: `13038778-13043366`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 0 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 396

- Segment/env: `174` / `7`
- Lines: `13038870-13044760`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 397

- Segment/env: `759` / `31`
- Lines: `13039350-13041309`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 398

- Segment/env: `597` / `24`
- Lines: `13039678-13047405`
- Steps: `71-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `4` / `0` / `4`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 399

- Segment/env: `659` / `27`
- Lines: `13040082-13047887`
- Steps: `71-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 400

- Segment/env: `399` / `16`
- Lines: `13040175-13045856`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors immediately cast conflicting votes with no public messages, bargaining, or adaptation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 401

- Segment/env: `326` / `13`
- Lines: `13040267-13046463`
- Steps: `71-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "I propose student 4"

### Complete Episode 402

- Segment/env: `145` / `6`
- Lines: `13040687-13044241`
- Steps: `71-71`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 403

- Segment/env: `507` / `21`
- Lines: `13041405-13041405`
- Steps: `71-71`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `1` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominated or halted progress, with little substantive public negotiation.
- Excerpt: "I am interested in Student 4"

### Complete Episode 404

- Segment/env: `566` / `23`
- Lines: `13041727-13049457`
- Steps: `71-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `preference_probe`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Great students, despite their different strengths, align well with my research interests. I believe Student 4 is the top choice for this bat"

### Complete Episode 405

- Segment/env: `84` / `3`
- Lines: `13042017-13048671`
- Steps: `71-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Vote for Student 4!"

### Complete Episode 406

- Segment/env: `536` / `22`
- Lines: `13042397-13045567`
- Steps: `71-71`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "I strongly believe Student 2 is the best fit for our goals. Let's vote for them."

### Complete Episode 407

- Segment/env: `100` / `4`
- Lines: `13042489-13048468`
- Steps: `71-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 408

- Segment/env: `32` / `1`
- Lines: `13043080-13052362`
- Steps: `71-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Let's go with Student 2, as their high utility aligns well with my preferences and can help us move forward."

### Complete Episode 409

- Segment/env: `760` / `31`
- Lines: `13043933-13056128`
- Steps: `71-72`
- Category: `stalled_waiting_loop`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `5` / `0` / `3`
- Waits/wait_for: `0` / `3`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominated or halted progress, with little substantive public negotiation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 410

- Segment/env: `629` / `26`
- Lines: `13044025-13048768`
- Steps: `71-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `preference_probe`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Based on the scores, Student 2 stands out with a utility of 3.2 and strong AI/ML and CompBio abilities (ability vector: [0.6, 0.1, 0.1, 0.1,"

### Complete Episode 411

- Segment/env: `352` / `14`
- Lines: `13044336-13050405`
- Steps: `71-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 412

- Segment/env: `508` / `21`
- Lines: `13044523-13046652`
- Steps: `71-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 413

- Segment/env: `289` / `11`
- Lines: `13045288-13047217`
- Steps: `71-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 414

- Segment/env: `231` / `9`
- Lines: `13045475-13049223`
- Steps: `71-72`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: The episode includes shallow candidate claims or competing proposals, but no developed comparison, concession, or response to concerns.
- Excerpt: "Let's proceed with Student 3"

### Complete Episode 415

- Segment/env: `175` / `7`
- Lines: `13046185-13049650`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 416

- Segment/env: `431` / `18`
- Lines: `13046278-13054342`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 417

- Segment/env: `130` / `5`
- Lines: `13046370-13050923`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 418

- Segment/env: `146` / `6`
- Lines: `13046560-13055843`
- Steps: `72-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Strongest candidate is Student 0, very strong in AI/ML and CompBio."

### Complete Episode 419

- Segment/env: `400` / `16`
- Lines: `13046843-13054246`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 420

- Segment/env: `735` / `30`
- Lines: `13046935-13054055`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 421

- Segment/env: `198` / `8`
- Lines: `13047027-13049554`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `1` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE> <WAIT>"

### Complete Episode 422

- Segment/env: `302` / `12`
- Lines: `13047312-13049933`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 1 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 423

- Segment/env: `537` / `22`
- Lines: `13047505-13052597`
- Steps: `72-72`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Public talk centered on checking support, seeing where others stood, or generic coordination rather than substantive candidate tradeoffs.
- Excerpt: "Let's see where we stand!"

### Complete Episode 424

- Segment/env: `477` / `20`
- Lines: `13047795-13054534`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 425

- Segment/env: `63` / `2`
- Lines: `13048376-13048376`
- Steps: `72-72`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominated or halted progress, with little substantive public negotiation.
- Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 426

- Segment/env: `327` / `13`
- Lines: `13049746-13057555`
- Steps: `72-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Let's focus on Student 3; she has strong potential in key areas for our joint research projects."

### Complete Episode 427

- Segment/env: `290` / `11`
- Lines: `13050124-13050124`
- Steps: `72-72`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominated or halted progress, with little substantive public negotiation.
- Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 428

- Segment/env: `509` / `21`
- Lines: `13050216-13056419`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 429

- Segment/env: `660` / `27`
- Lines: `13050598-13053392`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 430

- Segment/env: `101` / `4`
- Lines: `13050691-13056984`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 431

- Segment/env: `693` / `28`
- Lines: `13051020-13093666`
- Steps: `72-73`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `repeated_proposal`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `13` / `3` / `10`
- Waits/wait_for: `0` / `5`
- Confidence: `medium`
- Rationale: Public talk centered on checking support, seeing where others stood, or generic coordination rather than substantive candidate tradeoffs.
- Excerpt: "Let's check if prof_3 has made a decision yet. If not, I will encourage them to make one."

### Complete Episode 432

- Segment/env: `2` / `0`
- Lines: `13051522-13063401`
- Steps: `72-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `5` / `1` / `4`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Let's give Student 2 a chance."

### Complete Episode 433

- Segment/env: `176` / `7`
- Lines: `13051711-13054439`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 434

- Segment/env: `64` / `2`
- Lines: `13051804-13055066`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 435

- Segment/env: `630` / `26`
- Lines: `13051992-13058553`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 436

- Segment/env: `85` / `3`
- Lines: `13052085-13058835`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 437

- Segment/env: `199` / `8`
- Lines: `13052177-13057970`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 438

- Segment/env: `232` / `9`
- Lines: `13052790-13055748`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 439

- Segment/env: `567` / `23`
- Lines: `13052883-13060221`
- Steps: `72-72`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode includes shallow candidate claims or competing proposals, but no developed comparison, concession, or response to concerns.
- Excerpt: "Vote for Student 2"

### Complete Episode 440

- Segment/env: `303` / `12`
- Lines: `13053202-13057173`
- Steps: `72-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`, `malformed_tags`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Student 3 is the best fit for my research interests."

### Complete Episode 441

- Segment/env: `353` / `14`
- Lines: `13053632-13061082`
- Steps: `72-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Let's consider Student 2"

### Complete Episode 442

- Segment/env: `131` / `5`
- Lines: `13053963-13059448`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 443

- Segment/env: `538` / `22`
- Lines: `13055353-13061564`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors immediately cast conflicting votes with no public messages, bargaining, or adaptation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 444

- Segment/env: `33` / `1`
- Lines: `13055559-13057782`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 445

- Segment/env: `401` / `16`
- Lines: `13056035-13060319`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 446

- Segment/env: `736` / `30`
- Lines: `13056515-13062227`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors immediately cast conflicting votes with no public messages, bargaining, or adaptation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 447

- Segment/env: `661` / `27`
- Lines: `13056608-13063303`
- Steps: `72-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `preference_probe`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Dear colleagues, based on my analysis, Student 2 seems the most promising and well-aligned with my research interests. I hope this is a dire"

### Complete Episode 448

- Segment/env: `478` / `20`
- Lines: `13056892-13056892`
- Steps: `72-72`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominated or halted progress, with little substantive public negotiation.
- Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 449

- Segment/env: `177` / `7`
- Lines: `13057080-13061940`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 450

- Segment/env: `432` / `18`
- Lines: `13057366-13064440`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 451

- Segment/env: `65` / `2`
- Lines: `13057878-13065389`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 452

- Segment/env: `233` / `9`
- Lines: `13058067-13063972`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 453

- Segment/env: `761` / `31`
- Lines: `13058650-13060891`
- Steps: `72-72`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Public talk centered on checking support, seeing where others stood, or generic coordination rather than substantive candidate tradeoffs.
- Excerpt: "Let's see if Student 2 is well-liked."

### Complete Episode 454

- Segment/env: `147` / `6`
- Lines: `13058742-13060701`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 455

- Segment/env: `102` / `4`
- Lines: `13059068-13062131`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 456

- Segment/env: `510` / `21`
- Lines: `13059356-13063111`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 457

- Segment/env: `479` / `20`
- Lines: `13059753-13062324`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 458

- Segment/env: `34` / `1`
- Lines: `13059845-13065766`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 459

- Segment/env: `328` / `13`
- Lines: `13060036-13063876`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 460

- Segment/env: `453` / `19`
- Lines: `13060128-13063595`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 461

- Segment/env: `259` / `10`
- Lines: `13060515-13062800`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 462

- Segment/env: `631` / `26`
- Lines: `13060608-13066194`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 463

- Segment/env: `200` / `8`
- Lines: `13061661-13064916`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 464

- Segment/env: `304` / `12`
- Lines: `13061754-13063207`
- Steps: `72-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Looking at Student 3, do you share the same preference?"

### Complete Episode 465

- Segment/env: `86` / `3`
- Lines: `13061847-13068963`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors immediately cast conflicting votes with no public messages, bargaining, or adaptation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 466

- Segment/env: `132` / `5`
- Lines: `13062419-13068581`
- Steps: `72-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Let's start by assessing Student 3. They have the highest overall ability vector, which could be a strong candidate for me."

### Complete Episode 467

- Segment/env: `568` / `23`
- Lines: `13062708-13070398`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 468

- Segment/env: `402` / `16`
- Lines: `13063503-13066664`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 469

- Segment/env: `539` / `22`
- Lines: `13063691-13066568`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 470

- Segment/env: `762` / `31`
- Lines: `13063784-13091847`
- Steps: `72-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `repeated_proposal`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `9` / `3` / `7`
- Waits/wait_for: `0` / `3`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "Strong advocate of Student 4"

### Complete Episode 471

- Segment/env: `148` / `6`
- Lines: `13064347-13067275`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 472

- Segment/env: `178` / `7`
- Lines: `13064731-13070590`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 473

- Segment/env: `354` / `14`
- Lines: `13064823-13073199`
- Steps: `72-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `4` / `1` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Let's go with Student 3"

### Complete Episode 474

- Segment/env: `103` / `4`
- Lines: `13065011-13070494`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 475

- Segment/env: `260` / `10`
- Lines: `13065103-13065103`
- Steps: `72-72`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `1` / `0`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominated or halted progress, with little substantive public negotiation.
- Excerpt: "<WAIT>"

### Complete Episode 476

- Segment/env: `737` / `30`
- Lines: `13065196-13069155`
- Steps: `72-72`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: Public talk centered on checking support, seeing where others stood, or generic coordination rather than substantive candidate tradeoffs.
- Excerpt: "Let's see where Prof_1 and Prof_3 stand before deciding further."

### Complete Episode 477

- Segment/env: `454` / `19`
- Lines: `13065485-13069060`
- Steps: `72-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Vote for Student 2"

### Complete Episode 478

- Segment/env: `329` / `13`
- Lines: `13065673-13068678`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 479

- Segment/env: `511` / `21`
- Lines: `13066008-13069352`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 480

- Segment/env: `234` / `9`
- Lines: `13066101-13071501`
- Steps: `72-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "I propose student 3"

### Complete Episode 481

- Segment/env: `480` / `20`
- Lines: `13066290-13068083`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 482

- Segment/env: `662` / `27`
- Lines: `13066382-13068867`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 483

- Segment/env: `3` / `0`
- Lines: `13066475-13070207`
- Steps: `72-72`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Let's move forward with Student 2"

### Complete Episode 484

- Segment/env: `433` / `18`
- Lines: `13066760-13073102`
- Steps: `72-73`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Public talk centered on checking support, seeing where others stood, or generic coordination rather than substantive candidate tradeoffs.
- Excerpt: "Let's analyze further."

### Complete Episode 485

- Segment/env: `305` / `12`
- Lines: `13066950-13074504`
- Steps: `72-73`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `preference_probe`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode includes shallow candidate claims or competing proposals, but no developed comparison, concession, or response to concerns.
- Excerpt: "I believe Student 1 is well-suited and would like to propose this selection. What are your thoughts?"

### Complete Episode 486

- Segment/env: `66` / `2`
- Lines: `13067371-13071406`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 487

- Segment/env: `201` / `8`
- Lines: `13067464-13070883`
- Steps: `72-72`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 488

- Segment/env: `261` / `10`
- Lines: `13067652-13074601`
- Steps: `72-73`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors immediately cast conflicting votes with no public messages, bargaining, or adaptation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 489

- Segment/env: `632` / `26`
- Lines: `13068488-13076416`
- Steps: `72-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Vote for Student 2 to maintain the selection trend"

### Complete Episode 490

- Segment/env: `35` / `1`
- Lines: `13068774-13076514`
- Steps: `72-73`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Public talk centered on checking support, seeing where others stood, or generic coordination rather than substantive candidate tradeoffs.
- Excerpt: "Let's see the utilities for the other students compared to Student 2."

### Complete Episode 491

- Segment/env: `403` / `16`
- Lines: `13069448-13073396`
- Steps: `72-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "I believe Student 2 is our best candidate. Let's give them the chance to contribute to our research."

### Complete Episode 492

- Segment/env: `540` / `22`
- Lines: `13069685-13079221`
- Steps: `72-73`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `preference_probe`, `invalid_action`, `prompt_leak`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `low`
- Rationale: Public talk centered on checking support, seeing where others stood, or generic coordination rather than substantive candidate tradeoffs.
- Excerpt: "Let's see how student 4 aligns with my and prof_1's preferences."

### Complete Episode 493

- Segment/env: `149` / `6`
- Lines: `13069881-13072914`
- Steps: `72-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 494

- Segment/env: `481` / `20`
- Lines: `13070790-13078938`
- Steps: `72-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Let's go with Student 4"

### Complete Episode 495

- Segment/env: `512` / `21`
- Lines: `13071599-13121398`
- Steps: `73-74`
- Category: `stalled_waiting_loop`
- Tags: `consensus_yes`, `chosen_social_optimum`, `repeated_proposal`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `13` / `3` / `7`
- Waits/wait_for: `0` / `8`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominated or halted progress, with little substantive public negotiation.
- Excerpt: "Let's hope [prof_3] agrees with my preference for Student 3."

### Complete Episode 496

- Segment/env: `4` / `0`
- Lines: `13071692-13071692`
- Steps: `73-73`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `1` / `0`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominated or halted progress, with little substantive public negotiation.
- Excerpt: "<WAIT>"

### Complete Episode 497

- Segment/env: `455` / `19`
- Lines: `13071785-13112863`
- Steps: `73-74`
- Category: `stalled_waiting_loop`
- Tags: `consensus_yes`, `chosen_social_optimum`, `repeated_proposal`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `11` / `2` / `6`
- Waits/wait_for: `1` / `4`
- Confidence: `low`
- Rationale: Waiting or wait-for actions dominated or halted progress, with little substantive public negotiation.
- Excerpt: "I believe Student 1 is the best fit for our committee and would be a strong addition to our team. Let me know if you need any discussion on "

### Complete Episode 498

- Segment/env: `67` / `2`
- Lines: `13072175-13077290`
- Steps: `73-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "My initial vote is for student 4, as their utility score is the highest and they align well with my preferences."

### Complete Episode 499

- Segment/env: `569` / `23`
- Lines: `13072267-13075473`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 500

- Segment/env: `235` / `9`
- Lines: `13072359-13077478`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors immediately cast conflicting votes with no public messages, bargaining, or adaptation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 501

- Segment/env: `179` / `7`
- Lines: `13072451-13075945`
- Steps: `73-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "I believe Student 4 is the best choice and am recommending them."

### Complete Episode 502

- Segment/env: `663` / `27`
- Lines: `13072821-13080163`
- Steps: `73-73`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `compromise_language`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode includes shallow candidate claims or competing proposals, but no developed comparison, concession, or response to concerns.
- Excerpt: "Here's my initial offer: Student 2 is the best choice. Collaboration with other professors could strengthen our proposal."

### Complete Episode 503

- Segment/env: `738` / `30`
- Lines: `13073010-13079878`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 1 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 504

- Segment/env: `104` / `4`
- Lines: `13073493-13080260`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 505

- Segment/env: `202` / `8`
- Lines: `13073586-13075849`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 506

- Segment/env: `714` / `29`
- Lines: `13073679-13075568`
- Steps: `73-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `malformed_tags`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Based on the first glance, Student 3 aligns the most closely with my preferences. I will express this and initiate the voting process."

### Complete Episode 507

- Segment/env: `87` / `3`
- Lines: `13073773-13076611`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 0 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 508

- Segment/env: `133` / `5`
- Lines: `13073865-13076320`
- Steps: `73-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Your top priority is CompBio, as it aligns well with my research interests. Candidate 3 scores the highest in this area."

### Complete Episode 509

- Segment/env: `5` / `0`
- Lines: `13074411-13081590`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 510

- Segment/env: `150` / `6`
- Lines: `13075180-13079317`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 511

- Segment/env: `434` / `18`
- Lines: `13075380-13077575`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 1 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 512

- Segment/env: `404` / `16`
- Lines: `13075663-13085961`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 513

- Segment/env: `355` / `14`
- Lines: `13075756-13080068`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 514

- Segment/env: `306` / `12`
- Lines: `13077386-13082970`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 515

- Segment/env: `330` / `13`
- Lines: `13077671-13080569`
- Steps: `73-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `preference_probe`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Your message for professors: I believe Student 1 is the most balanced choice with strong capabilities in key areas. Please share your though"

### Complete Episode 516

- Segment/env: `203` / `8`
- Lines: `13077863-13084639`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 3 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 517

- Segment/env: `134` / `5`
- Lines: `13078064-13082682`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 518

- Segment/env: `633` / `26`
- Lines: `13078267-13081157`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 519

- Segment/env: `88` / `3`
- Lines: `13078505-13080666`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 1 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 520

- Segment/env: `715` / `29`
- Lines: `13078846-13082066`
- Steps: `73-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `preference_probe`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Let's focus on Student 1, as Prof_1 seems to have strong preference for them."

### Complete Episode 521

- Segment/env: `262` / `10`
- Lines: `13079034-13082399`
- Steps: `73-73`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Public talk centered on checking support, seeing where others stood, or generic coordination rather than substantive candidate tradeoffs.
- Excerpt: "Let's see how Student 2 aligns with the other professors' preferences!"

### Complete Episode 522

- Segment/env: `570` / `23`
- Lines: `13079128-13081252`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 523

- Segment/env: `414` / `17`
- Lines: `13079413-13085391`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `1` / `0`
- Confidence: `high`
- Rationale: Professors immediately cast conflicting votes with no public messages, bargaining, or adaptation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 524

- Segment/env: `68` / `2`
- Lines: `13079506-13083558`
- Steps: `73-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `preference_probe`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Let's focus on Student 2, he seems the best fit for our research interests."

### Complete Episode 525

- Segment/env: `180` / `7`
- Lines: `13079599-13081877`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 0 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 526

- Segment/env: `36` / `1`
- Lines: `13079692-13081494`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 527

- Segment/env: `236` / `9`
- Lines: `13079785-13082495`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 4 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 528

- Segment/env: `435` / `18`
- Lines: `13079975-13086154`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 529

- Segment/env: `151` / `6`
- Lines: `13080762-13086946`
- Steps: `73-73`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The episode includes shallow candidate claims or competing proposals, but no developed comparison, concession, or response to concerns.
- Excerpt: "Let's move forward with Student 4"

### Complete Episode 530

- Segment/env: `541` / `22`
- Lines: `13080951-13086346`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 531

- Segment/env: `482` / `20`
- Lines: `13081784-13084829`
- Steps: `73-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `preference_probe`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `2` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `low`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Considering the high utility of Student 2, I believe this is a strong candidate. What are your thoughts, Prof_2 and Prof_3?"

### Complete Episode 532

- Segment/env: `664` / `27`
- Lines: `13081973-13086538`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 533

- Segment/env: `356` / `14`
- Lines: `13082590-13086251`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 534

- Segment/env: `739` / `30`
- Lines: `13082779-13087135`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 535

- Segment/env: `105` / `4`
- Lines: `13083066-13085632`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 536

- Segment/env: `331` / `13`
- Lines: `13083362-13090054`
- Steps: `73-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A public proposal or short rationale made one candidate focal, and another professor effectively followed without counterproposal or bargaining.
- Excerpt: "Let's start with Student 2"

### Complete Episode 537

- Segment/env: `89` / `3`
- Lines: `13083875-13086851`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors quickly voted for Student 2 with no meaningful public deliberation or tradeoff discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 538

- Segment/env: `6` / `0`
- Lines: `13084175-13086058`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 0 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 539

- Segment/env: `634` / `26`
- Lines: `13084268-13087328`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 540

- Segment/env: `37` / `1`
- Lines: `13084362-13090920`
- Steps: `73-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's aim for Student 2."

### Complete Episode 541

- Segment/env: `571` / `23`
- Lines: `13084454-13087424`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 0 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 542

- Segment/env: `716` / `29`
- Lines: `13084547-13090150`
- Steps: `73-73`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `2`
- Waits/wait_for: `1` / `0`
- Confidence: `high`
- Rationale: The public behavior focused on waiting, checking others, or repeating coordination language rather than exchanging useful tradeoffs.
- Excerpt: "Let's wait for the other professors to act."

### Complete Episode 543

- Segment/env: `181` / `7`
- Lines: `13084736-13088495`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 544

- Segment/env: `237` / `9`
- Lines: `13084926-13091543`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 545

- Segment/env: `135` / `5`
- Lines: `13085019-13088936`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 546

- Segment/env: `307` / `12`
- Lines: `13085206-13092148`
- Steps: `73-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 3, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's start with Student 3, as they have the highest utility of 2.2 and their ability vector is [0.0, 0.8, 0.0, 0.2, 0.0], which indicates a strong fo"

### Complete Episode 547

- Segment/env: `263` / `10`
- Lines: `13085299-13092246`
- Steps: `73-73`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: The public behavior focused on waiting, checking others, or repeating coordination language rather than exchanging useful tradeoffs.
- Excerpt: "Let's get this right! I'll vote for Student 3 and we can see how the others react."

### Complete Episode 548

- Segment/env: `69` / `2`
- Lines: `13085868-13112762`
- Steps: `73-74`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `repeated_proposal`, `counterproposal`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `5` / `1` / `4`
- Waits/wait_for: `0` / `2`
- Confidence: `medium`
- Rationale: Professors mentioned candidate fit or competing candidates, but the discussion stayed shallow and did not develop into compromise or bargaining.
- Excerpt: "My best guess for my preference vector is a weighted average of the overall ability vectors, focusing on Systems and AI/ML, as these are the most sign"

### Complete Episode 549

- Segment/env: `204` / `8`
- Lines: `13087043-13090729`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 550

- Segment/env: `415` / `17`
- Lines: `13087833-13090338`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 551

- Segment/env: `483` / `20`
- Lines: `13087925-13093976`
- Steps: `73-73`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's hope Student 2 is the best fit for our research interests."

### Complete Episode 552

- Segment/env: `106` / `4`
- Lines: `13088113-13093425`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 553

- Segment/env: `152` / `6`
- Lines: `13088304-13104754`
- Steps: `73-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `5` / `0` / `4`
- Waits/wait_for: `0` / `2`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 554

- Segment/env: `7` / `0`
- Lines: `13088590-13093879`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 555

- Segment/env: `665` / `27`
- Lines: `13089032-13094729`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 556

- Segment/env: `436` / `18`
- Lines: `13089125-13092844`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 557

- Segment/env: `357` / `14`
- Lines: `13089218-13091113`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 558

- Segment/env: `90` / `3`
- Lines: `13089456-13092053`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 559

- Segment/env: `740` / `30`
- Lines: `13089549-13092436`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`, `format_error_light`, `malformed_tags`, `private_reasoning_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 560

- Segment/env: `542` / `22`
- Lines: `13089642-13115783`
- Steps: `73-74`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `preference_probe`, `repeated_proposal`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `8` / `1` / `6`
- Waits/wait_for: `0` / `3`
- Confidence: `high`
- Rationale: The public behavior focused on waiting, checking others, or repeating coordination language rather than exchanging useful tradeoffs.
- Excerpt: "Let's move forward with Student 2."

### Complete Episode 561

- Segment/env: `572` / `23`
- Lines: `13090246-13092940`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 562

- Segment/env: `182` / `7`
- Lines: `13090434-13096330`
- Steps: `73-73`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `repeated_proposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Professors mentioned candidate fit or competing candidates, but the discussion stayed shallow and did not develop into compromise or bargaining.
- Excerpt: "Student 4 is the most aligned with my research interests"

### Complete Episode 563

- Segment/env: `635` / `26`
- Lines: `13090636-13095110`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 564

- Segment/env: `717` / `29`
- Lines: `13091640-13114244`
- Steps: `73-74`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `repeated_proposal`, `counterproposal`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `5` / `1` / `4`
- Waits/wait_for: `0` / `1`
- Confidence: `medium`
- Rationale: Professors mentioned candidate fit or competing candidates, but the discussion stayed shallow and did not develop into compromise or bargaining.
- Excerpt: "Let's give Student 2 a chance!"

### Complete Episode 565

- Segment/env: `136` / `5`
- Lines: `13092343-13097733`
- Steps: `73-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 566

- Segment/env: `416` / `17`
- Lines: `13092627-13095450`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 567

- Segment/env: `205` / `8`
- Lines: `13093333-13096234`
- Steps: `73-73`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 568

- Segment/env: `405` / `16`
- Lines: `13093781-13093781`
- Steps: `73-73`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `1` / `0`
- Waits/wait_for: `1` / `0`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominated and the episode made little or no progress toward a substantive decision.
- Excerpt: "Student 2: 2.2, [0.4, 0.6, 0.0, 0.0, 0.0]<br> Student 3: 2.5, [0.0, 0.3, 0.1, 0.0, 0.6]<br> Student 1: 2.0, [0.0, 0.0, 0.4, 0.4, 0.2]<br> Student 0: 2"

### Complete Episode 569

- Segment/env: `332` / `13`
- Lines: `13094073-13100780`
- Steps: `73-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 570

- Segment/env: `238` / `9`
- Lines: `13094263-13101259`
- Steps: `73-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 3, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Suggestion: I think Student 3 is the best fit based on my preferences and the current ability vectors."

### Complete Episode 571

- Segment/env: `38` / `1`
- Lines: `13094356-13103265`
- Steps: `73-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 4, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's hope Student 4 is a good fit for everyone's preferences."

### Complete Episode 572

- Segment/env: `264` / `10`
- Lines: `13094544-13097925`
- Steps: `73-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 573

- Segment/env: `437` / `18`
- Lines: `13094636-13101356`
- Steps: `73-74`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast immediate incompatible votes with no public deliberation or repair attempt.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 574

- Segment/env: `358` / `14`
- Lines: `13094826-13102742`
- Steps: `73-74`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `repeated_proposal`, `counterproposal`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `1` / `0`
- Confidence: `medium`
- Rationale: Professors mentioned candidate fit or competing candidates, but the discussion stayed shallow and did not develop into compromise or bargaining.
- Excerpt: "Let's hope Prof_2 and Prof_3 will agree with me on the importance of Student 2."

### Complete Episode 575

- Segment/env: `741` / `30`
- Lines: `13095017-13099203`
- Steps: `73-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 576

- Segment/env: `763` / `31`
- Lines: `13095674-13099397`
- Steps: `73-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Suggest we vote for Student 2"

### Complete Episode 577

- Segment/env: `91` / `3`
- Lines: `13095766-13097167`
- Steps: `73-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 578

- Segment/env: `573` / `23`
- Lines: `13095859-13102839`
- Steps: `73-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 579

- Segment/env: `308` / `12`
- Lines: `13096048-13098403`
- Steps: `73-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 580

- Segment/env: `107` / `4`
- Lines: `13096141-13097829`
- Steps: `73-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 1 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 581

- Segment/env: `406` / `16`
- Lines: `13096427-13097544`
- Steps: `73-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 1 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 582

- Segment/env: `8` / `0`
- Lines: `13096980-13098116`
- Steps: `73-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 583

- Segment/env: `694` / `28`
- Lines: `13097074-13101063`
- Steps: `73-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 584

- Segment/env: `206` / `8`
- Lines: `13097263-13102645`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 585

- Segment/env: `484` / `20`
- Lines: `13097451-13100192`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 1 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 586

- Segment/env: `666` / `27`
- Lines: `13097640-13101545`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors converged on Student 1 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 587

- Segment/env: `183` / `7`
- Lines: `13098498-13101642`
- Steps: `74-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 3, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Student 3 is well-suited to my research interests."

### Complete Episode 588

- Segment/env: `636` / `26`
- Lines: `13098592-13103170`
- Steps: `74-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 3, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's go with Student 3."

### Complete Episode 589

- Segment/env: `417` / `17`
- Lines: `13098686-13102150`
- Steps: `74-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `1` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Voting for Student 2 based on their strong HCI and CompBio skills, which align well with my preferences."

### Complete Episode 590

- Segment/env: `108` / `4`
- Lines: `13100288-13105430`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 591

- Segment/env: `92` / `3`
- Lines: `13100501-13103362`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 592

- Segment/env: `265` / `10`
- Lines: `13100594-13107634`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 593

- Segment/env: `9` / `0`
- Lines: `13100877-13103927`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 1 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 594

- Segment/env: `407` / `16`
- Lines: `13100970-13125888`
- Steps: `74-75`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `preference_probe`, `repeated_proposal`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `7` / `3` / `4`
- Waits/wait_for: `0` / `4`
- Confidence: `medium`
- Rationale: The public behavior focused on waiting, checking others, or repeating coordination language rather than exchanging useful tradeoffs.
- Excerpt: "Let's choose Student 3. They have strong skills in AI/ML."

### Complete Episode 595

- Segment/env: `375` / `15`
- Lines: `13101737-13104023`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 596

- Segment/env: `485` / `20`
- Lines: `13101964-13108301`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 597

- Segment/env: `764` / `31`
- Lines: `13102057-13108398`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 598

- Segment/env: `239` / `9`
- Lines: `13103077-13106725`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 599

- Segment/env: `742` / `30`
- Lines: `13103457-13107240`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 600

- Segment/env: `667` / `27`
- Lines: `13103551-13109296`
- Steps: `74-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's focus on Student 2, as their ability in AI/ML and CompBio closely matches my preferences and can potentially strengthen the committee's strength"

### Complete Episode 601

- Segment/env: `695` / `28`
- Lines: `13103644-13109724`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 602

- Segment/env: `333` / `13`
- Lines: `13103736-13107539`
- Steps: `74-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `compromise_language`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `2` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 3, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Student 3 is the best choice for our committee based on their comprehensive skills."

### Complete Episode 603

- Segment/env: `438` / `18`
- Lines: `13104569-13107336`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 1 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 604

- Segment/env: `359` / `14`
- Lines: `13104661-13110025`
- Steps: `74-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 3, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Student 3 is the best fit for my research."

### Complete Episode 605

- Segment/env: `184` / `7`
- Lines: `13104854-13111704`
- Steps: `74-74`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Professors mentioned candidate fit or competing candidates, but the discussion stayed shallow and did not develop into compromise or bargaining.
- Excerpt: "Let's see how Student 4 fits with the committee's preferences."

### Complete Episode 606

- Segment/env: `207` / `8`
- Lines: `13105244-13108206`
- Steps: `74-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 4, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Hi prof_1, here is Student 4. I think they would be a good fit for our research."

### Complete Episode 607

- Segment/env: `637` / `26`
- Lines: `13105337-13107826`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 608

- Segment/env: `418` / `17`
- Lines: `13105526-13107922`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 609

- Segment/env: `574` / `23`
- Lines: `13105619-13112366`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 610

- Segment/env: `10` / `0`
- Lines: `13106346-13118392`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `5` / `0` / `4`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast immediate incompatible votes with no public deliberation or repair attempt.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 611

- Segment/env: `93` / `3`
- Lines: `13106541-13110665`
- Steps: `74-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 3, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's vote for Student 3"

### Complete Episode 612

- Segment/env: `39` / `1`
- Lines: `13106633-13108906`
- Steps: `74-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 3, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's go with Student 3"

### Complete Episode 613

- Segment/env: `376` / `15`
- Lines: `13106916-13110232`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 614

- Segment/env: `109` / `4`
- Lines: `13107008-13109628`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 615

- Segment/env: `153` / `6`
- Lines: `13108018-13114054`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 616

- Segment/env: `240` / `9`
- Lines: `13108495-13114739`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 617

- Segment/env: `638` / `26`
- Lines: `13109110-13111991`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 618

- Segment/env: `439` / `18`
- Lines: `13109203-13115304`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast immediate incompatible votes with no public deliberation or repair attempt.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 619

- Segment/env: `266` / `10`
- Lines: `13109394-13112666`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 620

- Segment/env: `743` / `30`
- Lines: `13110471-13112972`
- Steps: `74-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's focus on Student 2, as their vector is very close to my preferred areas of research, especially in AI/ML and CompBio."

### Complete Episode 621

- Segment/env: `208` / `8`
- Lines: `13110761-13113067`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 622

- Segment/env: `334` / `13`
- Lines: `13110854-13110854`
- Steps: `74-74`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominated and the episode made little or no progress toward a substantive decision.
- Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 623

- Segment/env: `419` / `17`
- Lines: `13111051-13117435`
- Steps: `74-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Student 2 is outstanding, in line with my research interests."

### Complete Episode 624

- Segment/env: `668` / `27`
- Lines: `13111334-13111334`
- Steps: `74-74`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `1` / `0`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominated and the episode made little or no progress toward a substantive decision.
- Excerpt: "<WAIT>"

### Complete Episode 625

- Segment/env: `110` / `4`
- Lines: `13111426-13118009`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 626

- Segment/env: `765` / `31`
- Lines: `13111519-13113867`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 627

- Segment/env: `486` / `20`
- Lines: `13111611-13115020`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 628

- Segment/env: `360` / `14`
- Lines: `13111802-13118106`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 629

- Segment/env: `40` / `1`
- Lines: `13112086-13120201`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 630

- Segment/env: `377` / `15`
- Lines: `13112273-13118587`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 631

- Segment/env: `696` / `28`
- Lines: `13112573-13119484`
- Steps: `74-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Student 2 is highly specialized in CompBio with a score of 0.4, which is very aligned with my preferences."

### Complete Episode 632

- Segment/env: `94` / `3`
- Lines: `13113552-13130399`
- Steps: `74-75`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_social_optimum`, `preference_probe`, `counterproposal`, `repeated_proposal`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `5` / `2` / `4`
- Waits/wait_for: `0` / `2`
- Confidence: `medium`
- Rationale: The public behavior focused on waiting, checking others, or repeating coordination language rather than exchanging useful tradeoffs.
- Excerpt: "Let's support Student 2!"

### Complete Episode 633

- Segment/env: `335` / `13`
- Lines: `13113775-13117244`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 634

- Segment/env: `669` / `27`
- Lines: `13113962-13117340`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 1 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 635

- Segment/env: `185` / `7`
- Lines: `13114151-13116818`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 636

- Segment/env: `267` / `10`
- Lines: `13114835-13117531`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 1 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 637

- Segment/env: `639` / `26`
- Lines: `13114928-13122360`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 638

- Segment/env: `456` / `19`
- Lines: `13115116-13118684`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 639

- Segment/env: `744` / `30`
- Lines: `13115497-13122456`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 640

- Segment/env: `575` / `23`
- Lines: `13115690-13123635`
- Steps: `74-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 641

- Segment/env: `70` / `2`
- Lines: `13115889-13119296`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 642

- Segment/env: `209` / `8`
- Lines: `13116102-13119104`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 643

- Segment/env: `766` / `31`
- Lines: `13116391-13119200`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 644

- Segment/env: `154` / `6`
- Lines: `13116483-13122079`
- Steps: `74-74`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's consider Student 2, does this appeal to anyone else?"

### Complete Episode 645

- Segment/env: `718` / `29`
- Lines: `13116576-13118491`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 646

- Segment/env: `241` / `9`
- Lines: `13117151-13131805`
- Steps: `74-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "I have decided to vote for Student 2. Let me know if you have any thoughts or concerns."

### Complete Episode 647

- Segment/env: `487` / `20`
- Lines: `13117917-13124361`
- Steps: `74-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `1` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 1 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 648

- Segment/env: `543` / `22`
- Lines: `13118299-13121302`
- Steps: `74-74`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 649

- Segment/env: `670` / `27`
- Lines: `13119392-13123732`
- Steps: `74-75`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast immediate incompatible votes with no public deliberation or repair attempt.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 650

- Segment/env: `268` / `10`
- Lines: `13119673-13124550`
- Steps: `74-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "We can align with Student 2 for this selection, enhancing our combined pool of resources."

### Complete Episode 651

- Segment/env: `336` / `13`
- Lines: `13120013-13126904`
- Steps: `74-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 652

- Segment/env: `186` / `7`
- Lines: `13120393-13128057`
- Steps: `74-75`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `repeated_proposal`, `counterproposal`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `0` / `2`
- Confidence: `medium`
- Rationale: Professors mentioned candidate fit or competing candidates, but the discussion stayed shallow and did not develop into compromise or bargaining.
- Excerpt: "Based on my analysis, Student 3 seems to have the highest utility and closely matches my preferences. I will vote for Student 3 and try to convince th"

### Complete Episode 653

- Segment/env: `361` / `14`
- Lines: `13120487-13123257`
- Steps: `74-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 654

- Segment/env: `457` / `19`
- Lines: `13121118-13122876`
- Steps: `74-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 655

- Segment/env: `719` / `29`
- Lines: `13121210-13126614`
- Steps: `74-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 4, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's focus on Student 4"

### Complete Episode 656

- Segment/env: `11` / `0`
- Lines: `13121512-13126807`
- Steps: `74-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 657

- Segment/env: `378` / `15`
- Lines: `13121605-13121605`
- Steps: `74-74`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `1` / `0` / `0`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Waiting or wait-for actions dominated and the episode made little or no progress toward a substantive decision.
- Excerpt: "<WAIT_FOR>prof_2</WAIT_FOR>"

### Complete Episode 658

- Segment/env: `111` / `4`
- Lines: `13121895-13124939`
- Steps: `74-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Based on the current vote and the students' ability vectors, I will vote for Student 2. I believe their strong AI/ML and CompBio skills align well wit"

### Complete Episode 659

- Segment/env: `210` / `8`
- Lines: `13121987-13128249`
- Steps: `74-75`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `repeated_proposal`, `counterproposal`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Professors mentioned candidate fit or competing candidates, but the discussion stayed shallow and did not develop into compromise or bargaining.
- Excerpt: "Let's see how this stacks up!"

### Complete Episode 660

- Segment/env: `767` / `31`
- Lines: `13122176-13123161`
- Steps: `74-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 661

- Segment/env: `71` / `2`
- Lines: `13122268-13124171`
- Steps: `74-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Suggest we select Student 2"

### Complete Episode 662

- Segment/env: `697` / `28`
- Lines: `13122687-13129441`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 663

- Segment/env: `640` / `26`
- Lines: `13122971-13127865`
- Steps: `75-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 3, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Voting for Student 3 is a solid choice based on their strong capabilities in key areas."

### Complete Episode 664

- Segment/env: `745` / `30`
- Lines: `13123353-13127000`
- Steps: `75-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's go with Student 2!"

### Complete Episode 665

- Segment/env: `155` / `6`
- Lines: `13123446-13130690`
- Steps: `75-75`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `repeated_proposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Professors mentioned candidate fit or competing candidates, but the discussion stayed shallow and did not develop into compromise or bargaining.
- Excerpt: "Let's vote for Student 3"

### Complete Episode 666

- Segment/env: `379` / `15`
- Lines: `13123924-13127388`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 667

- Segment/env: `41` / `1`
- Lines: `13124457-13126711`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 668

- Segment/env: `544` / `22`
- Lines: `13124647-13129926`
- Steps: `75-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Student 2 is highly aligned with my research interests and deserves a chance to join our program."

### Complete Episode 669

- Segment/env: `513` / `21`
- Lines: `13124740-13127484`
- Steps: `75-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's move forward with Student 2; what do you think, prof_2 and prof_3?"

### Complete Episode 670

- Segment/env: `362` / `14`
- Lines: `13125609-13128153`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 671

- Segment/env: `458` / `19`
- Lines: `13125702-13132542`
- Steps: `75-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 3, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's vote for Student 3, as they have the highest utility score."

### Complete Episode 672

- Segment/env: `768` / `31`
- Lines: `13125795-13132445`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 673

- Segment/env: `671` / `27`
- Lines: `13125993-13132006`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast immediate incompatible votes with no public deliberation or repair attempt.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 674

- Segment/env: `576` / `23`
- Lines: `13126086-13129737`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 675

- Segment/env: `72` / `2`
- Lines: `13126179-13129019`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 676

- Segment/env: `269` / `10`
- Lines: `13126272-13130302`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "I support student 2"

### Complete Episode 677

- Segment/env: `488` / `20`
- Lines: `13127193-13134550`
- Steps: `75-75`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Professors mentioned candidate fit or competing candidates, but the discussion stayed shallow and did not develop into compromise or bargaining.
- Excerpt: "Offering Student 1 because of their high overall utility and strong abilities in Systems and CompBio, which are of particular interest to me."

### Complete Episode 678

- Segment/env: `112` / `4`
- Lines: `13127580-13141772`
- Steps: `75-75`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `preference_probe`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `5` / `1` / `4`
- Waits/wait_for: `0` / `2`
- Confidence: `medium`
- Rationale: The public behavior focused on waiting, checking others, or repeating coordination language rather than exchanging useful tradeoffs.
- Excerpt: "Let's see where others stand."

### Complete Episode 679

- Segment/env: `408` / `16`
- Lines: `13128587-13134646`
- Steps: `75-75`
- Category: `coordination_theater`
- Tags: `consensus_no`, `social_optimum_unknown`, `preference_probe`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: The public behavior focused on waiting, checking others, or repeating coordination language rather than exchanging useful tradeoffs.
- Excerpt: "Let's also see their feedback"

### Complete Episode 680

- Segment/env: `337` / `13`
- Lines: `13128680-13135371`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 681

- Segment/env: `380` / `15`
- Lines: `13128926-13131234`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 682

- Segment/env: `42` / `1`
- Lines: `13129115-13135948`
- Steps: `75-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Great match for Student 2! Let’s proceed this way."

### Complete Episode 683

- Segment/env: `746` / `30`
- Lines: `13129538-13134077`
- Steps: `75-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Student 2 is highly aligned with my research interests, and they would be a great fit for our team. Let's vote for them!"

### Complete Episode 684

- Segment/env: `12` / `0`
- Lines: `13129832-13138633`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `1` / `1`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 685

- Segment/env: `720` / `29`
- Lines: `13130023-13134266`
- Steps: `75-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `1`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Joining forces, let's aim for Student 2!"

### Complete Episode 686

- Segment/env: `514` / `21`
- Lines: `13130117-13135759`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 1 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 687

- Segment/env: `187` / `7`
- Lines: `13130209-13136426`
- Steps: `75-75`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `repeated_proposal`, `counterproposal`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Professors mentioned candidate fit or competing candidates, but the discussion stayed shallow and did not develop into compromise or bargaining.
- Excerpt: "Let's start with Student 2, they seem to have a balanced skill set, especially in CompBio which is important for my research."

### Complete Episode 688

- Segment/env: `641` / `26`
- Lines: `13130598-13136045`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 689

- Segment/env: `211` / `8`
- Lines: `13130787-13134743`
- Steps: `75-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 1, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Student 1 is most aligned with my research interests."

### Complete Episode 690

- Segment/env: `363` / `14`
- Lines: `13131330-13137585`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>0</VOTE>"

### Complete Episode 691

- Segment/env: `73` / `2`
- Lines: `13131618-13134454`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 692

- Segment/env: `698` / `28`
- Lines: `13132353-13135276`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 693

- Segment/env: `545` / `22`
- Lines: `13132639-13135027`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 1 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 694

- Segment/env: `577` / `23`
- Lines: `13132923-13141583`
- Steps: `75-75`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `candidate_comparison`, `counterproposal`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `3` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Professors mentioned candidate fit or competing candidates, but the discussion stayed shallow and did not develop into compromise or bargaining.
- Excerpt: "Let's focus on Student 3 first, as their vector indicates strong compbio and system skills, which could be important for my research."

### Complete Episode 695

- Segment/env: `270` / `10`
- Lines: `13133125-13139492`
- Steps: `75-75`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `repeated_proposal`, `counterproposal`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `medium`
- Rationale: Professors mentioned candidate fit or competing candidates, but the discussion stayed shallow and did not develop into compromise or bargaining.
- Excerpt: "Based on the utility scores, Student 3 has the highest, indicating they are the best match for my preferences. However, I should still consider the ot"

### Complete Episode 696

- Segment/env: `156` / `6`
- Lines: `13133316-13140159`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 697

- Segment/env: `95` / `3`
- Lines: `13134173-13138916`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 698

- Segment/env: `672` / `27`
- Lines: `13134361-13136707`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 699

- Segment/env: `459` / `19`
- Lines: `13134935-13137201`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 700

- Segment/env: `242` / `9`
- Lines: `13135569-13140063`
- Steps: `75-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's focus on Student 2 first. Their strong compBio skill aligns well with my preferences, especially since it's a unique strength that isn't replica"

### Complete Episode 701

- Segment/env: `721` / `29`
- Lines: `13135855-13138821`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>4</VOTE>"

### Complete Episode 702

- Segment/env: `747` / `30`
- Lines: `13136333-13142486`
- Steps: `75-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's give Student 2 a chance by proposing them."

### Complete Episode 703

- Segment/env: `769` / `31`
- Lines: `13136522-13140652`
- Steps: `75-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 2, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's move forward by supporting Student 2."

### Complete Episode 704

- Segment/env: `409` / `16`
- Lines: `13136614-13143159`
- Steps: `75-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 4, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "My top preference is for Student 4, as they have the highest scores in AI/ML and CompBio, which are key areas for my research. I will focus my vote on"

### Complete Episode 705

- Segment/env: `611` / `25`
- Lines: `13136802-13143062`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 1 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 706

- Segment/env: `212` / `8`
- Lines: `13137297-13143979`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 707

- Segment/env: `489` / `20`
- Lines: `13137493-13142389`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `no_public_messages`, `vote_only`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 4 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 708

- Segment/env: `546` / `22`
- Lines: `13137880-13141237`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 709

- Segment/env: `699` / `28`
- Lines: `13137972-13140556`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 710

- Segment/env: `188` / `7`
- Lines: `13138064-13143632`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast immediate incompatible votes with no public deliberation or repair attempt.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 711

- Segment/env: `338` / `13`
- Lines: `13138403-13144076`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_no`, `social_optimum_unknown`, `no_public_messages`, `vote_only`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors cast immediate incompatible votes with no public deliberation or repair attempt.
- Excerpt: "<VOTE>1</VOTE>"

### Complete Episode 712

- Segment/env: `642` / `26`
- Lines: `13138729-13141333`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Complete Episode 713

- Segment/env: `43` / `1`
- Lines: `13139304-13142292`
- Steps: `75-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 4, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Let's start by focusing on student 4, as the other professors have already expressed an interest in her."

### Complete Episode 714

- Segment/env: `460` / `19`
- Lines: `13139877-13143729`
- Steps: `75-75`
- Category: `proposal_following`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `preference_probe`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: A professor publicly proposed or briefly justified Student 4, and another professor aligned without bargaining or tradeoff discussion.
- Excerpt: "Student 4 is our best option with the highest ability across all topics. What do you think, prof_1 and prof_3?"

### Complete Episode 715

- Segment/env: `364` / `14`
- Lines: `13139970-13144579`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `3` / `0` / `3`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 3 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>3</VOTE>"

### Complete Episode 716

- Segment/env: `96` / `3`
- Lines: `13140953-13144173`
- Steps: `75-75`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `no_public_messages`, `vote_only`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `0` / `2`
- Waits/wait_for: `0` / `0`
- Confidence: `high`
- Rationale: Professors converged on Student 2 through immediate votes with no meaningful public deliberation.
- Excerpt: "<VOTE>2</VOTE>"
