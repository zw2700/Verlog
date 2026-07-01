# Preference Scenario Metrics Summary

- episode_log: `logs/episode_log_train_auton_14743.jsonl`
- global_step range: `0` to `9`
- episodes analyzed: `7168`

Scenario definitions use each professor's top-ranked student set. Ties are allowed.

## all_three_share_top

- episodes: `246`
- percent of analyzed episodes: `0.034`
- consensus rate: `0.691`
- SO rate: `0.220`
- SO|cons rate: `0.318`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 190 | 0.772 | 0.637 | 0.158 | 0.248 | 0.494 | 3.884 | 311.8 | 14.8 |
| instant_decision | 47 | 0.191 | 1.000 | 0.489 | 0.489 | 0.821 | 3.064 | 44.3 | 3.3 |
| stalled_coordination_failure | 9 | 0.037 | 0.222 | 0.111 | 0.500 | 0.194 | 1.500 | 438.6 | 21.3 |

## only_prof_1_prof_2_share_top

- episodes: `1051`
- percent of analyzed episodes: `0.147`
- consensus rate: `0.685`
- SO rate: `0.175`
- SO|cons rate: `0.256`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 858 | 0.816 | 0.657 | 0.154 | 0.234 | 0.560 | 4.032 | 310.2 | 13.7 |
| instant_decision | 150 | 0.143 | 0.993 | 0.340 | 0.342 | 0.857 | 3.745 | 42.7 | 3.0 |
| stalled_coordination_failure | 43 | 0.041 | 0.163 | 0.023 | 0.143 | 0.135 | 3.857 | 475.6 | 27.3 |

## only_prof_1_prof_3_share_top

- episodes: `1033`
- percent of analyzed episodes: `0.144`
- consensus rate: `0.712`
- SO rate: `0.155`
- SO|cons rate: `0.218`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 842 | 0.815 | 0.694 | 0.143 | 0.205 | 0.582 | 4.163 | 295.8 | 13.4 |
| instant_decision | 151 | 0.146 | 0.980 | 0.265 | 0.270 | 0.828 | 4.155 | 42.1 | 3.0 |
| stalled_coordination_failure | 40 | 0.039 | 0.075 | 0.000 | 0.000 | 0.063 | 5.333 | 495.4 | 26.6 |

## only_prof_2_prof_3_share_top

- episodes: `1036`
- percent of analyzed episodes: `0.145`
- consensus rate: `0.693`
- SO rate: `0.122`
- SO|cons rate: `0.175`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 866 | 0.836 | 0.670 | 0.120 | 0.179 | 0.561 | 4.245 | 303.8 | 13.4 |
| instant_decision | 139 | 0.134 | 0.971 | 0.158 | 0.163 | 0.821 | 4.156 | 44.0 | 3.2 |
| stalled_coordination_failure | 30 | 0.029 | 0.067 | 0.000 | 0.000 | 0.052 | 6.000 | 493.0 | 27.1 |
| malformed_or_other | 1 | 0.001 | 1.000 | 0.000 | 0.000 | 0.716 | 2.000 | 274.0 | 15.0 |

## no_pair_shares_top

- episodes: `3763`
- percent of analyzed episodes: `0.525`
- consensus rate: `0.675`
- SO rate: `0.122`
- SO|cons rate: `0.180`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 3134 | 0.833 | 0.641 | 0.112 | 0.175 | 0.552 | 4.573 | 312.5 | 13.8 |
| instant_decision | 519 | 0.138 | 0.998 | 0.200 | 0.201 | 0.872 | 4.317 | 34.9 | 3.1 |
| stalled_coordination_failure | 110 | 0.029 | 0.109 | 0.027 | 0.250 | 0.093 | 3.917 | 491.3 | 27.9 |

## multi_pair_without_all_three_common_top

- episodes: `39`
- percent of analyzed episodes: `0.005`
- consensus rate: `0.718`
- SO rate: `0.179`
- SO|cons rate: `0.250`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 27 | 0.692 | 0.704 | 0.185 | 0.263 | 0.589 | 3.632 | 346.1 | 16.9 |
| instant_decision | 8 | 0.205 | 1.000 | 0.250 | 0.250 | 0.877 | 3.125 | 33.8 | 3.5 |
| stalled_coordination_failure | 4 | 0.103 | 0.250 | 0.000 | 0.000 | 0.197 | 5.000 | 493.2 | 24.5 |

