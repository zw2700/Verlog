# Final 10 Training Steps Agent-Model Segmentation

## Scope

- Source: `logs/agent_model_train_auton_12993.log`
- Training steps: `global_steps=66..75` inferred by timestamp alignment to `game_log_train_auton_12993.log`
- Agent-model line slice: `12887502..13148260`
- Excludes trailing cluster 78, which starts at line `13148261` and has no matching `game_log` training-step marker.

## Counts

- Turn records: `2560`
- Total segments: `770`
- Complete bounded episodes: `716`
- Complete episodes with inferred consensus: `630`
- Complete episodes without inferred consensus: `86`
- Left continuation fragments: `22`
- Right trailing fragments: `32`
- Unbounded env fragments: `0`

## Complete Episodes By Start Step

| Global step | Complete episodes starting in step | Turn records in step |
|---:|---:|---:|
| 66 | 66 | 256 |
| 67 | 63 | 256 |
| 68 | 54 | 256 |
| 69 | 71 | 256 |
| 70 | 80 | 256 |
| 71 | 80 | 256 |
| 72 | 80 | 256 |
| 73 | 89 | 256 |
| 74 | 78 | 256 |
| 75 | 55 | 256 |

## Segmentation Rule

An episode start is inferred from a turn block with all of:

- `=== YOUR TURN (t=0) ===`
- `CONVERSATION HISTORY ... (No messages yet)`
- no `CURRENT VOTES:` block

A complete bounded episode is a start followed by another start in the same env within the slice.
The final started episode in each env is marked as `right_trailing_fragment` because it may continue after the slice.
Turns before the first start in an env are marked as `left_continuation_fragment` because the episode began before global step 66.