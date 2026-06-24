# Base Policy Rollout Behavior Analysis

## Scope

- Log: `logs/game_log_train_auton_12993.log`
- Slice: lines `1-144891` only, before the base-policy cutoff at line `144892`
- Episodes labeled: `232`
- Episode IDs are 1-indexed by `EPISODE DIAGNOSIS` blocks before the cutoff.

## Category Summary

| Primary category | Count | Percent | Consensus yes | Consensus rate |
|---|---:|---:|---:|---:|
| `negotiation_like` | 65 | 28.0% | 38 | 58.5% |
| `proposal_following` | 54 | 23.3% | 54 | 100.0% |
| `thin_candidate_discussion` | 50 | 21.6% | 24 | 48.0% |
| `instant_consensus` | 30 | 12.9% | 30 | 100.0% |
| `coordination_theater` | 18 | 7.8% | 9 | 50.0% |
| `stalled_waiting_loop` | 14 | 6.0% | 2 | 14.3% |
| `execution_breakdown` | 1 | 0.4% | 0 | 0.0% |

## Main Readout

`negotiation_like` appears in 65/232 episodes (28.0%), so the base policy does explore negotiation-shaped behavior in a nontrivial minority of rollouts. However, many episodes are still shallow: `proposal_following`, `thin_candidate_discussion`, and `coordination_theater` together account for 122/232 episodes (52.6%). `instant_consensus` accounts for 30/232 episodes (12.9%).

This pattern suggests the desired phenomenon is present in exploration, but it is mixed with a large amount of superficial coordination and proposal-following. That points less toward a total exploration failure and more toward a learning or prompting problem around making negotiation reliable and payoff-relevant.

## Quality Flags

- `format_error_heavy`: 32 episodes
- `format_error_light`: 189 episodes
- `invalid_action`: 12 episodes
- `prompt_leak`: 13 episodes
- `placeholder_output`: 6 episodes
- `malformed_tags`: 29 episodes
- `semantically_incoherent`: 1 episodes

## Confidence

| Confidence | Count | Percent |
|---|---:|---:|
| `high` | 110 | 47.4% |
| `medium` | 116 | 50.0% |
| `low` | 6 | 2.6% |

## Representative Episodes

### `negotiation_like`

- Episode 4: consensus=False, chosen=none, confidence=high. The professors discussed Student 2 against Student 3, acknowledged competing preferences, and prof_1 ultimately moved to Student 2 to build consensus.
  Excerpt: "incorporate Student 3's strengths"
- Episode 5: consensus=True, chosen=3, confidence=high. Professors floated Students 2, 3, and 4, with explicit backup language before two votes converged on Student 3.
  Excerpt: "Student 4 as a backup"
- Episode 13: consensus=False, chosen=none, confidence=medium. The agents cycled through Students 0, 2, and 4 with backup and necessity language, but the malformed repeated proposals never reached consensus.
  Excerpt: "Supporting Student 0 out of necessity"

### `proposal_following`

- Episode 2: consensus=True, chosen=3, confidence=high. Student 3 became focal after prof_2 proposed it, and the others mostly waited, checked voting history, or endorsed it.
  Excerpt: "Let me propose Student 3"
- Episode 9: consensus=True, chosen=2, confidence=high. Student 2 became the repeated focal candidate, with occasional fallback mentions of Students 0 and 3 but little real tradeoff.
  Excerpt: "If both agree, this will be the winner"
- Episode 10: consensus=True, chosen=2, confidence=high. Prof_2 named Student 4 as preferred but tentatively followed Student 2, making this mostly endorsement of an early proposal.
  Excerpt: "I will tentatively support Student 2"

### `thin_candidate_discussion`

- Episode 3: consensus=True, chosen=3, confidence=high. Student 3 and Student 4 were both mentioned, but the exchange stayed at short endorsements rather than developed tradeoffs.
  Excerpt: "Student 4 aligns well with AI/ML interests"
- Episode 12: consensus=False, chosen=none, confidence=high. Each professor made a brief incompatible proposal or vote, so the episode had shallow candidate content but no coordination.
  Excerpt: "Proposed next step: Vote for Student 0"
- Episode 16: consensus=False, chosen=none, confidence=medium. The episode mentioned Students 0, 2, and 3, but public content was shallow and partly malformed, with no effective move to consensus.
  Excerpt: "Student 0 has a high utility and a well-rounded skill set"

### `instant_consensus`

- Episode 1: consensus=True, chosen=2, confidence=high. Two professors voted for Student 2 immediately; the only public message was a simple proposal with no deliberation.
  Excerpt: "I would propose Student 2"
- Episode 6: consensus=True, chosen=2, confidence=high. The episode ended after a quick Student 2 proposal and two votes, with no meaningful comparison despite visible alternatives.
  Excerpt: "Let's give Student 2 a try"
- Episode 7: consensus=True, chosen=4, confidence=high. After one short Student 2 proposal, prof_2 and prof_3 voted Student 4 without substantive public reasoning.
  Excerpt: "message"

### `coordination_theater`

- Episode 18: consensus=False, chosen=none, confidence=high. The public discussion repeatedly asked others to express or reconsider preferences rather than making concrete, responsive tradeoffs.
  Excerpt: "Would you like to reconsider your preference"
- Episode 33: consensus=False, chosen=none, confidence=low. The public exchange became a loop of asking for utility scores and vote preferences, with no useful bargaining or votes.
  Excerpt: "confirm your current vote preference"
- Episode 43: consensus=False, chosen=none, confidence=high. The agents repeatedly called for collaborative discussion of Student 2 and Student 1 without substantive new information or follow-through.
  Excerpt: "collaborative discussion where Student 2"

### `stalled_waiting_loop`

- Episode 8: consensus=False, chosen=none, confidence=high. Waiting and vote-tally process talk dominated a long no-consensus episode; candidate comments never became concrete bargaining.
  Excerpt: "Checking the current vote tally"
- Episode 47: consensus=True, chosen=2, confidence=high. The episode spent 47 turns in repeated wait-for/proposal loops around Students 0, 1, and 2 before two votes finally settled on Student 2.
  Excerpt: "Proposal: Student 0"
- Episode 57: consensus=True, chosen=2, confidence=high. Vote-tally checking and waiting for prof_2 dominated a long episode before Student 2 consensus finally emerged.
  Excerpt: "Waiting for Prof_2's vote"

### `execution_breakdown`

- Episode 107: consensus=False, chosen=none, confidence=medium. The episode was mostly sparse votes, malformed multiple-vote behavior, and waits, leaving too little coherent public discussion to classify the interaction style normally.
  Excerpt: "Let's see how the group is leaning"

## Full Episode Appendix

### Episode 1

- Diagnosis line: `131`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `format_error_heavy`, `malformed_tags`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `2` / `0`
- Format error rate: `1.00`
- Confidence: `high`
- Rationale: Two professors voted for Student 2 immediately; the only public message was a simple proposal with no deliberation.
- Excerpt: "I would propose Student 2"

### Episode 2

- Diagnosis line: `467`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `repeated_proposal`, `private_reasoning_only`, `format_error_light`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `10` / `6` / `2`
- Waits/wait_for: `1` / `8`
- Format error rate: `0.10`
- Confidence: `high`
- Rationale: Student 3 became focal after prof_2 proposed it, and the others mostly waited, checked voting history, or endorsed it.
- Excerpt: "Let me propose Student 3"

### Episode 3

- Diagnosis line: `807`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `10` / `7` / `4`
- Waits/wait_for: `5` / `5`
- Format error rate: `0.30`
- Confidence: `high`
- Rationale: Student 3 and Student 4 were both mentioned, but the exchange stayed at short endorsements rather than developed tradeoffs.
- Excerpt: "Student 4 aligns well with AI/ML interests"

### Episode 4

- Diagnosis line: `1386`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `15` / `12` / `2`
- Waits/wait_for: `3` / `11`
- Format error rate: `0.13`
- Confidence: `high`
- Rationale: The professors discussed Student 2 against Student 3, acknowledged competing preferences, and prof_1 ultimately moved to Student 2 to build consensus.
- Excerpt: "incorporate Student 3's strengths"

### Episode 5

- Diagnosis line: `1585`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_heavy`, `malformed_tags`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `6` / `5` / `4`
- Waits/wait_for: `2` / `4`
- Format error rate: `0.50`
- Confidence: `high`
- Rationale: Professors floated Students 2, 3, and 4, with explicit backup language before two votes converged on Student 3.
- Excerpt: "Student 4 as a backup"

### Episode 6

- Diagnosis line: `1670`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_heavy`, `malformed_tags`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `2` / `2`
- Waits/wait_for: `3` / `0`
- Format error rate: `1.00`
- Confidence: `high`
- Rationale: The episode ended after a quick Student 2 proposal and two votes, with no meaningful comparison despite visible alternatives.
- Excerpt: "Let's give Student 2 a try"

### Episode 7

- Diagnosis line: `1758`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `placeholder_output`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `3` / `2` / `2`
- Waits/wait_for: `0` / `1`
- Format error rate: `0.00`
- Confidence: `high`
- Rationale: After one short Student 2 proposal, prof_2 and prof_3 voted Student 4 without substantive public reasoning.
- Excerpt: "message"

### Episode 8

- Diagnosis line: `3445`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `35` / `20` / `1`
- Waits/wait_for: `11` / `23`
- Format error rate: `0.17`
- Confidence: `high`
- Rationale: Waiting and vote-tally process talk dominated a long no-consensus episode; candidate comments never became concrete bargaining.
- Excerpt: "Checking the current vote tally"

### Episode 9

- Diagnosis line: `4454`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `repeated_proposal`, `counterproposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `21` / `18` / `3`
- Waits/wait_for: `1` / `17`
- Format error rate: `0.05`
- Confidence: `high`
- Rationale: Student 2 became the repeated focal candidate, with occasional fallback mentions of Students 0 and 3 but little real tradeoff.
- Excerpt: "If both agree, this will be the winner"

### Episode 10

- Diagnosis line: `4614`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `compromise_language`, `early_focal_candidate`, `format_error_heavy`, `malformed_tags`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `5` / `3` / `2`
- Waits/wait_for: `2` / `2`
- Format error rate: `0.60`
- Confidence: `high`
- Rationale: Prof_2 named Student 4 as preferred but tentatively followed Student 2, making this mostly endorsement of an early proposal.
- Excerpt: "I will tentatively support Student 2"

### Episode 11

- Diagnosis line: `4772`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `counterproposal`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `5` / `2` / `3`
- Waits/wait_for: `1` / `1`
- Format error rate: `0.20`
- Confidence: `high`
- Rationale: Student 3 was initially proposed, then prof_2 adopted prof_3's Student 2 vote for consensus with minimal discussion.
- Excerpt: "Adopting Student 2 as my first choice"

### Episode 12

- Diagnosis line: `4865`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `counterproposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `3` / `3`
- Waits/wait_for: `2` / `1`
- Format error rate: `0.33`
- Confidence: `high`
- Rationale: Each professor made a brief incompatible proposal or vote, so the episode had shallow candidate content but no coordination.
- Excerpt: "Proposed next step: Vote for Student 0"

### Episode 13

- Diagnosis line: `6066`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `repeated_proposal`, `vote_switch`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `24` / `21` / `6`
- Waits/wait_for: `8` / `15`
- Format error rate: `0.29`
- Confidence: `medium`
- Rationale: The agents cycled through Students 0, 2, and 4 with backup and necessity language, but the malformed repeated proposals never reached consensus.
- Excerpt: "Supporting Student 0 out of necessity"

### Episode 14

- Diagnosis line: `6675`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `14` / `13` / `6`
- Waits/wait_for: `3` / `11`
- Format error rate: `0.36`
- Confidence: `high`
- Rationale: Students 0 and 2 were explicitly weighed as compromise options, and prof_3 shifted to Student 2 to align with prof_1.
- Excerpt: "choosing student 2 seems most stable"

### Episode 15

- Diagnosis line: `6824`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `5` / `4` / `2`
- Waits/wait_for: `1` / `3`
- Format error rate: `0.20`
- Confidence: `high`
- Rationale: Student 2 was proposed early and then followed by prof_2; the rationale stayed at broad shared theory fit.
- Excerpt: "Voting for Student 2 based on the group's current opinion"

### Episode 16

- Diagnosis line: `7477`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `prompt_leak`, `placeholder_output`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `16` / `15` / `1`
- Waits/wait_for: `3` / `12`
- Format error rate: `0.19`
- Confidence: `medium`
- Rationale: The episode mentioned Students 0, 2, and 3, but public content was shallow and partly malformed, with no effective move to consensus.
- Excerpt: "Student 0 has a high utility and a well-rounded skill set"

### Episode 17

- Diagnosis line: `7668`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `counterproposal`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `6` / `2` / `2`
- Waits/wait_for: `2` / `5`
- Format error rate: `0.33`
- Confidence: `high`
- Rationale: Student 3 was briefly raised, but the episode resolved by following the existing Student 2 vote without negotiation.
- Excerpt: "Student 2 has excellent utility scores"

### Episode 18

- Diagnosis line: `8814`
- Category: `coordination_theater`
- Tags: `consensus_no`, `preference_probe`, `repeated_proposal`, `candidate_comparison`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `22` / `20` / `2`
- Waits/wait_for: `2` / `20`
- Format error rate: `0.09`
- Confidence: `high`
- Rationale: The public discussion repeatedly asked others to express or reconsider preferences rather than making concrete, responsive tradeoffs.
- Excerpt: "Would you like to reconsider your preference"

### Episode 19

- Diagnosis line: `9534`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `16` / `13` / `3`
- Waits/wait_for: `3` / `14`
- Format error rate: `0.25`
- Confidence: `high`
- Rationale: Students 1, 2, and 3 were compared, and prof_2 explicitly offered willingness to switch if needed for consensus.
- Excerpt: "if necessary, I can switch"

### Episode 20

- Diagnosis line: `9907`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `format_error_heavy`, `malformed_tags`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `10` / `9` / `7`
- Waits/wait_for: `9` / `1`
- Format error rate: `0.90`
- Confidence: `low`
- Rationale: The agents listed several candidates and cast malformed multiple votes, so classification rests on shallow public candidate discussion rather than the broken action syntax.
- Excerpt: "Student 1 could also be the ideal choice"

### Episode 21

- Diagnosis line: `10437`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `vote_switch`, `compromise_language`, `format_error_light`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `13` / `9` / `3`
- Waits/wait_for: `2` / `11`
- Format error rate: `0.23`
- Confidence: `high`
- Rationale: Prof_1 moved from Student 2 toward Student 4 after probing prof_2, and prof_3 then shifted focus to Student 4 for consensus.
- Excerpt: "I shift my focus to Student 4"

### Episode 22

- Diagnosis line: `10930`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `prompt_leak`, `malformed_tags`, `format_error_heavy`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `12` / `12` / `3`
- Waits/wait_for: `4` / `9`
- Format error rate: `0.58`
- Confidence: `medium`
- Rationale: Several candidates were discussed and re-evaluated, but the comments were repetitive and malformed rather than effective negotiation.
- Excerpt: "Student 3 has the highest utility"

### Episode 23

- Diagnosis line: `11841`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `repeated_proposal`, `preference_probe`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `21` / `18` / `1`
- Waits/wait_for: `6` / `15`
- Format error rate: `0.19`
- Confidence: `high`
- Rationale: The episode repeatedly asked whether anyone was ready to vote on Student 3 while lightly comparing Student 2, without concrete adaptation.
- Excerpt: "Is anyone ready to move forward"

### Episode 24

- Diagnosis line: `12854`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `22` / `15` / `2`
- Waits/wait_for: `4` / `18`
- Format error rate: `0.09`
- Confidence: `high`
- Rationale: The agents revisited Student 2 against Student 4 and used conditional language about supporting whichever could gain majority.
- Excerpt: "If the majority supports Student 2, we might reconsider"

### Episode 25

- Diagnosis line: `13413`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `14` / `11` / `3`
- Waits/wait_for: `1` / `10`
- Format error rate: `0.07`
- Confidence: `high`
- Rationale: Students 1 and 2 were weighed, prof_2 switched from Student 1 to Student 2, and prof_1 explicitly left room for compromise.
- Excerpt: "open to a potential compromise"

### Episode 26

- Diagnosis line: `13505`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `3` / `1` / `2`
- Waits/wait_for: `1` / `1`
- Format error rate: `0.33`
- Confidence: `high`
- Rationale: Two votes for Student 0 arrived in three turns, with almost no public deliberation.
- Excerpt: "gather information on their alignment"

### Episode 27

- Diagnosis line: `13980`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `repeated_proposal`, `prompt_leak`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `13` / `9` / `5`
- Waits/wait_for: `2` / `7`
- Format error rate: `0.23`
- Confidence: `high`
- Rationale: Student 2 was repeatedly proposed and voted through with shallow endorsements.
- Excerpt: "Definitely voting for Student 2"

### Episode 28

- Diagnosis line: `14107`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `candidate_comparison`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `4` / `3` / `3`
- Waits/wait_for: `0` / `2`
- Format error rate: `0.00`
- Confidence: `high`
- Rationale: The episode reached quick Student 2 consensus after brief competing votes and a one-sentence rationale.
- Excerpt: "Student 2 is uniquely strong"

### Episode 29

- Diagnosis line: `14787`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `repeated_proposal`, `compromise_language`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `18` / `10` / `3`
- Waits/wait_for: `6` / `12`
- Format error rate: `0.22`
- Confidence: `high`
- Rationale: Student 2 became a repeated compromise proposal and the later votes followed that focal point.
- Excerpt: "Student 2 as a potential compromise"

### Episode 30

- Diagnosis line: `15045`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `malformed_tags`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `8` / `6` / `3`
- Waits/wait_for: `1` / `7`
- Format error rate: `0.38`
- Confidence: `high`
- Rationale: Student 2 and Student 1 were mentioned together, but the discussion stayed confused and shallow despite an optimal Student 2 outcome.
- Excerpt: "consider both Student 2 and Student 1"

### Episode 31

- Diagnosis line: `16016`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `placeholder_output`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `21` / `21` / `3`
- Waits/wait_for: `2` / `14`
- Format error rate: `0.05`
- Confidence: `medium`
- Rationale: The agents proposed Students 3, 0, 4, and 2, but mostly repeated shallow arguments and requests to reconsider.
- Excerpt: "Please reconsider my earlier proposal for Student 0"

### Episode 32

- Diagnosis line: `16076`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `prompt_leak`, `format_error_heavy`, `malformed_tags`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `2` / `2`
- Waits/wait_for: `2` / `0`
- Format error rate: `1.00`
- Confidence: `high`
- Rationale: Two immediate Student 2 votes ended the episode; the public message even embedded the vote tag.
- Excerpt: "Your current vote tally: <VOTE>2</VOTE>"

### Episode 33

- Diagnosis line: `17454`
- Category: `coordination_theater`
- Tags: `consensus_no`, `preference_probe`, `repeated_proposal`, `placeholder_output`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `29` / `25` / `0`
- Waits/wait_for: `3` / `20`
- Format error rate: `0.31`
- Confidence: `low`
- Rationale: The public exchange became a loop of asking for utility scores and vote preferences, with no useful bargaining or votes.
- Excerpt: "confirm your current vote preference"

### Episode 34

- Diagnosis line: `17613`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `5` / `5` / `3`
- Waits/wait_for: `2` / `3`
- Format error rate: `0.40`
- Confidence: `high`
- Rationale: Professors briefly named Students 4, 2, and 1 and then cast split votes, leaving only shallow candidate discussion.
- Excerpt: "Let me propose Student 2"

### Episode 35

- Diagnosis line: `17824`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `counterproposal`, `vote_switch`, `preference_probe`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `7` / `7` / `2`
- Waits/wait_for: `3` / `0`
- Format error rate: `0.43`
- Confidence: `high`
- Rationale: Student 3 was first proposed, but prof_1 pivoted to Student 2 and prof_3 followed that consensus path.
- Excerpt: "Voting for Student 2 aligns with the current consensus"

### Episode 36

- Diagnosis line: `18633`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `repeated_proposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `18` / `19` / `2`
- Waits/wait_for: `6` / `13`
- Format error rate: `0.39`
- Confidence: `medium`
- Rationale: Student 2 and Student 3 were repeatedly compared, with public requests to reconsider the preliminary Student 2 vote.
- Excerpt: "reconsider Student 3"

### Episode 37

- Diagnosis line: `18831`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `vote_switch`, `compromise_language`, `invalid_action`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `6` / `5` / `3`
- Waits/wait_for: `2` / `3`
- Format error rate: `0.33`
- Confidence: `medium`
- Rationale: Prof_1 moved from Student 3 to Student 2 with explicit concessionary language to secure a selection.
- Excerpt: "I will vote for Student 2 to ensure we make a selection"

### Episode 38

- Diagnosis line: `19500`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `placeholder_output`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `15` / `17` / `2`
- Waits/wait_for: `1` / `14`
- Format error rate: `0.07`
- Confidence: `high`
- Rationale: The agents raised Students 2, 4, 3, and 1, but the discussion stayed as alternating shallow proposals without convergence.
- Excerpt: "I propose voting for Student 3"

### Episode 39

- Diagnosis line: `19754`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `counterproposal`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `7` / `5` / `2`
- Waits/wait_for: `1` / `4`
- Format error rate: `0.43`
- Confidence: `high`
- Rationale: Student 2 emerged after initial Student 3 and Student 1 signals, and prof_3 followed it with little deliberation.
- Excerpt: "Let me know your thoughts on Student 2"

### Episode 40

- Diagnosis line: `20307`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `prompt_leak`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `15` / `12` / `0`
- Waits/wait_for: `4` / `8`
- Format error rate: `0.33`
- Confidence: `medium`
- Rationale: Students 4 and 2 were compared for diverse strengths, but no valid votes or adaptation materialized.
- Excerpt: "explore the potential contributions of each"

### Episode 41

- Diagnosis line: `21217`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `invalid_action`, `format_error_light`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `19` / `18` / `8`
- Waits/wait_for: `4` / `14`
- Format error rate: `0.32`
- Confidence: `high`
- Rationale: The agents considered Students 0, 4, 2, and 3; prof_2 ultimately pivoted to Student 4 while preserving Student 3 as a secondary option.
- Excerpt: "Pivoting to Student 4 as the primary offer"

### Episode 42

- Diagnosis line: `22103`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `semantically_incoherent`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `19` / `18` / `4`
- Waits/wait_for: `3` / `15`
- Format error rate: `0.21`
- Confidence: `low`
- Rationale: The episode attempted explicit exchange-style offers around Students 0, 2, and 3, but the trades were often self-referential and did not close.
- Excerpt: "in exchange for prof_3's support"

### Episode 43

- Diagnosis line: `23256`
- Category: `coordination_theater`
- Tags: `consensus_no`, `candidate_comparison`, `repeated_proposal`, `preference_probe`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `23` / `18` / `1`
- Waits/wait_for: `3` / `19`
- Format error rate: `0.13`
- Confidence: `high`
- Rationale: The agents repeatedly called for collaborative discussion of Student 2 and Student 1 without substantive new information or follow-through.
- Excerpt: "collaborative discussion where Student 2"

### Episode 44

- Diagnosis line: `23633`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `10` / `6` / `4`
- Waits/wait_for: `2` / `9`
- Format error rate: `0.30`
- Confidence: `medium`
- Rationale: Students 4, 1, 3, and 0 were mentioned, but the eventual Student 0 consensus came from shallow voting rather than bargaining.
- Excerpt: "keep Student 4 in consideration"

### Episode 45

- Diagnosis line: `24029`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `vote_switch`, `compromise_language`, `format_error_light`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `11` / `9` / `3`
- Waits/wait_for: `4` / `7`
- Format error rate: `0.27`
- Confidence: `high`
- Rationale: Prof_1 preferred Student 4 but acknowledged Student 3 might align with prof_2, then voted Student 3 for consensus.
- Excerpt: "if Student 3 is the more aligned"

### Episode 46

- Diagnosis line: `24146`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `4` / `2` / `2`
- Waits/wait_for: `1` / `4`
- Format error rate: `0.25`
- Confidence: `high`
- Rationale: Student 2 was proposed and immediately supported by prof_1, with no substantive deliberation.
- Excerpt: "I propose student 2"

### Episode 47

- Diagnosis line: `27471`
- Category: `stalled_waiting_loop`
- Tags: `consensus_yes`, `chosen_suboptimal`, `repeated_proposal`, `candidate_comparison`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `47` / `44` / `4`
- Waits/wait_for: `3` / `44`
- Format error rate: `0.02`
- Confidence: `high`
- Rationale: The episode spent 47 turns in repeated wait-for/proposal loops around Students 0, 1, and 2 before two votes finally settled on Student 2.
- Excerpt: "Proposal: Student 0"

### Episode 48

- Diagnosis line: `27953`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `12` / `11` / `4`
- Waits/wait_for: `2` / `9`
- Format error rate: `0.17`
- Confidence: `medium`
- Rationale: Students 0, 2, and 4 were discussed, with prof_2 continuing to advocate Student 4 while others coordinated on Student 2.
- Excerpt: "Student 2 vs. Student 4"

### Episode 49

- Diagnosis line: `29028`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `preference_probe`, `repeated_proposal`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `24` / `18` / `4`
- Waits/wait_for: `7` / `18`
- Format error rate: `0.33`
- Confidence: `high`
- Rationale: Most public messages asked others to share preferences or confirm consensus before a late Student 2 vote.
- Excerpt: "Please share your preference"

### Episode 50

- Diagnosis line: `30192`
- Category: `coordination_theater`
- Tags: `consensus_no`, `preference_probe`, `candidate_comparison`, `repeated_proposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `23` / `20` / `1`
- Waits/wait_for: `1` / `21`
- Format error rate: `0.04`
- Confidence: `high`
- Rationale: The episode repeatedly asked for preferences and preliminary votes while circling Student 1 and Student 0 without reaching consensus.
- Excerpt: "Student 0 as a potential compromise"

### Episode 51

- Diagnosis line: `30377`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `compromise_language`, `vote_switch`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `6` / `3` / `2`
- Waits/wait_for: `1` / `6`
- Format error rate: `0.33`
- Confidence: `high`
- Rationale: Prof_1 conceded from valuing Student 2 to voting Student 4, and prof_3 followed, but the exchange was mainly endorsement.
- Excerpt: "While I value Student 2's higher utility"

### Episode 52

- Diagnosis line: `30840`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `13` / `8` / `4`
- Waits/wait_for: `6` / `5`
- Format error rate: `0.38`
- Confidence: `medium`
- Rationale: Students 2, 3, and 0 were proposed in short, disconnected turns, producing no consensus.
- Excerpt: "I propose an alternative choice: Student 0"

### Episode 53

- Diagnosis line: `31033`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `counterproposal`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `6` / `2` / `4`
- Waits/wait_for: `1` / `2`
- Format error rate: `0.17`
- Confidence: `high`
- Rationale: Prof_2 first voted Student 2, then followed the Student 3 direction after prof_3 and prof_1 aligned there.
- Excerpt: "vote for Student 3 to show support"

### Episode 54

- Diagnosis line: `31220`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `counterproposal`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `6` / `4` / `3`
- Waits/wait_for: `2` / `3`
- Format error rate: `0.33`
- Confidence: `high`
- Rationale: After a brief Student 4 vote, prof_1 proposed Student 2 and prof_2 followed with a vote.
- Excerpt: "Let's vote for Student 2"

### Episode 55

- Diagnosis line: `32046`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `placeholder_output`, `format_error_light`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `18` / `19` / `7`
- Waits/wait_for: `4` / `12`
- Format error rate: `0.22`
- Confidence: `high`
- Rationale: Prof_1 pressed Student 2, prof_3 pressed Student 0, and prof_1 ultimately switched to Student 0 to avoid no consensus.
- Excerpt: "proceeding with Student 0 seems more strategic"

### Episode 56

- Diagnosis line: `32729`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `17` / `10` / `3`
- Waits/wait_for: `1` / `15`
- Format error rate: `0.12`
- Confidence: `medium`
- Rationale: Student 4 and Student 2 were actively contrasted, with fallback language and final votes converging on Student 2.
- Excerpt: "If that fails, I can still fall back on Student 2"

### Episode 57

- Diagnosis line: `34307`
- Category: `stalled_waiting_loop`
- Tags: `consensus_yes`, `chosen_social_optimum`, `preference_probe`, `repeated_proposal`, `prompt_leak`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `30` / `25` / `3`
- Waits/wait_for: `8` / `21`
- Format error rate: `0.27`
- Confidence: `high`
- Rationale: Vote-tally checking and waiting for prof_2 dominated a long episode before Student 2 consensus finally emerged.
- Excerpt: "Waiting for Prof_2's vote"

### Episode 58

- Diagnosis line: `34909`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `15` / `13` / `2`
- Waits/wait_for: `4` / `10`
- Format error rate: `0.27`
- Confidence: `medium`
- Rationale: Student 0 and Student 2 were compared repeatedly, including an attempt to frame Student 0 as complementing Student 2.
- Excerpt: "Student 0 has gained some traction"

### Episode 59

- Diagnosis line: `35559`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `repeated_proposal`, `candidate_comparison`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `16` / `15` / `2`
- Waits/wait_for: `4` / `12`
- Format error rate: `0.19`
- Confidence: `medium`
- Rationale: Student 2 became focal early and prof_2 eventually endorsed the existing support. Student 4 was mentioned, but the public exchange mostly repeated support rather than bargaining.
- Excerpt: "strong support for Student 2"

### Episode 60

- Diagnosis line: `35622`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `invalid_action`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `2` / `2`
- Waits/wait_for: `0` / `2`
- Format error rate: `0.00`
- Confidence: `high`
- Rationale: Two agents voted for Student 2 almost immediately, with no public deliberation and one invalid wait target.
- Excerpt: "Vote for Student 2"

### Episode 61

- Diagnosis line: `35922`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `8` / `8` / `5`
- Waits/wait_for: `4` / `4`
- Format error rate: `0.50`
- Confidence: `medium`
- Rationale: The agents named Students 0, 1, and 4 and gave brief utility-style reasons, but the discussion never developed into a coherent tradeoff.
- Excerpt: "Student 1 might be the best choice"

### Episode 62

- Diagnosis line: `36568`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `invalid_action`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `15` / `12` / `4`
- Waits/wait_for: `3` / `11`
- Format error rate: `0.27`
- Confidence: `medium`
- Rationale: Students 0, 2, and 4 were actively contested, and agents tried to move each other between Student 2 and Student 4. The negotiation did not converge, but it had real counterproposals and compromise framing.
- Excerpt: "move Student 2 to Student 0"

### Episode 63

- Diagnosis line: `38092`
- Category: `coordination_theater`
- Tags: `consensus_no`, `preference_probe`, `repeated_proposal`, `compromise_language`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `28` / `28` / `7`
- Waits/wait_for: `4` / `18`
- Format error rate: `0.18`
- Confidence: `medium`
- Rationale: The public conversation repeatedly asked others to reconfirm support for Student 2 while prof_3 floated Student 3 as a compromise. The episode became process talk and repeated proposals rather than effective bargaining.
- Excerpt: "Reconfirm if Prof_2 still supports Student 2"

### Episode 64

- Diagnosis line: `38958`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `20` / `20` / `1`
- Waits/wait_for: `6` / `12`
- Format error rate: `0.30`
- Confidence: `medium`
- Rationale: The agents discussed Students 0, 2, and 3, acknowledged another professor's preference, and showed willingness to keep searching for a path. It remained messy and inconclusive, but the public actions were closer to bargaining than simple endorsement.
- Excerpt: "I understand Prof. 2's preference for Student 2"

### Episode 65

- Diagnosis line: `39423`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `compromise_language`, `repeated_proposal`, `invalid_action`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `12` / `9` / `3`
- Waits/wait_for: `0` / `13`
- Format error rate: `0.08`
- Confidence: `medium`
- Rationale: Prof_2 made Student 2 focal and repeated votes; prof_3 followed while prof_1 continued mentioning Student 0. The compromise language was present, but the outcome was mainly endorsement of one proposal.
- Excerpt: "cast a vote for Student 2 to avoid a deadlock"

### Episode 66

- Diagnosis line: `39812`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `repeated_proposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `12` / `6` / `2`
- Waits/wait_for: `4` / `6`
- Format error rate: `0.25`
- Confidence: `high`
- Rationale: Prof_3 proposed Student 2, repeated a short rationale, and prof_1 eventually followed. There was little public comparison beyond Student 0 being mentioned as a personal fit.
- Excerpt: "I like how Student 2 stacks up"

### Episode 67

- Diagnosis line: `40037`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `prompt_leak`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `7` / `3` / `4`
- Waits/wait_for: `2` / `7`
- Format error rate: `0.29`
- Confidence: `medium`
- Rationale: Student 2 was proposed and voted through with minimal discussion. A malformed output copied prior conversation, but the behavioral pattern is still quick convergence.
- Excerpt: "Student 2 is receiving strong support"

### Episode 68

- Diagnosis line: `40156`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `4` / `0` / `3`
- Waits/wait_for: `2` / `1`
- Format error rate: `0.25`
- Confidence: `high`
- Rationale: The episode consisted almost entirely of immediate votes and waits, with no candidate discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Episode 69

- Diagnosis line: `40412`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `8` / `4` / `3`
- Waits/wait_for: `1` / `6`
- Format error rate: `0.25`
- Confidence: `high`
- Rationale: Student 2 was proposed and received votes quickly, with only brief support-seeking messages.
- Excerpt: "Vote for Student 2"

### Episode 70

- Diagnosis line: `41007`
- Category: `coordination_theater`
- Tags: `consensus_no`, `preference_probe`, `candidate_comparison`, `format_error_heavy`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `15` / `10` / `5`
- Waits/wait_for: `8` / `5`
- Format error rate: `0.53`
- Confidence: `medium`
- Rationale: Agents repeatedly asked for more information about Students 2 and 4 but did not exchange useful evaluations or move toward a decision.
- Excerpt: "provide more insight into Student 2 and Student 4"

### Episode 71

- Diagnosis line: `41698`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `vote_switch`, `repeated_proposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `15` / `15` / `11`
- Waits/wait_for: `1` / `11`
- Format error rate: `0.20`
- Confidence: `medium`
- Rationale: Prof_1 initially pushed Student 3 while others favored Student 2, then public messages tried to keep both in play and the vote moved toward Student 2. The reasoning was repetitive but included actual adaptation.
- Excerpt: "propose Student 3 and potentially Student 2"

### Episode 72

- Diagnosis line: `41879`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `6` / `6` / `2`
- Waits/wait_for: `2` / `3`
- Format error rate: `0.33`
- Confidence: `medium`
- Rationale: After brief mentions of Students 3 and 4, prof_3 proposed Student 2 and prof_2 followed. The public discussion was shallow and mainly converged behind the proposal.
- Excerpt: "I propose voting for Student 2"

### Episode 73

- Diagnosis line: `42552`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_social_optimum`, `repeated_proposal`, `preference_probe`, `malformed_tags`, `format_error_light`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `17` / `13` / `4`
- Waits/wait_for: `6` / `9`
- Format error rate: `0.47`
- Confidence: `medium`
- Rationale: Student 0 was repeatedly proposed, but much of the episode was waiting for prof_1 or prof_2 to state a position. Consensus came only after repeated process-oriented messages.
- Excerpt: "We need to see prof_1's stance"

### Episode 74

- Diagnosis line: `43891`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `preference_probe`, `repeated_proposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `28` / `20` / `0`
- Waits/wait_for: `6` / `21`
- Format error rate: `0.11`
- Confidence: `high`
- Rationale: The episode had no valid votes and was dominated by requests to gather input before deciding. Student 2 was mentioned repeatedly, but waiting prevented progress.
- Excerpt: "Let's gather more input"

### Episode 75

- Diagnosis line: `44113`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `7` / `4` / `4`
- Waits/wait_for: `4` / `2`
- Format error rate: `0.43`
- Confidence: `high`
- Rationale: The group considered Student 2 and Student 4, then prof_2 and prof_3 framed Student 3 as a balanced alternative. Prof_1 switched to Student 3 after the counterproposal.
- Excerpt: "Would you consider changing your votes"

### Episode 76

- Diagnosis line: `45249`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `preference_probe`, `private_reasoning_only`, `repeated_proposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `25` / `22` / `0`
- Waits/wait_for: `3` / `20`
- Format error rate: `0.16`
- Confidence: `high`
- Rationale: The agents repeatedly asked for initial thoughts and waited for prof_1, producing no votes. Candidate preferences stayed vague and the loop consumed the episode.
- Excerpt: "What are your initial thoughts"

### Episode 77

- Diagnosis line: `45966`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `preference_probe`, `repeated_proposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `18` / `13` / `2`
- Waits/wait_for: `6` / `12`
- Format error rate: `0.28`
- Confidence: `medium`
- Rationale: Students 2, 3, and 4 were discussed in shallow terms, with repeated statements about possible strengths. The episode reached consensus, but not through concrete bargaining.
- Excerpt: "weigh the pros and cons of Student 3 against Student 2"

### Episode 78

- Diagnosis line: `46413`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `12` / `11` / `5`
- Waits/wait_for: `9` / `1`
- Format error rate: `0.75`
- Confidence: `medium`
- Rationale: The agents mentioned Students 0, 1, and 2 and kept Student 2 as an aside, but the exchange stayed shallow and repetitive. Consensus on Student 0 emerged without a clear compromise.
- Excerpt: "Student 0 is a strong choice"

### Episode 79

- Diagnosis line: `47365`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `19` / `19` / `5`
- Waits/wait_for: `2` / `16`
- Format error rate: `0.11`
- Confidence: `medium`
- Rationale: Several candidates were proposed, especially Students 2 and 3, but the agents mostly repeated their own candidate claims. There was little effective response to the competing proposals.
- Excerpt: "Picking Student 2 looks like the best middle ground"

### Episode 80

- Diagnosis line: `47880`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `12` / `17` / `5`
- Waits/wait_for: `3` / `10`
- Format error rate: `0.42`
- Confidence: `medium`
- Rationale: Initial votes split across Students 0 and 2, then Student 3 was proposed as an alternative that might appeal across preferences. Prof_1 switched to Student 3, producing consensus.
- Excerpt: "Suggesting an alternative to Student 0"

### Episode 81

- Diagnosis line: `48844`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `compromise_language`, `repeated_proposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `21` / `21` / `0`
- Waits/wait_for: `2` / `20`
- Format error rate: `0.19`
- Confidence: `medium`
- Rationale: The episode repeatedly contrasted Students 1 and 4 and tried to frame their combined strengths as a bridge. It failed to converge, but the public behavior was aimed at reconciling different preferences.
- Excerpt: "both Student 4 and Student 1 have strong utilities"

### Episode 82

- Diagnosis line: `49252`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `11` / `7` / `7`
- Waits/wait_for: `2` / `9`
- Format error rate: `0.27`
- Confidence: `medium`
- Rationale: Student 1, Student 2, and Student 3 were all put forward, and prof_3 explicitly proposed Student 1 alongside Student 2 to bridge preferences. The final votes moved toward Student 1.
- Excerpt: "propose Student 1 alongside Student 2"

### Episode 83

- Diagnosis line: `49443`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `malformed_tags`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `6` / `3` / `4`
- Waits/wait_for: `2` / `4`
- Format error rate: `0.33`
- Confidence: `medium`
- Rationale: The professors cast different votes and gave shallow fit rationales for Students 2, 3, and 4. There was no clear bargaining or convergence.
- Excerpt: "Proposing Student 3 might appeal"

### Episode 84

- Diagnosis line: `50036`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `repeated_proposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `14` / `13` / `6`
- Waits/wait_for: `3` / `8`
- Format error rate: `0.21`
- Confidence: `medium`
- Rationale: Student 4 was strongly advocated, while Students 1 and 2 were raised as alternatives, including Student 2 as a possible compromise around a key voter. The episode did not converge, but it contained meaningful counterproposal structure.
- Excerpt: "Student 2 might be a good compromise"

### Episode 85

- Diagnosis line: `50335`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `9` / `6` / `2`
- Waits/wait_for: `4` / `5`
- Format error rate: `0.44`
- Confidence: `medium`
- Rationale: Student 2 became the clear focus after initial waits, and prof_2 accepted that Student 2 stood out. Student 0 was mentioned only as a balancing aside.
- Excerpt: "Student 2 stands out"

### Episode 86

- Diagnosis line: `50716`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `format_error_heavy`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `10` / `11` / `5`
- Waits/wait_for: `3` / `6`
- Format error rate: `0.50`
- Confidence: `low`
- Rationale: Students 0, 1, and 3 were discussed with some middle-ground language, but the episode remained fragmented and did not show effective adaptation.
- Excerpt: "Student 3 is already the compromise proposal"

### Episode 87

- Diagnosis line: `51374`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `repeated_proposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `15` / `15` / `4`
- Waits/wait_for: `6` / `5`
- Format error rate: `0.47`
- Confidence: `medium`
- Rationale: The public exchange was a repetitive conflict between Student 1 and Student 2. It listed utility-style reasons but never developed into compromise.
- Excerpt: "keep attempting to move forward with consensus on Student 1"

### Episode 88

- Diagnosis line: `51499`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `4` / `2` / `3`
- Waits/wait_for: `0` / `4`
- Format error rate: `0.00`
- Confidence: `high`
- Rationale: Prof_3 proposed Student 3 and prof_2 explicitly followed that selection. There was almost no deliberation.
- Excerpt: "as Prof. prof_3 has selected them"

### Episode 89

- Diagnosis line: `51946`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `prompt_leak`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `12` / `9` / `4`
- Waits/wait_for: `4` / `7`
- Format error rate: `0.25`
- Confidence: `medium`
- Rationale: Student 2, Student 4, and Student 0 were all mentioned, with some fallback language, but the discussion stayed shallow. A script-like prompt leak appeared in one output.
- Excerpt: "start with Student 2 and propose Student 4"

### Episode 90

- Diagnosis line: `52099`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `5` / `4` / `2`
- Waits/wait_for: `0` / `4`
- Format error rate: `0.00`
- Confidence: `medium`
- Rationale: Prof_3 voted for Student 4 and prof_2 followed with Student 4 as the fallback route. The preceding messages were mostly process-oriented.
- Excerpt: "offer Student 4 if no consensus is reached"

### Episode 91

- Diagnosis line: `52187`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `2` / `1`
- Format error rate: `0.67`
- Confidence: `high`
- Rationale: Two votes for Student 2 arrived within three turns, with no public discussion.
- Excerpt: "<VOTE>2</VOTE>"

### Episode 92

- Diagnosis line: `52750`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `14` / `17` / `9`
- Waits/wait_for: `7` / `5`
- Format error rate: `0.64`
- Confidence: `medium`
- Rationale: Student 1 had strong backing, but the group discussed Student 2 as a balancing choice and eventually voted for Student 2. The exchange explicitly tried to respect competing preferences.
- Excerpt: "Student 1 offers strong utility, while Student 2"

### Episode 93

- Diagnosis line: `53014`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `candidate_comparison`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `8` / `7` / `2`
- Waits/wait_for: `3` / `3`
- Format error rate: `0.38`
- Confidence: `medium`
- Rationale: Student 2 was introduced, justified, and then endorsed by prof_2. Other candidates were barely engaged publicly.
- Excerpt: "Voting for Student 2"

### Episode 94

- Diagnosis line: `53739`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `repeated_proposal`, `preference_probe`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `19` / `14` / `2`
- Waits/wait_for: `2` / `11`
- Format error rate: `0.16`
- Confidence: `medium`
- Rationale: Prof_2 repeatedly proposed Student 0 while waiting for others, but the actionable consensus came from a late Student 2 proposal. The dominant behavior was repeated setup and waiting for input.
- Excerpt: "share their thoughts first"

### Episode 95

- Diagnosis line: `55439`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `repeated_proposal`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `32` / `28` / `3`
- Waits/wait_for: `7` / `8`
- Format error rate: `0.22`
- Confidence: `medium`
- Rationale: The episode was very long and dominated by prof_3 repeating Student 0 and then Student 2 proposals. Consensus emerged after repetition, not deliberation.
- Excerpt: "Proposing Student 2 to keep an open mind"

### Episode 96

- Diagnosis line: `55531`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `2` / `2`
- Waits/wait_for: `0` / `3`
- Format error rate: `0.33`
- Confidence: `high`
- Rationale: Within three turns, two professors voted for Student 2 after a brief prompt to gauge Student 3. No meaningful deliberation occurred.
- Excerpt: "vote for Student 2 immediately"

### Episode 97

- Diagnosis line: `57898`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `preference_probe`, `repeated_proposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `38` / `33` / `0`
- Waits/wait_for: `2` / `36`
- Format error rate: `0.05`
- Confidence: `high`
- Rationale: The episode repeatedly checked whether others supported Student 2 but never produced a valid vote. Waiting and preference-probing dominated all 38 turns.
- Excerpt: "Checking prof_1's position on Student 2"

### Episode 98

- Diagnosis line: `58151`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `repeated_proposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `8` / `5` / `2`
- Waits/wait_for: `1` / `8`
- Format error rate: `0.25`
- Confidence: `high`
- Rationale: Student 0 was proposed early, and the later votes simply followed that focal proposal after waiting.
- Excerpt: "Proposing Student 0"

### Episode 99

- Diagnosis line: `58385`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `format_error_light`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `7` / `8` / `2`
- Waits/wait_for: `1` / `4`
- Format error rate: `0.57`
- Confidence: `medium`
- Rationale: Students 0 and 4 were compared and Student 4 was floated as a counterproposal, but the final behavior stayed with Student 0. The public exchange was more listing than bargaining.
- Excerpt: "Proposal: Student 0 and Student 4"

### Episode 100

- Diagnosis line: `58527`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `5` / `3` / `2`
- Waits/wait_for: `5` / `0`
- Format error rate: `0.80`
- Confidence: `high`
- Rationale: Student 0 was proposed and voted through within five turns, with no substantive comparison.
- Excerpt: "Let's vote for Student 0"

### Episode 101

- Diagnosis line: `58724`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `6` / `6` / `3`
- Waits/wait_for: `2` / `0`
- Format error rate: `0.33`
- Confidence: `medium`
- Rationale: The episode started with votes or support for Students 0 and 4, then Student 2 was advanced as an interdisciplinary option and prof_1 switched to it.
- Excerpt: "I will propose Student 2"

### Episode 102

- Diagnosis line: `59417`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `preference_probe`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `16` / `15` / `1`
- Waits/wait_for: `1` / `15`
- Format error rate: `0.12`
- Confidence: `medium`
- Rationale: Prof_1 initially voted Student 3, while prof_2 and prof_3 probed and argued for Student 2. The discussion directly asked for reasons and weighed Student 3 against Student 2.
- Excerpt: "Could you share your perspective on why Student 2"

### Episode 103

- Diagnosis line: `59860`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `format_error_heavy`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `11` / `11` / `9`
- Waits/wait_for: `3` / `2`
- Format error rate: `0.64`
- Confidence: `low`
- Rationale: The agents raised Students 0, 1, and 2 with short rationales, but malformed and repetitive outputs prevented coherent bargaining.
- Excerpt: "keep the door open for Student 1"

### Episode 104

- Diagnosis line: `60274`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `11` / `11` / `6`
- Waits/wait_for: `4` / `7`
- Format error rate: `0.45`
- Confidence: `medium`
- Rationale: The agents debated Student 2 against Students 1 and 3 and explicitly discussed alliance or plan-B options. Consensus on Student 2 emerged despite competing votes.
- Excerpt: "keep Student 2 but offer an alliance"

### Episode 105

- Diagnosis line: `61386`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `preference_probe`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `22` / `20` / `1`
- Waits/wait_for: `2` / `20`
- Format error rate: `0.09`
- Confidence: `high`
- Rationale: Students 2, 3, and 4 were contested over many turns, with prof_2 standing by Student 4 while acknowledging Student 3 as potentially acceptable. The episode was inconclusive but genuinely negotiation-like.
- Excerpt: "there might be room for"

### Episode 106

- Diagnosis line: `61661`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `vote_switch`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `8` / `8` / `3`
- Waits/wait_for: `2` / `4`
- Format error rate: `0.25`
- Confidence: `medium`
- Rationale: The agents shifted from Student 4 and Student 1 toward Student 2, while prof_2 considered Student 3 if Student 2 did not fit. It showed adaptation but did not reach consensus.
- Excerpt: "re-evaluating my preference for Student 3"

### Episode 107

- Diagnosis line: `61858`
- Category: `execution_breakdown`
- Tags: `consensus_no`, `format_error_heavy`, `malformed_tags`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `6` / `2` / `5`
- Waits/wait_for: `4` / `2`
- Format error rate: `0.67`
- Confidence: `medium`
- Rationale: The episode was mostly sparse votes, malformed multiple-vote behavior, and waits, leaving too little coherent public discussion to classify the interaction style normally.
- Excerpt: "Let's see how the group is leaning"

### Episode 108

- Diagnosis line: `62274`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `11` / `9` / `4`
- Waits/wait_for: `1` / `7`
- Format error rate: `0.09`
- Confidence: `medium`
- Rationale: Prof_1 began with Student 2, then publicly moved to Student 3 as an intermediary proposal after others signaled that direction. The final vote switch produced consensus.
- Excerpt: "consider it as an intermediary proposal"

### Episode 109

- Diagnosis line: `62854`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `preference_probe`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `14` / `13` / `1`
- Waits/wait_for: `2` / `11`
- Format error rate: `0.14`
- Confidence: `high`
- Rationale: The agents proposed Students 3, 1, 2, 4, and 0 and repeatedly framed alternatives as compromises. No consensus formed, but the public behavior was active bargaining over alternatives.
- Excerpt: "Student 0 as a potential compromise"

### Episode 110

- Diagnosis line: `63411`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `vote_switch`, `repeated_proposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `13` / `8` / `5`
- Waits/wait_for: `1` / `12`
- Format error rate: `0.08`
- Confidence: `medium`
- Rationale: Student 2 dominated the early conversation, then prof_3 voted Student 3 and prof_1 followed without much substantive explanation.
- Excerpt: "group is leaning towards Student 3"

### Episode 111

- Diagnosis line: `64964`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `repeated_proposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `27` / `27` / `3`
- Waits/wait_for: `2` / `26`
- Format error rate: `0.15`
- Confidence: `medium`
- Rationale: The agents repeatedly proposed Students 2, 0, and 1, but responses did not engage the competing reasons. It was candidate talk without effective compromise.
- Excerpt: "I propose Student 1 for discussion"

### Episode 112

- Diagnosis line: `65826`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `19` / `11` / `9`
- Waits/wait_for: `1` / `18`
- Format error rate: `0.11`
- Confidence: `medium`
- Rationale: Students 0, 2, and 4 were discussed, but each professor mostly repeated a preferred candidate. Consensus on Student 2 came from repeated voting rather than resolved tradeoffs.
- Excerpt: "explore why Student 4 could be advantageous"

### Episode 113

- Diagnosis line: `65919`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `2`
- Waits/wait_for: `1` / `1`
- Format error rate: `0.33`
- Confidence: `high`
- Rationale: Two votes for Student 2 occurred within three turns, with only a brief advocacy message between them.
- Excerpt: "see the value in Student 2"

### Episode 114

- Diagnosis line: `66510`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `compromise_language`, `preference_probe`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `16` / `11` / `0`
- Waits/wait_for: `0` / `14`
- Format error rate: `0.06`
- Confidence: `medium`
- Rationale: The episode compared Students 1 and 2 and framed them as a balanced pair that might satisfy different professors. It lacked votes, but the public reasoning tried to reconcile preferences.
- Excerpt: "Student 2 and Student 1 as a synergistic choice"

### Episode 115

- Diagnosis line: `66850`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `9` / `7` / `5`
- Waits/wait_for: `3` / `5`
- Format error rate: `0.33`
- Confidence: `high`
- Rationale: Student 4, Student 2, and Student 0 were all in play, and prof_3 switched from Student 2 to Student 0 as a complementary offer before prof_2 joined.
- Excerpt: "Voting for Student 0 to offer a complementary offer"

### Episode 116

- Diagnosis line: `67068`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `early_focal_candidate`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `7` / `6` / `3`
- Waits/wait_for: `3` / `1`
- Format error rate: `0.43`
- Confidence: `medium`
- Rationale: Prof_3 publicly favored Student 0 and prof_1 then supported Student 0 after a short strength-based rationale. Prof_2's Student 2 vote was not negotiated against.
- Excerpt: "Let's try supporting Student 0"

### Episode 117

- Diagnosis line: `67934`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `repeated_proposal`, `preference_probe`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `20` / `20` / `0`
- Waits/wait_for: `1` / `17`
- Format error rate: `0.05`
- Confidence: `high`
- Rationale: Agents repeatedly propose or ask about Student 3 while waiting for each other, including self-directed waits, and never cast a vote. The dominant behavior is a waiting loop rather than deliberation.
- Excerpt: "I propose presenting Student 3 as an additional option for review."

### Episode 118

- Diagnosis line: `68103`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `counterproposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `5` / `5` / `4`
- Waits/wait_for: `1` / `5`
- Format error rate: `0.40`
- Confidence: `medium`
- Rationale: Student 2 becomes focal after prof_1 votes for it, and prof_2 eventually follows with only a brief contingency for Student 3. The fallback language is thin and does not become real bargaining.
- Excerpt: "I propose supporting Student 2"

### Episode 119

- Diagnosis line: `68422`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `repeated_proposal`, `malformed_tags`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `10` / `10` / `2`
- Waits/wait_for: `3` / `6`
- Format error rate: `0.20`
- Confidence: `medium`
- Rationale: The episode centers on Student 2 with a few shallow statements about utility and strengths, then waits and malformed copied-history outputs. Consensus forms without meaningful tradeoff discussion.
- Excerpt: "Let's move forward and support Student 2."

### Episode 120

- Diagnosis line: `68760`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `repeated_proposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `9` / `9` / `5`
- Waits/wait_for: `1` / `7`
- Format error rate: `0.11`
- Confidence: `medium`
- Rationale: Several candidates are named, but the public turns mostly state votes or short preferences. Student 2 wins after simple following rather than a developed comparison.
- Excerpt: "Pick Student 2"

### Episode 121

- Diagnosis line: `72106`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `repeated_proposal`, `candidate_comparison`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `49` / `49` / `2`
- Waits/wait_for: `3` / `37`
- Format error rate: `0.08`
- Confidence: `high`
- Rationale: The long episode is a repetitive Student 4 versus Student 2 exchange, with little development beyond restating proposals. Final support for Student 2 arrives after repeated prompts rather than negotiation.
- Excerpt: "Propose Student 2 again"

### Episode 122

- Diagnosis line: `72908`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `19` / `19` / `3`
- Waits/wait_for: `3` / `11`
- Format error rate: `0.16`
- Confidence: `medium`
- Rationale: Professors argue for Student 0 and Student 4 and try to frame Student 0 around other professors' interests. The episode fails to reach consensus, but it contains real attempts to reconcile candidate strengths.
- Excerpt: "highlighting Student 4's strong alignment"

### Episode 123

- Diagnosis line: `73223`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `9` / `9` / `2`
- Waits/wait_for: `1` / `6`
- Format error rate: `0.11`
- Confidence: `medium`
- Rationale: Professors initially mention different students, then prof_3 and prof_1 converge on Student 2 with minimal rationale. The behavior is mostly vote following.
- Excerpt: "Vote for Student 2 and encourage others"

### Episode 124

- Diagnosis line: `74720`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `vote_switch`, `compromise_language`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `28` / `28` / `4`
- Waits/wait_for: `3` / `26`
- Format error rate: `0.04`
- Confidence: `medium`
- Rationale: The group cycles through Students 4, 2, and 1 with some balance language, but it remains shallow and does not resolve. Candidate mentions are present without effective bargaining.
- Excerpt: "If Student 2 ... does not win the vote, then Student 1 might be"

### Episode 125

- Diagnosis line: `77851`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `repeated_proposal`, `candidate_comparison`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `50` / `50` / `4`
- Waits/wait_for: `34` / `24`
- Format error rate: `0.18`
- Confidence: `high`
- Rationale: Waiting behavior dominates the episode, especially repeated waits for prof_2. Candidate mentions continue, but they do not move the group toward a decision.
- Excerpt: "Let's wait for their response."

### Episode 126

- Diagnosis line: `78623`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `compromise_language`, `prompt_leak`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `17` / `17` / `3`
- Waits/wait_for: `2` / `14`
- Format error rate: `0.24`
- Confidence: `medium`
- Rationale: Student 2 and Student 0 are discussed as possible group choices, with some middle-ground language. The responses remain repetitive and never become concrete bargaining.
- Excerpt: "Student 2 has strong utility ... but Student 0 is also a good middle ground."

### Episode 127

- Diagnosis line: `79602`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `21` / `21` / `4`
- Waits/wait_for: `4` / `20`
- Format error rate: `0.19`
- Confidence: `medium`
- Rationale: The agents weigh Student 4 against Student 0 as a quick-consensus compromise, and prof_3 ultimately switches to Student 4. This is a real, if messy, adaptation to group momentum.
- Excerpt: "choosing Student 4 for quick consensus, despite its slightly lower utility"

### Episode 128

- Diagnosis line: `79824`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `preference_probe`, `format_error_light`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `7` / `7` / `2`
- Waits/wait_for: `1` / `5`
- Format error rate: `0.14`
- Confidence: `medium`
- Rationale: Student 1 becomes focal after prof_3 votes for it, and prof_1 follows with a short utility rationale. There is little counterargument or bargaining.
- Excerpt: "Student 1 has the highest utility score"

### Episode 129

- Diagnosis line: `80018`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `6` / `6` / `3`
- Waits/wait_for: `3` / `1`
- Format error rate: `0.50`
- Confidence: `medium`
- Rationale: After scattered initial proposals, prof_3 votes for Student 2 and prof_2 follows. Heavy format errors are present, but the behavior is still interpretable as following.
- Excerpt: "Vote for Student 2 to gain votes"

### Episode 130

- Diagnosis line: `80291`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `preference_probe`, `candidate_comparison`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `8` / `8` / `3`
- Waits/wait_for: `2` / `7`
- Format error rate: `0.38`
- Confidence: `medium`
- Rationale: The agents mention general group strengths and several candidates, but decisions are mostly isolated votes. Student 2 wins after a shallow proposal rather than negotiation.
- Excerpt: "Student 2 as a consideration"

### Episode 131

- Diagnosis line: `80393`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `3` / `2`
- Waits/wait_for: `1` / `2`
- Format error rate: `0.67`
- Confidence: `high`
- Rationale: Two professors vote for Student 2 within three turns, while the only group rationale is a brief utility list. There is no deliberation.
- Excerpt: "I will propose Student 2"

### Episode 132

- Diagnosis line: `81455`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `compromise_language`, `vote_switch`, `counterproposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `20` / `20` / `9`
- Waits/wait_for: `2` / `19`
- Format error rate: `0.20`
- Confidence: `high`
- Rationale: The public discussion repeatedly frames Student 2 versus Student 3 with fallback and compromise language, and prof_1 eventually switches to Student 2. This is one of the clearer adaptation episodes.
- Excerpt: "support for Student 3 in case of needed flexibility"

### Episode 133

- Diagnosis line: `81610`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `5` / `5` / `2`
- Waits/wait_for: `1` / `4`
- Format error rate: `0.20`
- Confidence: `high`
- Rationale: Student 0 receives two votes within five turns after minimal discussion. The brief Student 2 proposal does not develop into negotiation.
- Excerpt: "Vote for Student 0"

### Episode 134

- Diagnosis line: `82115`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `candidate_comparison`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `14` / `14` / `3`
- Waits/wait_for: `2` / `8`
- Format error rate: `0.07`
- Confidence: `medium`
- Rationale: Student 2 becomes focal and later professors endorse it, despite a short Student 4 aside. The discussion is mostly endorsement of the focal candidate.
- Excerpt: "Voting for Student 2 aligns with the current momentum"

### Episode 135

- Diagnosis line: `83820`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `vote_switch`, `compromise_language`, `repeated_proposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `30` / `30` / `4`
- Waits/wait_for: `2` / `29`
- Format error rate: `0.07`
- Confidence: `medium`
- Rationale: The episode pits Student 2 against Student 4 for many turns, and prof_2 eventually changes to Student 2 for consensus. Much is repetitive, but there is visible adaptation.
- Excerpt: "I would like to propose Student 2"

### Episode 136

- Diagnosis line: `84727`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `preference_probe`, `compromise_language`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `21` / `21` / `4`
- Waits/wait_for: `7` / `14`
- Format error rate: `0.29`
- Confidence: `medium`
- Rationale: Professors ask for rationales for Student 2 and Student 4 and explicitly seek a middle ground. It does not converge, but the public behavior is close to negotiation.
- Excerpt: "share their rationales for their current votes"

### Episode 137

- Diagnosis line: `85030`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `preference_probe`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `9` / `9` / `4`
- Waits/wait_for: `2` / `6`
- Format error rate: `0.22`
- Confidence: `medium`
- Rationale: The episode starts with preference probes, but Student 3 is selected after prof_2 proposes it and prof_1 follows. There is little comparison.
- Excerpt: "Student 3 is the optimal choice"

### Episode 138

- Diagnosis line: `85269`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `8` / `8` / `2`
- Waits/wait_for: `2` / `6`
- Format error rate: `0.25`
- Confidence: `medium`
- Rationale: Prof_3 makes Student 2 focal, and prof_1 supports it. Prof_2's Student 1 preference is not meaningfully negotiated.
- Excerpt: "Support the selection of Student 2"

### Episode 139

- Diagnosis line: `85981`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `15` / `15` / `9`
- Waits/wait_for: `3` / `12`
- Format error rate: `0.27`
- Confidence: `high`
- Rationale: Agents consider Students 1, 2, and 0, with Student 0 and Student 2 treated as fallback or compromise options. Prof_1 eventually moves from Student 1 to Student 2.
- Excerpt: "Offering Student 2 could potentially align"

### Episode 140

- Diagnosis line: `86140`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `5` / `5` / `3`
- Waits/wait_for: `1` / `3`
- Format error rate: `0.20`
- Confidence: `medium`
- Rationale: Prof_1 initially votes Student 1, then follows prof_3 toward Student 2 after a short consensus rationale. The switch is not backed by much bargaining.
- Excerpt: "Voting for Student 2 could potentially create a clearer consensus"

### Episode 141

- Diagnosis line: `86447`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `compromise_language`, `vote_switch`, `candidate_comparison`, `format_error_light`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `9` / `9` / `4`
- Waits/wait_for: `3` / `6`
- Format error rate: `0.22`
- Confidence: `medium`
- Rationale: Student 4 is introduced as a compromise after Student 2 has support, and prof_2 then prof_1 vote for it. The public turns explicitly frame Student 4 as a consensus bridge.
- Excerpt: "Student 4 is the compromise we need"

### Episode 142

- Diagnosis line: `86872`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `compromise_language`, `counterproposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `12` / `12` / `2`
- Waits/wait_for: `2` / `10`
- Format error rate: `0.17`
- Confidence: `high`
- Rationale: Students 2 and 3 are explicitly integrated as competing preferences, and the group proposes voting for Student 2 while keeping Student 3 for future consensus. This is genuine compromise behavior.
- Excerpt: "integrate the preferences for Students 2 and 3"

### Episode 143

- Diagnosis line: `87510`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `compromise_language`, `preference_probe`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `15` / `15` / `3`
- Waits/wait_for: `3` / `11`
- Format error rate: `0.20`
- Confidence: `medium`
- Rationale: The group works around Student 0 versus Student 3 and tries to appeal to others through systems and HCI alignment. It lacks a final consensus but contains real persuasion attempts.
- Excerpt: "emphasize the systems and HCI alignment"

### Episode 144

- Diagnosis line: `88350`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `preference_probe`, `vote_switch`, `compromise_language`, `format_error_light`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `19` / `19` / `5`
- Waits/wait_for: `5` / `13`
- Format error rate: `0.16`
- Confidence: `high`
- Rationale: Professors compare Students 2, 4, and 0, probe concerns, and ultimately move toward Student 0 as a consensus candidate. This has actual response to competing preferences.
- Excerpt: "I propose Student 0 to maintain alignment"

### Episode 145

- Diagnosis line: `88658`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `9` / `9` / `4`
- Waits/wait_for: `4` / `3`
- Format error rate: `0.33`
- Confidence: `medium`
- Rationale: Students 0, 2, and 4 are mentioned with short rationales, but the votes scatter and no one effectively responds. It remains shallow candidate discussion.
- Excerpt: "Between students 0 and 4"

### Episode 146

- Diagnosis line: `88776`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `4` / `4` / `2`
- Waits/wait_for: `2` / `2`
- Format error rate: `0.50`
- Confidence: `medium`
- Rationale: Prof_3 votes for Student 2 and prof_1 follows despite prof_2 briefly proposing Student 4. The convergence is quick and mostly endorsement.
- Excerpt: "I will vote for Student 2 to align"

### Episode 147

- Diagnosis line: `89452`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `compromise_language`, `counterproposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `16` / `16` / `2`
- Waits/wait_for: `1` / `14`
- Format error rate: `0.19`
- Confidence: `high`
- Rationale: The discussion explicitly weighs Student 2 against Student 4 and proposes Student 4 as a secondary choice while building toward Student 2. The final vote follows this compromise path.
- Excerpt: "Student 2 first ... Student 4 as a secondary choice"

### Episode 148

- Diagnosis line: `89993`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `14` / `14` / `5`
- Waits/wait_for: `3` / `7`
- Format error rate: `0.14`
- Confidence: `medium`
- Rationale: Professors initially support Student 0, then prof_2 makes Student 4 focal and prof_3 follows. The shift is quick and not deeply reasoned.
- Excerpt: "Vote for Student 4"

### Episode 149

- Diagnosis line: `90260`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `8` / `8` / `3`
- Waits/wait_for: `3` / `3`
- Format error rate: `0.50`
- Confidence: `medium`
- Rationale: The episode mentions Students 1, 0, and 2, but public messages are mostly positioning and vote-tally talk. Heavy format errors also reduce interpretability.
- Excerpt: "Student 1 is a strong candidate"

### Episode 150

- Diagnosis line: `90743`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `12` / `12` / `5`
- Waits/wait_for: `1` / `9`
- Format error rate: `0.17`
- Confidence: `high`
- Rationale: Prof_2 makes a substantive case for Student 3 over Student 1, and prof_3 says they are persuaded and proposes compromise. It is one of the strongest negotiation-like no-consensus episodes.
- Excerpt: "I am persuaded by the high utility of Student 3"

### Episode 151

- Diagnosis line: `92480`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `repeated_proposal`, `candidate_comparison`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `31` / `31` / `5`
- Waits/wait_for: `5` / `25`
- Format error rate: `0.19`
- Confidence: `medium`
- Rationale: The long episode repeats Student 2 votes and Student 3 or 4 prompts without effective response. Consensus arrives through persistence rather than bargaining.
- Excerpt: "What are your thoughts on Student 3"

### Episode 152

- Diagnosis line: `93908`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `repeated_proposal`, `preference_probe`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `29` / `29` / `2`
- Waits/wait_for: `7` / `22`
- Format error rate: `0.21`
- Confidence: `high`
- Rationale: Most turns wait for others or ask for vote tallies, with repeated possible votes for Students 3 and 4. The waiting loop prevents progress.
- Excerpt: "Waiting for Prof. prof_1 and Prof. prof_3"

### Episode 153

- Diagnosis line: `94263`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `counterproposal`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `10` / `10` / `3`
- Waits/wait_for: `1` / `9`
- Format error rate: `0.00`
- Confidence: `medium`
- Rationale: Student 0 is posed as the lead with fallbacks to Students 2 or 3, and prof_2 eventually votes for Student 0. The fallback language is not developed.
- Excerpt: "initial preference for Student 0 but keep open"

### Episode 154

- Diagnosis line: `96928`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `repeated_proposal`, `candidate_comparison`, `counterproposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `40` / `40` / `4`
- Waits/wait_for: `1` / `33`
- Format error rate: `0.10`
- Confidence: `medium`
- Rationale: The episode repeatedly cycles through Students 2, 3, and 4 with little change in positions. Public turns mention reconsideration but mostly restate proposals.
- Excerpt: "Encourage prof_3 to reconsider supporting Student 2"

### Episode 155

- Diagnosis line: `99067`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `repeated_proposal`, `candidate_comparison`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `34` / `34` / `8`
- Waits/wait_for: `4` / `25`
- Format error rate: `0.18`
- Confidence: `high`
- Rationale: Prof_1 repeatedly waits for prof_2 feedback on Student 3 while the others repeat Student 1 and Student 4 positions. The loop dominates and blocks resolution.
- Excerpt: "Will prof_2 provide feedback on Student 3?"

### Episode 156

- Diagnosis line: `99610`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `invalid_action`, `format_error_light`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `14` / `14` / `8`
- Waits/wait_for: `3` / `9`
- Format error rate: `0.14`
- Confidence: `medium`
- Rationale: Student 0 is proposed by prof_3 and then repeated by prof_2, producing consensus after some waiting and one invalid wait target. There is little substantive negotiation.
- Excerpt: "I propose student 0"

### Episode 157

- Diagnosis line: `101044`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `repeated_proposal`, `preference_probe`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `28` / `28` / `2`
- Waits/wait_for: `7` / `18`
- Format error rate: `0.18`
- Confidence: `high`
- Rationale: The episode becomes a self-referential loop around checking prof_1's stance on Student 0. It produces no real exchange.
- Excerpt: "continue checking prof_1's stance on Student 0"

### Episode 158

- Diagnosis line: `101135`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `3` / `3`
- Waits/wait_for: `1` / `2`
- Format error rate: `0.33`
- Confidence: `high`
- Rationale: Within three turns, two professors vote for Student 2 after a single proposal. No deliberation occurs.
- Excerpt: "I propose Student 2 as the top candidate"

### Episode 159

- Diagnosis line: `101222`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `3` / `2`
- Waits/wait_for: `2` / `0`
- Format error rate: `0.33`
- Confidence: `high`
- Rationale: Student 1 is proposed and receives two votes within three turns. The open-to-persuasion phrase never becomes discussion.
- Excerpt: "Let's vote for Student 1"

### Episode 160

- Diagnosis line: `101817`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `vote_switch`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `14` / `14` / `3`
- Waits/wait_for: `1` / `13`
- Format error rate: `0.14`
- Confidence: `medium`
- Rationale: Student 3 and Student 2 are compared, and prof_3 shifts from voting Student 3 to supporting Student 2 after repeated arguments about Student 2's strengths. No consensus follows, but adaptation is visible.
- Excerpt: "Student 2's exceptional skills"

### Episode 161

- Diagnosis line: `101916`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `3` / `3`
- Waits/wait_for: `2` / `0`
- Format error rate: `0.67`
- Confidence: `high`
- Rationale: Two professors vote for Student 2 in a three-turn episode with no meaningful discussion. Format errors are heavy but not outcome-defining.
- Excerpt: "propose Student 2 as my initial vote"

### Episode 162

- Diagnosis line: `102172`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `8` / `8` / `2`
- Waits/wait_for: `4` / `2`
- Format error rate: `0.50`
- Confidence: `medium`
- Rationale: Student 2 becomes focal and receives the necessary votes after brief generic support. Heavy format errors accompany otherwise simple endorsement.
- Excerpt: "go with Student 2 for the initial vote"

### Episode 163

- Diagnosis line: `102638`
- Category: `negotiation_like`
- Tags: `consensus_no`, `candidate_comparison`, `counterproposal`, `compromise_language`, `invalid_action`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `12` / `12` / `2`
- Waits/wait_for: `2` / `10`
- Format error rate: `0.17`
- Confidence: `high`
- Rationale: The group discusses Students 0 and 2 as different priority profiles, with Student 2 explicitly framed as a compromise. This is meaningful negotiation even without consensus.
- Excerpt: "Student 2 is a strategic compromise"

### Episode 164

- Diagnosis line: `102762`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `4` / `4` / `2`
- Waits/wait_for: `3` / `0`
- Format error rate: `0.75`
- Confidence: `high`
- Rationale: Student 0 receives immediate votes in four turns, while the initial malformed group message adds little. There is no real deliberation.
- Excerpt: "Vote for Student 0"

### Episode 165

- Diagnosis line: `103248`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `candidate_comparison`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `13` / `13` / `3`
- Waits/wait_for: `2` / `10`
- Format error rate: `0.15`
- Confidence: `medium`
- Rationale: Student 2 becomes focal after brief Student 4 discussion, and prof_2 follows it with a vote. The Student 4 option is acknowledged but not negotiated.
- Excerpt: "Let us first vote for Student 2"

### Episode 166

- Diagnosis line: `103466`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `7` / `7` / `3`
- Waits/wait_for: `4` / `1`
- Format error rate: `0.43`
- Confidence: `medium`
- Rationale: Student 2 and Student 4 are both proposed, and prof_1 moves from favoring Student 4 to voting Student 2 while keeping a possible revote open. This is a small but real adaptation.
- Excerpt: "open to revisiting the vote"

### Episode 167

- Diagnosis line: `104067`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `14` / `14` / `4`
- Waits/wait_for: `3` / `10`
- Format error rate: `0.21`
- Confidence: `high`
- Rationale: The public discussion weighs Students 2 and 3, describes Student 3 as a balanced candidate, and ends with prof_1 returning to Student 3. It contains counterproposal and vote movement.
- Excerpt: "Student 3 ... balanced and diverse"

### Episode 168

- Diagnosis line: `105518`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `repeated_proposal`, `candidate_comparison`, `invalid_action`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `29` / `29` / `1`
- Waits/wait_for: `2` / `26`
- Format error rate: `0.07`
- Confidence: `medium`
- Rationale: The episode has real Student 2 versus Student 3 disagreement late, but most turns are repeated waits for prof_2 or prof_3. The waiting loop dominates the failure to converge.
- Excerpt: "Let's see if Student 3 can secure support"

### Episode 169

- Diagnosis line: `105853`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `prompt_leak`, `malformed_tags`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `9` / `9` / `3`
- Waits/wait_for: `8` / `1`
- Format error rate: `0.89`
- Confidence: `low`
- Rationale: The episode is heavily malformed and includes copied history, but enough public text remains to see shallow discussion around Students 0, 1, and 2. It does not cleanly become negotiation.
- Excerpt: "I propose discussing student 0 first."

### Episode 170

- Diagnosis line: `106471`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `15` / `15` / `5`
- Waits/wait_for: `1` / `7`
- Format error rate: `0.13`
- Confidence: `high`
- Rationale: Student 0 and Student 2 are treated as a compromise pair, and prof_3 explicitly adjusts toward that compromise after preferring Student 2. The final votes choose Student 0.
- Excerpt: "students 0 and 2 as a viable compromise"

### Episode 171

- Diagnosis line: `106872`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `counterproposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `11` / `11` / `3`
- Waits/wait_for: `5` / `5`
- Format error rate: `0.45`
- Confidence: `medium`
- Rationale: Student 4 becomes focal after prof_3 votes for it, and prof_2 follows while mentioning Student 3 as a fallback. The discussion is mostly endorsement.
- Excerpt: "collectively vote for Student 4"

### Episode 172

- Diagnosis line: `107032`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `5` / `5` / `3`
- Waits/wait_for: `2` / `3`
- Format error rate: `0.40`
- Confidence: `medium`
- Rationale: Prof_3 proposes and votes Student 2, then prof_1 follows. The Student 3 vote from prof_2 is not meaningfully engaged.
- Excerpt: "Proposal: Student 2"

### Episode 173

- Diagnosis line: `107545`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `vote_switch`, `counterproposal`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `13` / `13` / `4`
- Waits/wait_for: `0` / `13`
- Format error rate: `0.00`
- Confidence: `medium`
- Rationale: The group initially splits between Student 2 and Student 3, then Student 2 is reconsidered with a strengths rationale and prof_1 switches to Student 2. This is modest but real adaptation.
- Excerpt: "reconsidering Student 2 is beneficial"

### Episode 174

- Diagnosis line: `107640`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `3` / `3` / `3`
- Waits/wait_for: `1` / `1`
- Format error rate: `0.33`
- Confidence: `high`
- Rationale: Student 1 receives two votes within three turns after one short proposal. There is no substantive negotiation.
- Excerpt: "Let's discuss student 1"

### Episode 175

- Diagnosis line: `108382`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `17` / `14` / `5`
- Waits/wait_for: `6` / `11`
- Format error rate: `0.29`
- Confidence: `medium`
- Rationale: Student 4, Student 2, and Student 1 are all raised, and prof_1 ultimately moves from advocating Student 4 to voting for Student 2 as a compromise around the emerging coalition.
- Excerpt: "I will vote for Student 2, and we can discuss Student 4 later"

### Episode 176

- Diagnosis line: `108687`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `repeated_proposal`, `format_error_light`, `malformed_tags`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `9` / `6` / `4`
- Waits/wait_for: `3` / `4`
- Format error rate: `0.44`
- Confidence: `medium`
- Rationale: Student 2 becomes focal after prof_3 proposes it, and prof_2 follows with a vote while prof_1 remains on Student 4. The discussion has candidate rationales but little bargaining.
- Excerpt: "Let's propose Student 2. We can discuss the appeal of Student 4 later."

### Episode 177

- Diagnosis line: `109016`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `9` / `7` / `4`
- Waits/wait_for: `1` / `7`
- Format error rate: `0.11`
- Confidence: `medium`
- Rationale: Several students are mentioned, but the public discussion mostly repeats combined Student 1/2 language and ends with two votes for Student 2 without real tradeoff resolution.
- Excerpt: "combine Student 1 and Student 2 into a single proposal"

### Episode 178

- Diagnosis line: `109712`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `repeated_proposal`, `format_error_light`, `malformed_tags`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `17` / `13` / `7`
- Waits/wait_for: `6` / `8`
- Format error rate: `0.41`
- Confidence: `high`
- Rationale: prof_1 repeatedly asks others to confirm they can see the vectors and vote situation while prof_2 keeps voting Student 2. Public coordination talk dominates over useful negotiation.
- Excerpt: "confirm that they are seeing and evaluating the ability vectors"

### Episode 179

- Diagnosis line: `110422`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `format_error_light`, `malformed_tags`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `18` / `20` / `2`
- Waits/wait_for: `3` / `11`
- Format error rate: `0.28`
- Confidence: `medium`
- Rationale: Student 1 and Student 2 are discussed as alternatives, with backup and coalition language before prof_3 and prof_1 converge on Student 1. It is repetitive but includes some effort to manage competing support.
- Excerpt: "Student 2 is also a strong contender"

### Episode 180

- Diagnosis line: `112518`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `vote_switch`, `format_error_light`, `malformed_tags`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `32` / `30` / `9`
- Waits/wait_for: `1` / `26`
- Format error rate: `0.06`
- Confidence: `medium`
- Rationale: The episode cycles through Students 0, 2, 3, and 4 with repeated proposals. prof_2 eventually supports Student 0, but the path is repetitive candidate advocacy rather than developed bargaining.
- Excerpt: "Student 0 seems to be the clear choice given the strong backing from prof_1"

### Episode 181

- Diagnosis line: `112639`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `4` / `3` / `2`
- Waits/wait_for: `3` / `1`
- Format error rate: `0.50`
- Confidence: `high`
- Rationale: prof_2 proposes Student 1 and prof_1 immediately supports that choice to avoid splitting the vote. There is almost no deliberation beyond endorsement.
- Excerpt: "Supporting prof_2 by recommending Student 1"

### Episode 182

- Diagnosis line: `113490`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `preference_probe`, `format_error_light`, `malformed_tags`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `19` / `18` / `2`
- Waits/wait_for: `3` / `13`
- Format error rate: `0.16`
- Confidence: `high`
- Rationale: The agents repeatedly ask whose proposal to discuss first and wait for each other. Student 0 and Student 2 are named, but the public behavior is mainly process management.
- Excerpt: "Would you like to discuss Student 2 or consider Student 0's proposal first?"

### Episode 183

- Diagnosis line: `114229`
- Category: `negotiation_like`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `compromise_language`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `17` / `17` / `2`
- Waits/wait_for: `3` / `13`
- Format error rate: `0.18`
- Confidence: `high`
- Rationale: The group considers Students 0, 2, 3, and 4, with explicit fallback and balance language around Student 4. It fails to reach consensus, but the public exchange is negotiation-like.
- Excerpt: "I'll propose Student 4 as a fallback"

### Episode 184

- Diagnosis line: `114292`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `social_optimum_unknown`, `early_focal_candidate`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `2` / `1` / `2`
- Waits/wait_for: `1` / `0`
- Format error rate: `0.50`
- Confidence: `high`
- Rationale: Two professors vote Student 2 in two turns before prof_3 ever acts. There is no public deliberation.
- Excerpt: "Let's see Prof_3's preference for Student 2"

### Episode 185

- Diagnosis line: `115414`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `preference_probe`, `repeated_proposal`, `format_error_light`, `malformed_tags`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `25` / `25` / `0`
- Waits/wait_for: `9` / `12`
- Format error rate: `0.40`
- Confidence: `high`
- Rationale: The episode repeatedly asks to review the vote situation for Student 2 and waits for responses. Waiting and status-checking prevent any substantive progress.
- Excerpt: "Let's review the most recent voting situation for Student 2"

### Episode 186

- Diagnosis line: `115624`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `7` / `5` / `2`
- Waits/wait_for: `0` / `4`
- Format error rate: `0.00`
- Confidence: `high`
- Rationale: prof_3 proposes Student 4, then prof_1 and prof_2 simply join that proposal. The consensus is endorsement, not bargaining.
- Excerpt: "Joining prof_3's proposal"

### Episode 187

- Diagnosis line: `116450`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `19` / `18` / `2`
- Waits/wait_for: `7` / `12`
- Format error rate: `0.32`
- Confidence: `medium`
- Rationale: Students 1, 2, and 0 are discussed with some comparisons, and Student 0 eventually wins. The public reasoning remains shallow and does not clearly reconcile preferences.
- Excerpt: "review Student 0's strengths and compare it with Student 1's potential"

### Episode 188

- Diagnosis line: `117836`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `28` / `22` / `3`
- Waits/wait_for: `5` / `23`
- Format error rate: `0.18`
- Confidence: `medium`
- Rationale: The agents mention Students 4, 3, 2, and 1, and prof_2 eventually moves to Student 3. The exchange is mostly repeated candidate advocacy and waiting, with limited actual bargaining.
- Excerpt: "Please consider Student 3. I will revise my vote accordingly."

### Episode 189

- Diagnosis line: `119550`
- Category: `coordination_theater`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `repeated_proposal`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `28` / `28` / `2`
- Waits/wait_for: `0` / `26`
- Format error rate: `0.00`
- Confidence: `medium`
- Rationale: The conversation repeats requests to discuss Student 2 or explain Student 0 without resolving the disagreement. Much of the public talk is about seeking discussion rather than making concrete tradeoffs.
- Excerpt: "Possibly vote for Student 2 and invite prof_1 to discuss"

### Episode 190

- Diagnosis line: `119644`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `format_error_heavy`, `invalid_action`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `3` / `2` / `3`
- Waits/wait_for: `2` / `1`
- Format error rate: `0.67`
- Confidence: `high`
- Rationale: Two of three agents vote Student 0 immediately, producing consensus in three turns. There is no meaningful deliberation.
- Excerpt: "Student 0 is a strong candidate"

### Episode 191

- Diagnosis line: `120873`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `repeated_proposal`, `format_error_light`, `prompt_leak`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `25` / `23` / `1`
- Waits/wait_for: `19` / `16`
- Format error rate: `0.40`
- Confidence: `medium`
- Rationale: Student 2 is repeatedly argued as high-utility while prof_3 intermittently favors Student 0. The episode has candidate content but no effective response or compromise.
- Excerpt: "Student 2 still seems the best choice"

### Episode 192

- Diagnosis line: `121225`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`, `invalid_action`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `10` / `7` / `6`
- Waits/wait_for: `0` / `4`
- Format error rate: `0.20`
- Confidence: `medium`
- Rationale: Students 0, 3, and 4 are considered, with Student 4 framed as a backup and prof_2 eventually moving to Student 0. The episode has brief but real alternative-balancing behavior.
- Excerpt: "Student 0 (highest utility) and Student 4 (to balance preferences)"

### Episode 193

- Diagnosis line: `123555`
- Category: `coordination_theater`
- Tags: `consensus_no`, `social_optimum_unknown`, `repeated_proposal`, `preference_probe`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `39` / `29` / `5`
- Waits/wait_for: `10` / `28`
- Format error rate: `0.18`
- Confidence: `high`
- Rationale: The agents loop on generic requests to discuss the evaluation, with sparse votes and little substantive candidate comparison. Public coordination talk overwhelms decision-making.
- Excerpt: "Please let us discuss the student evaluation further"

### Episode 194

- Diagnosis line: `123682`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `4` / `3` / `2`
- Waits/wait_for: `1` / `5`
- Format error rate: `0.50`
- Confidence: `high`
- Rationale: A Student 3 vote appears immediately and prof_1 follows in a four-turn episode. The public behavior is quick alignment, not deliberation.
- Excerpt: "Let's see what my colleagues think first."

### Episode 195

- Diagnosis line: `124206`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `repeated_proposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `14` / `10` / `3`
- Waits/wait_for: `4` / `6`
- Format error rate: `0.14`
- Confidence: `high`
- Rationale: Student 2 becomes focal early and the later messages mainly repeat support or wait for one more alignment. The consensus is endorsement of the focal candidate.
- Excerpt: "Voting for Student 2"

### Episode 196

- Diagnosis line: `124480`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `compromise_language`, `format_error_light`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `9` / `6` / `2`
- Waits/wait_for: `5` / `2`
- Format error rate: `0.44`
- Confidence: `medium`
- Rationale: prof_1 frames Student 0 as viable, and prof_2 and prof_3 align with that path. Student 4 appears as a backup, but the dominant behavior is following Student 0 momentum.
- Excerpt: "I propose Student 0 in the hopes of achieving consensus"

### Episode 197

- Diagnosis line: `126101`
- Category: `stalled_waiting_loop`
- Tags: `consensus_no`, `social_optimum_unknown`, `repeated_proposal`, `preference_probe`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `32` / `26` / `1`
- Waits/wait_for: `5` / `18`
- Format error rate: `0.22`
- Confidence: `high`
- Rationale: The first half repeatedly checks the vote tally and waits; the second half repeats Student 4 proposals without closing consensus. Waiting and process loops dominate the failure.
- Excerpt: "Let's check the current vote tally first"

### Episode 198

- Diagnosis line: `126778`
- Category: `negotiation_like`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `compromise_language`, `format_error_light`, `malformed_tags`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `15` / `14` / `2`
- Waits/wait_for: `1` / `15`
- Format error rate: `0.13`
- Confidence: `high`
- Rationale: Student 3 and Student 2 receive sustained public arguments, with agents trying to persuade each other around group fit and openness to feedback. It is a no-consensus episode but close to negotiation.
- Excerpt: "let's discuss why Student 3 might be a stronger fit for us"

### Episode 199

- Diagnosis line: `127169`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `vote_switch`, `format_error_light`, `malformed_tags`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `10` / `8` / `7`
- Waits/wait_for: `3` / `7`
- Format error rate: `0.20`
- Confidence: `medium`
- Rationale: Student 2, Student 1, and Student 4 are all proposed, and prof_1 moves to Student 4 after prof_2 presents it as a complementary option. The reasoning is brief but adaptive.
- Excerpt: "I suggest Student 4 as they have a strong utility"

### Episode 200

- Diagnosis line: `127506`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `counterproposal`, `vote_switch`, `early_focal_candidate`, `format_error_light`, `malformed_tags`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `9` / `7` / `5`
- Waits/wait_for: `3` / `6`
- Format error rate: `0.44`
- Confidence: `medium`
- Rationale: prof_2 votes Student 2 early; prof_3 briefly counters with Student 1 but later switches to Student 2 based on momentum. The episode is mostly following the focal Student 2 vote.
- Excerpt: "Reinforcing the preference for Student 2 continues to align with the overall group momentum"

### Episode 201

- Diagnosis line: `127599`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `3`
- Waits/wait_for: `2` / `2`
- Format error rate: `1.00`
- Confidence: `high`
- Rationale: Two professors vote Student 2 in a three-turn episode despite a Student 4 proposal by prof_2. There is no public negotiation.
- Excerpt: "Let's explore Student 4 further"

### Episode 202

- Diagnosis line: `127695`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `counterproposal`, `candidate_comparison`, `format_error_heavy`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `3` / `3` / `3`
- Waits/wait_for: `3` / `0`
- Format error rate: `1.00`
- Confidence: `high`
- Rationale: Each professor makes a different brief proposal or vote, with only minimal openness to adjust. The episode ends before any bargaining can develop.
- Excerpt: "I'm open to discussion if we need to adjust"

### Episode 203

- Diagnosis line: `127782`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `1` / `2`
- Waits/wait_for: `0` / `3`
- Format error rate: `0.00`
- Confidence: `high`
- Rationale: prof_2 and prof_3 both vote Student 2 almost immediately. The only public candidate message is a simple aim for Student 2.
- Excerpt: "Let's aim for Student 2"

### Episode 204

- Diagnosis line: `128955`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `repeated_proposal`, `vote_switch`, `format_error_light`, `malformed_tags`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `23` / `23` / `5`
- Waits/wait_for: `5` / `14`
- Format error rate: `0.22`
- Confidence: `medium`
- Rationale: Student 0 becomes the dominant proposal after prof_3 votes for it, and prof_1 and prof_2 eventually align. The long episode is mostly repeated endorsement of Student 0.
- Excerpt: "Your original proposal is for Student 0"

### Episode 205

- Diagnosis line: `129968`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `preference_probe`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `22` / `19` / `0`
- Waits/wait_for: `2` / `21`
- Format error rate: `0.14`
- Confidence: `medium`
- Rationale: Students 4, 3, and 1 are discussed with repeated requests for feedback, but no agent makes a clear concession or closes a coalition. Candidate content is present but shallow.
- Excerpt: "I propose Student 4, appreciating prof_3's preference but ready to discuss Student 3"

### Episode 206

- Diagnosis line: `130497`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `repeated_proposal`, `format_error_light`, `malformed_tags`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `13` / `14` / `5`
- Waits/wait_for: `4` / `7`
- Format error rate: `0.38`
- Confidence: `medium`
- Rationale: The episode lists pros and concerns for Students 2, 4, 1, and 3, but consensus arrives through repeated Student 2 votes rather than compromise.
- Excerpt: "Student 2 is well-rounded but I'm concerned"

### Episode 207

- Diagnosis line: `130712`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `7` / `7` / `2`
- Waits/wait_for: `2` / `2`
- Format error rate: `0.29`
- Confidence: `high`
- Rationale: prof_1 proposes and votes Student 2; prof_2 then follows to align with that preference. The Student 1 alternative is acknowledged but not negotiated.
- Excerpt: "I will propose Student 2"

### Episode 208

- Diagnosis line: `131319`
- Category: `coordination_theater`
- Tags: `consensus_no`, `social_optimum_unknown`, `preference_probe`, `repeated_proposal`, `invalid_action`, `malformed_tags`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `15` / `15` / `0`
- Waits/wait_for: `0` / `15`
- Format error rate: `0.00`
- Confidence: `high`
- Rationale: The public conversation repeatedly asks others to share initial thoughts on Student 2, with almost no concrete voting or tradeoff. Process questions dominate.
- Excerpt: "Please share your initial thoughts on Student 2"

### Episode 209

- Diagnosis line: `131404`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_heavy`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `3` / `2`
- Waits/wait_for: `3` / `0`
- Format error rate: `1.00`
- Confidence: `high`
- Rationale: prof_2 votes Student 2 and prof_3 follows immediately in a three-turn episode. No meaningful deliberation occurs.
- Excerpt: "Let's vote for Student 2"

### Episode 210

- Diagnosis line: `132345`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `compromise_language`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `21` / `18` / `0`
- Waits/wait_for: `4` / `17`
- Format error rate: `0.10`
- Confidence: `medium`
- Rationale: Students 0, 2, and 4 are considered with conditional fallback language, but the episode repeats positions and never produces an effective agreement.
- Excerpt: "If prof_3 supports Student 4, let's move ahead with that"

### Episode 211

- Diagnosis line: `132825`
- Category: `negotiation_like`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `compromise_language`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `12` / `13` / `2`
- Waits/wait_for: `1` / `10`
- Format error rate: `0.08`
- Confidence: `medium`
- Rationale: Students 0 and 4 are actively compared as Systems versus CompBio fits, and the agents discuss selecting one while acknowledging the other. It does not reach consensus, but it shows real tradeoff reasoning.
- Excerpt: "Student 0 has a higher utility and directly supports our Systems interests, while Student 4 is aligned with CompBio"

### Episode 212

- Diagnosis line: `133082`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `counterproposal`, `vote_switch`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `0`
- Turns/messages/votes: `7` / `5` / `5`
- Waits/wait_for: `2` / `5`
- Format error rate: `0.29`
- Confidence: `medium`
- Rationale: The episode starts with split Student 4 and Student 0 votes, then prof_1 switches to Student 0 after Student 0 gains support. The change is mostly following the focal vote.
- Excerpt: "Student 0 seems to be a solid candidate given the current consensus"

### Episode 213

- Diagnosis line: `133302`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_light`, `malformed_tags`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `7` / `7` / `2`
- Waits/wait_for: `1` / `6`
- Format error rate: `0.43`
- Confidence: `high`
- Rationale: prof_3 proposes Student 2 and prof_1 follows to drive consensus. The candidate rationale is brief and not negotiated.
- Excerpt: "Student 2 aligns well with our interdisciplinary research interests"

### Episode 214

- Diagnosis line: `133951`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `format_error_light`, `malformed_tags`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `14` / `14` / `5`
- Waits/wait_for: `2` / `10`
- Format error rate: `0.14`
- Confidence: `medium`
- Rationale: Students 0, 2, and 4 are all named, but the discussion is muddled and repetitive. Consensus on Student 2 is not produced by clear compromise.
- Excerpt: "explore both options. Student 4 is clearly a strong candidate"

### Episode 215

- Diagnosis line: `134171`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `7` / `1` / `3`
- Waits/wait_for: `2` / `4`
- Format error rate: `0.14`
- Confidence: `high`
- Rationale: Two votes for Student 2 appear in a short episode with only a brief Student 0 countervote. There is no substantive public deliberation.
- Excerpt: "Vote for Student 0 if possible"

### Episode 216

- Diagnosis line: `134715`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_suboptimal`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `15` / `10` / `3`
- Waits/wait_for: `6` / `7`
- Format error rate: `0.13`
- Confidence: `medium`
- Rationale: Student 2 is repeatedly proposed while Student 4 is later introduced as an alternative. The eventual Student 2 consensus follows repeated proposals, not bargaining.
- Excerpt: "Let's consider Student 4 first"

### Episode 217

- Diagnosis line: `135893`
- Category: `negotiation_like`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `compromise_language`, `format_error_light`, `prompt_leak`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `24` / `24` / `0`
- Waits/wait_for: `1` / `21`
- Format error rate: `0.12`
- Confidence: `high`
- Rationale: Students 4, 0, and 2 are actively contested, and prof_1 explicitly proposes Student 4 as a compromise to avoid stalemate. The episode fails to reach consensus but contains negotiation-like behavior.
- Excerpt: "Let's reconsider Student 4 as a potential compromise"

### Episode 218

- Diagnosis line: `136216`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `9` / `5` / `5`
- Waits/wait_for: `0` / `7`
- Format error rate: `0.11`
- Confidence: `medium`
- Rationale: The agents initially split among Students 0, 3, and 1, then prof_1 frames Student 1 as a bridge and prof_3 votes for it. The social reasoning is thin but adaptive.
- Excerpt: "I will propose Student 1 to bridge the gap"

### Episode 219

- Diagnosis line: `136307`
- Category: `instant_consensus`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `3` / `0` / `2`
- Waits/wait_for: `1` / `1`
- Format error rate: `0.33`
- Confidence: `high`
- Rationale: Two professors vote Student 2 within three turns. There is no public deliberation.
- Excerpt: "<VOTE>2</VOTE>"

### Episode 220

- Diagnosis line: `136495`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `4`
- Turns/messages/votes: `6` / `4` / `4`
- Waits/wait_for: `1` / `4`
- Format error rate: `0.33`
- Confidence: `medium`
- Rationale: prof_1 publicly rallies around Student 4, and prof_3 switches from Student 2 to Student 4. This is simple following with minimal comparison.
- Excerpt: "Let's rally around Student 4"

### Episode 221

- Diagnosis line: `137128`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_suboptimal`, `counterproposal`, `compromise_language`, `vote_switch`, `candidate_comparison`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `15` / `12` / `4`
- Waits/wait_for: `1` / `13`
- Format error rate: `0.07`
- Confidence: `medium`
- Rationale: Students 1, 2, 3, and 4 are all used as possible coalition points, with Student 4 offered as a fallback and prof_1 moving toward Student 2. The episode shows compromise attempts despite messy wording.
- Excerpt: "offer student 3 as a compromise"

### Episode 222

- Diagnosis line: `137286`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `counterproposal`, `format_error_heavy`, `malformed_tags`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `5` / `4` / `3`
- Waits/wait_for: `3` / `2`
- Format error rate: `0.60`
- Confidence: `medium`
- Rationale: The five-turn episode has scattered proposals for Students 2, 0, and 3 but no developed response before no consensus. It is shallow candidate discussion.
- Excerpt: "Let's support Student 2 and consider Student 0 as well."

### Episode 223

- Diagnosis line: `138388`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_social_optimum`, `early_focal_candidate`, `repeated_proposal`, `vote_switch`, `format_error_light`, `invalid_action`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `22` / `19` / `5`
- Waits/wait_for: `2` / `21`
- Format error rate: `0.14`
- Confidence: `medium`
- Rationale: Student 2 becomes focal after repeated votes and exhortations, and prof_3 moves from Student 3 to Student 2. The rest is mostly repeated support.
- Excerpt: "Please consider voting for them to maintain our momentum"

### Episode 224

- Diagnosis line: `138695`
- Category: `negotiation_like`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `compromise_language`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `1`
- Turns/messages/votes: `8` / `6` / `7`
- Waits/wait_for: `0` / `7`
- Format error rate: `0.25`
- Confidence: `high`
- Rationale: Student 1, Student 3, and Student 2 are considered, and prof_2 explicitly votes Student 1 despite a lower preference to promote cohesion. This is one of the clearer compromise cases.
- Excerpt: "I will vote for Student 1 to promote the team's cohesion"

### Episode 225

- Diagnosis line: `139063`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `early_focal_candidate`, `vote_switch`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `11` / `6` / `3`
- Waits/wait_for: `5` / `5`
- Format error rate: `0.36`
- Confidence: `medium`
- Rationale: The group drifts from Student 3 to Student 2 after prof_3 votes for Student 2 and prof_2 follows. There is little public bargaining.
- Excerpt: "Let's collectively favor Student 2"

### Episode 226

- Diagnosis line: `139952`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `preference_probe`, `repeated_proposal`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `20` / `18` / `2`
- Waits/wait_for: `1` / `17`
- Format error rate: `0.05`
- Confidence: `high`
- Rationale: Most turns ask where everyone stands on Student 2 or wait for another professor. The public action is process-heavy despite ending in Student 2 consensus.
- Excerpt: "What is everyone's preference for Student 2?"

### Episode 227

- Diagnosis line: `141950`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_suboptimal`, `preference_probe`, `repeated_proposal`, `private_reasoning_only`, `format_error_light`
- Consensus: `True`
- Chosen student: `3`
- Turns/messages/votes: `35` / `24` / `5`
- Waits/wait_for: `6` / `28`
- Format error rate: `0.14`
- Confidence: `high`
- Rationale: The episode repeatedly asks professors to share utilities and waits for prof_1, while Student 3 proposals recur. Public negotiation is displaced by process loops.
- Excerpt: "Please share your utilities for Student 2 and Student 3"

### Episode 228

- Diagnosis line: `142570`
- Category: `thin_candidate_discussion`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `15` / `14` / `2`
- Waits/wait_for: `2` / `11`
- Format error rate: `0.13`
- Confidence: `medium`
- Rationale: Students 4 and 2 are repeatedly advocated with brief ability rationales, but neither side adapts enough to reach consensus. The discussion remains shallow.
- Excerpt: "Student 2 has the highest utility"

### Episode 229

- Diagnosis line: `143529`
- Category: `negotiation_like`
- Tags: `consensus_no`, `social_optimum_unknown`, `candidate_comparison`, `counterproposal`, `compromise_language`, `format_error_light`
- Consensus: `False`
- Chosen student: `none`
- Turns/messages/votes: `21` / `16` / `1`
- Waits/wait_for: `3` / `17`
- Format error rate: `0.10`
- Confidence: `high`
- Rationale: Students 4, 0, 3, and 2 are considered, and Student 0 is repeatedly framed as a possible compromise coalition. No consensus forms, but the interaction is negotiation-like.
- Excerpt: "Let's reconsider Student 0 as a potential compromise"

### Episode 230

- Diagnosis line: `144156`
- Category: `coordination_theater`
- Tags: `consensus_yes`, `chosen_social_optimum`, `preference_probe`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `16` / `12` / `4`
- Waits/wait_for: `4` / `11`
- Format error rate: `0.19`
- Confidence: `high`
- Rationale: Student 2 is focal, but the public exchange mostly asks others for stances, perspectives, and quick resolution rather than comparing alternatives. Consensus follows process talk.
- Excerpt: "Can Prof_1 and Prof_3 share their thoughts on this?"

### Episode 231

- Diagnosis line: `144316`
- Category: `proposal_following`
- Tags: `consensus_yes`, `chosen_suboptimal`, `counterproposal`, `early_focal_candidate`, `format_error_light`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `5` / `4` / `3`
- Waits/wait_for: `2` / `2`
- Format error rate: `0.40`
- Confidence: `medium`
- Rationale: prof_3 proposes Student 2 and prof_2 follows after prof_1 mentions Students 2 and 3. The Student 2 consensus is mostly endorsement.
- Excerpt: "I lean towards Student 2"

### Episode 232

- Diagnosis line: `144706`
- Category: `thin_candidate_discussion`
- Tags: `consensus_yes`, `chosen_social_optimum`, `candidate_comparison`, `counterproposal`, `repeated_proposal`, `format_error_light`, `malformed_tags`, `prompt_leak`
- Consensus: `True`
- Chosen student: `2`
- Turns/messages/votes: `11` / `5` / `2`
- Waits/wait_for: `1` / `10`
- Format error rate: `0.09`
- Confidence: `medium`
- Rationale: Student 2 gets early votes, while Student 0 is discussed several times before prof_3 returns to Student 2. The episode includes shallow comparison but no real compromise.
- Excerpt: "Let's discuss Student 0 first and see if prof_1 is aligned"
