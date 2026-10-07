# Individual/shared × numerical/binary reward comparison

Use historical W&B run `szopa-michala/unscripted/amtaz7fo`
(`unscripted_auton_base-warm10`) as the individual numerical baseline.
This worktree starts at its recorded parent commit `e9e6b5ac` and keeps hiring
environment commit `aa7da2bc9947289eb2261fc3d0bf6f1875f4a631` pinned.
Three new runs vary terminal reward:

| Mode | Reward to professor i after agreement |
|---|---|
| `binary_individual` | 1 iff selected student maximizes i's utility, else 0 |
| `group` | Sum of all professors' utilities for the selected student |
| `binary_social_optimum` | 1 iff selected student maximizes summed utility, else 0 |

Failed agreement gives zero selection reward in all modes. All modes retain
0.1 format/invalid-action penalties and the baseline's KL regularization.
Thus binary refers to terminal selection reward, not the complete PPO reward.
This deliberately differs from the earlier binary-only proposal that disabled
penalties: preserving them avoids an extra treatment difference from baseline.
Use absolute tie tolerance 1e-9; real utility gaps are not rounded away.

## Matched training settings

Compose `+experiment=reward_comparison` through `slurm/train_auton.sbatch`.
Qwen3-4B; native thinking disabled; 32 environments; batch256; actor LR1e-6,
critic LR1e-5; actor-visible critic; actor/critic microbatches2/4; static batching;
10 critic-only steps followed by65 actor-update steps; warmup repeat/divide1/1.
Keep original private-utility prompts, majority voting, five candidates, token
budget500, max50 actions, and independent random-permutation preferences.
No discussion instructions, bonuses, repeated interaction, or replay changes.

Submit exactly the three conditions using tags `own-binary-warm10`,
`shared-numerical-warm10`, and `shared-binary-warm10`, with explicit reward_mode
overrides. Requested A6000 resources:4GPUs,32CPUs,200G,24hours; partition general,
QOS qos_general. H200 test-only queue estimates use the same resource counts in
project/qos_radio_freq. Test-only estimates do not reserve resources.

Final validation and checkpoints are enabled at step75 (the historical run did
not save them); no pre-training validation perturbs the training RNG progression.
Automatic resume is disabled and each job has an isolated output directory.
No matched random-scenario pairing or exact reproducibility across GPU hardware
is claimed. The unchanged prompt explicitly describes individual utility, so
shared-reward runs also test adaptation despite that common initial instruction.

## Measurement changes

Terminal ranks and binary rewards use the same tolerance; report historical
baseline tie-aware recomputations alongside original strict floating labels.
The parent agent loop now clears completion metrics on nonterminal turns,
preventing repeated counting of the previous finished game. This change does
not change rewards or GAE. Use unique raw episode JSONL for comparisons to the
historical run, whose dashboard outcome metrics can contain duplicates.

Record commit, source archive hash, fully resolved config, exact sbatch argv,
Slurm ID, output paths, and eventual W&B URL in the submission manifest. Keep
the remote experiment source immutable until all three jobs finish.

## Validation

Run `python -m pytest -q tests/envs/test_hiring_reward_comparison.py
tests/experimental/test_completed_episode_metric_lifecycle.py`.
The tests cover real environment transitions, all reward conditions, absent
agreement, preserved penalties and observations, numerical ties, nonoptimal
choices, and completed-game metric lifecycle with terminal-reward routing.
