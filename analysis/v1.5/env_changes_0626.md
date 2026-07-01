# Environment Changes 0626

This file tracks environment-construction and termination changes being tested
for the admissions committee negotiation environment.

## 1. Optional removal of all-voted no-consensus termination

Status: implemented as a backwards-compatible env/config flag.

Motivation:

- In the original environment, if all three professors cast valid votes and no
  student reached the consensus threshold, the episode terminated immediately
  with no consensus.
- In many no-shared-top episodes, this made the game end as soon as the three
  professors voted for three different students.
- This prevented repair negotiation after the first distinct-vote state.

Implementation:

- Added `terminate_on_all_voted_no_consensus`.
- Default: `false`.
- Setting it to `false` lets the episode continue until consensus, token budget,
  or `max_steps`.

Rollout flag:

```bash
--no-terminate-on-all-voted-no-consensus
```

Example:

```bash
sbatch rollout_frontier_frank.sbatch \
  --no-terminate-on-all-voted-no-consensus
```

## 2. Preference rejection sampling by low pairwise correlation

Status: implemented as a backwards-compatible env/config flag.

Motivation:

- Baseline environment construction produces `no_pair_shares_top` in about 36%
  of 3-professor, 5-student episodes.
- Training may under-emphasize negotiation because many episodes have an easy
  shared-preference path to consensus or instant decision.
- Rejection sampling makes professor preferences more diverse while preserving
  the same preference-vector representation: each professor still receives a
  permutation of `[0, 1, ..., feature_dim - 1]`.

Implementation:

- Added `professor_preference_mode`.
- Default: `random_permutation`, preserving old behavior.
- Added `preference_correlation_threshold`.
- Default threshold: `0.0`.
- Added `preference_rejection_max_attempts`.
- Default max attempts: `1000`.

Supported modes:

- `random_permutation`: original independent random permutation sampler.
- `diverse_top_feature`: directly assigns distinct top-weighted features.
- `rejection_low_correlation`: samples random permutations and accepts only if
  every professor pair has Pearson correlation less than or equal to the
  threshold.
- `rejection_low_correlation_distinct_top`: same as above, also requiring
  distinct top-weighted features.

Correlation definition:

- Pearson correlation over the two professors' feature-weight vectors.
- For threshold `0.0`, no professor pair is allowed to have positively
  correlated feature preferences.

Recommended first setting:

```bash
--professor-preference-mode rejection_low_correlation \
--preference-correlation-threshold 0.0
```

Simulation result for 3 professors, 5 students:

- Baseline `no_pair_shares_top`: about 36.2%.
- `rejection_low_correlation`, threshold `0.0`: about 64.2%.
- Expected rejection-sampling cost: about 9.3 raw preference samples per
  accepted preference set.

Example with no all-voted termination:

```bash
ROLLOUT_POSTFIX="pref_corr0_no_all_voted_termination" \
sbatch rollout_frontier_frank.sbatch \
  --professor-preference-mode rejection_low_correlation \
  --preference-correlation-threshold 0.0 \
  --preference-rejection-max-attempts 1000 \
  --no-terminate-on-all-voted-no-consensus
```

## 3. Larger student batches

Status: already supported by the existing rollout/env config.

Motivation:

- Increasing the number of students makes it less likely that two professors
  share the same top-ranked student.
- This is a simpler intervention than changing professor preference sampling.

Rollout flag:

```bash
--students-per-batch 10
```

Simulation results with baseline preferences:

- 3 professors, 5 students: `no_pair_shares_top` about 36.2%.
- 3 professors, 8 students: `no_pair_shares_top` about 48.7%.
- 3 professors, 10 students: `no_pair_shares_top` about 53.1%.

Example with no all-voted termination:

```bash
ROLLOUT_POSTFIX="10_students_no_all_voted_termination" \
sbatch rollout_frontier_frank.sbatch \
  --students-per-batch 10 \
  --no-terminate-on-all-voted-no-consensus
```

Note:

- Combining 10 students with `rejection_low_correlation` threshold `0.0` gives
  about 84.8% `no_pair_shares_top`, which may be too strong for the first
  rollout ablation.
