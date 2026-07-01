# Preference Scenario Metrics Summary

- episode_log: `logs/episode_log_train_auton_13244.jsonl`
- global_step range: `0` to `9`
- episodes analyzed: `7246`

Scenario definitions use each professor's top-ranked student set. Ties are allowed.

## all_three_share_top

- episodes: `503`
- percent of analyzed episodes: `0.069`
- consensus rate: `0.674`
- SO rate: `0.284`
- SO|cons rate: `0.422`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 410 | 0.815 | 0.671 | 0.280 | 0.418 | 0.556 | 2.164 | 282.0 | 13.1 |
| instant_decision | 71 | 0.141 | 0.887 | 0.380 | 0.429 | 0.748 | 2.032 | 27.7 | 3.7 |
| stalled_coordination_failure | 22 | 0.044 | 0.045 | 0.045 | 1.000 | 0.045 | 1.000 | 517.7 | 24.5 |

## only_prof_1_prof_2_share_top

- episodes: `1403`
- percent of analyzed episodes: `0.194`
- consensus rate: `0.652`
- SO rate: `0.234`
- SO|cons rate: `0.360`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 1164 | 0.830 | 0.643 | 0.216 | 0.335 | 0.566 | 2.418 | 287.2 | 13.3 |
| instant_decision | 187 | 0.133 | 0.861 | 0.406 | 0.472 | 0.783 | 2.118 | 30.7 | 3.4 |
| stalled_coordination_failure | 52 | 0.037 | 0.096 | 0.038 | 0.400 | 0.091 | 1.600 | 492.6 | 25.6 |

## only_prof_1_prof_3_share_top

- episodes: `1342`
- percent of analyzed episodes: `0.185`
- consensus rate: `0.666`
- SO rate: `0.223`
- SO|cons rate: `0.334`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 1154 | 0.860 | 0.656 | 0.218 | 0.333 | 0.575 | 2.491 | 292.5 | 13.7 |
| instant_decision | 149 | 0.111 | 0.899 | 0.309 | 0.343 | 0.792 | 2.418 | 32.1 | 3.5 |
| stalled_coordination_failure | 39 | 0.029 | 0.077 | 0.026 | 0.333 | 0.065 | 3.000 | 488.7 | 29.7 |

## only_prof_2_prof_3_share_top

- episodes: `1289`
- percent of analyzed episodes: `0.178`
- consensus rate: `0.646`
- SO rate: `0.196`
- SO|cons rate: `0.304`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 1080 | 0.838 | 0.631 | 0.189 | 0.299 | 0.549 | 2.584 | 292.5 | 13.5 |
| instant_decision | 163 | 0.126 | 0.908 | 0.294 | 0.324 | 0.802 | 2.480 | 29.0 | 3.4 |
| stalled_coordination_failure | 46 | 0.036 | 0.065 | 0.022 | 0.333 | 0.058 | 1.667 | 499.9 | 27.0 |

## no_pair_shares_top

- episodes: `2609`
- percent of analyzed episodes: `0.360`
- consensus rate: `0.663`
- SO rate: `0.189`
- SO|cons rate: `0.285`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 2210 | 0.847 | 0.651 | 0.180 | 0.276 | 0.584 | 2.659 | 289.4 | 13.3 |
| instant_decision | 316 | 0.121 | 0.899 | 0.294 | 0.327 | 0.817 | 2.458 | 32.6 | 3.5 |
| stalled_coordination_failure | 83 | 0.032 | 0.072 | 0.036 | 0.500 | 0.069 | 1.833 | 491.4 | 27.0 |

## multi_pair_without_all_three_common_top

- episodes: `100`
- percent of analyzed episodes: `0.014`
- consensus rate: `0.640`
- SO rate: `0.190`
- SO|cons rate: `0.297`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 82 | 0.820 | 0.646 | 0.195 | 0.302 | 0.577 | 2.472 | 319.4 | 15.2 |
| instant_decision | 13 | 0.130 | 0.846 | 0.231 | 0.273 | 0.760 | 2.455 | 37.1 | 4.2 |
| stalled_coordination_failure | 5 | 0.050 | 0.000 | 0.000 | NA | 0.000 | NA | 501.2 | 33.8 |

