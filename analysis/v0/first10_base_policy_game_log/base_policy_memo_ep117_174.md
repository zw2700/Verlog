# Base Policy Categorization Memo: Episodes 117-174

Assigned range: episodes 117 through 174 inclusive from `logs/game_log_train_auton_12993.log`, using only content before line 144892.

## Category Counts

- `negotiation_like`: 18
- `proposal_following`: 16
- `thin_candidate_discussion`: 11
- `instant_consensus`: 7
- `stalled_waiting_loop`: 6

## Representative Episodes

- Episode 117: stalled waiting loop. The agents repeatedly ask whether to introduce Student 3 and wait for one another, ending with no votes and no consensus.
- Episode 132: negotiation-like. Student 2 and Student 3 are treated as competing options with fallback language, and prof_1 eventually switches to Student 2.
- Episode 150: negotiation-like no-consensus case. Prof_2 argues substantively for Student 3 over Student 1, and prof_3 says they are persuaded while asking for a compromise.
- Episode 157: stalled waiting loop. The public behavior collapses into repeated checks of prof_1's stance on Student 0.
- Episode 170: negotiation-like consensus case. Student 0 and Student 2 are framed as a compromise pair before the final Student 0 consensus.

## Low-Confidence Or Borderline Episodes

- Low confidence: episode 169. It is heavily malformed with prompt/history leakage but still readable enough to classify as shallow candidate discussion rather than execution breakdown.
- Borderline negotiation-like versus thin discussion: episodes 122, 136, 160, 166, and 173. I marked them negotiation-like because they include public candidate comparison plus either explicit compromise language, vote movement, or response to another professor's preference.
- Borderline stalled versus thin discussion: episodes 152, 155, 157, and 168. I marked them stalled because repeated waiting or self-directed checking dominated the public behavior and blocked progress.

## New Categories

No new category suggested. The fixed taxonomy covered the observed behaviors.

## Negotiation-Like Behavior

Meaningful negotiation-like behavior does appear, but it is not the majority behavior. The clearest examples involve explicit comparison across two or three students, fallback or compromise language, and some vote movement. Many other consensus outcomes arise from quick following or shallow repeated proposals rather than socially grounded deliberation.
