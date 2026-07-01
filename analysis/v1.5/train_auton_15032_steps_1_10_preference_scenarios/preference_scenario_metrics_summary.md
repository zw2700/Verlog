# Preference Scenario Metrics Summary

- episode_log: `logs/episode_log_train_auton_15032.jsonl`
- global_step range: `1` to `10`
- episodes analyzed: `8200`

Scenario definitions use each professor's top-ranked student set. Ties are allowed.

## all_three_share_top

- episodes: `47`
- percent of analyzed episodes: `0.006`
- consensus rate: `0.766`
- SO rate: `0.298`
- SO|cons rate: `0.389`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 33 | 0.702 | 0.727 | 0.242 | 0.333 | 0.581 | 2.625 | 328.0 | 15.0 |
| instant_decision | 11 | 0.234 | 1.000 | 0.545 | 0.545 | 0.909 | 1.727 | 22.4 | 3.9 |
| stalled_coordination_failure | 3 | 0.064 | 0.333 | 0.000 | 0.000 | 0.284 | 2.000 | 445.3 | 25.3 |

## only_prof_1_prof_2_share_top

- episodes: `942`
- percent of analyzed episodes: `0.115`
- consensus rate: `0.702`
- SO rate: `0.223`
- SO|cons rate: `0.318`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 753 | 0.799 | 0.675 | 0.198 | 0.293 | 0.614 | 2.579 | 293.3 | 13.4 |
| instant_decision | 148 | 0.157 | 1.000 | 0.412 | 0.412 | 0.924 | 2.338 | 25.8 | 3.2 |
| stalled_coordination_failure | 41 | 0.044 | 0.122 | 0.000 | 0.000 | 0.110 | 4.000 | 489.1 | 28.0 |

## only_prof_1_prof_3_share_top

- episodes: `972`
- percent of analyzed episodes: `0.119`
- consensus rate: `0.703`
- SO rate: `0.199`
- SO|cons rate: `0.283`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 781 | 0.803 | 0.665 | 0.190 | 0.285 | 0.600 | 2.655 | 295.8 | 13.3 |
| instant_decision | 163 | 0.168 | 0.994 | 0.276 | 0.278 | 0.897 | 2.679 | 30.2 | 3.2 |
| stalled_coordination_failure | 28 | 0.029 | 0.071 | 0.000 | 0.000 | 0.064 | 3.000 | 478.0 | 26.6 |

## only_prof_2_prof_3_share_top

- episodes: `949`
- percent of analyzed episodes: `0.116`
- consensus rate: `0.690`
- SO rate: `0.177`
- SO|cons rate: `0.256`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 758 | 0.799 | 0.662 | 0.173 | 0.261 | 0.596 | 2.703 | 301.5 | 13.2 |
| instant_decision | 155 | 0.163 | 0.974 | 0.239 | 0.245 | 0.868 | 2.755 | 39.5 | 3.2 |
| stalled_coordination_failure | 36 | 0.038 | 0.056 | 0.000 | 0.000 | 0.048 | 2.500 | 502.3 | 26.0 |

## no_pair_shares_top

- episodes: `5232`
- percent of analyzed episodes: `0.638`
- consensus rate: `0.693`
- SO rate: `0.181`
- SO|cons rate: `0.261`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 4351 | 0.832 | 0.664 | 0.171 | 0.257 | 0.608 | 2.745 | 303.2 | 13.4 |
| instant_decision | 726 | 0.139 | 0.996 | 0.274 | 0.275 | 0.915 | 2.675 | 32.5 | 3.1 |
| stalled_coordination_failure | 155 | 0.030 | 0.077 | 0.032 | 0.417 | 0.076 | 1.750 | 491.9 | 28.7 |

## multi_pair_without_all_three_common_top

- episodes: `58`
- percent of analyzed episodes: `0.007`
- consensus rate: `0.621`
- SO rate: `0.155`
- SO|cons rate: `0.250`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 45 | 0.776 | 0.600 | 0.111 | 0.185 | 0.558 | 2.667 | 299.3 | 13.4 |
| instant_decision | 8 | 0.138 | 1.000 | 0.375 | 0.375 | 0.941 | 2.000 | 54.4 | 2.4 |
| stalled_coordination_failure | 5 | 0.086 | 0.200 | 0.200 | 1.000 | 0.200 | 1.000 | 463.0 | 28.6 |

