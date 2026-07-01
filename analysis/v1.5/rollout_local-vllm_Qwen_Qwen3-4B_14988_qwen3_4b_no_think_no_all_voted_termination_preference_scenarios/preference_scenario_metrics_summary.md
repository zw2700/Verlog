# Preference Scenario Metrics Summary

- episode_log: `logs/episode_log_rollout_local-vllm_Qwen_Qwen3-4B_14988_qwen3_4b_no_think_no_all_voted_termination.jsonl`
- global_step range: `None` to `None`
- episodes analyzed: `100`

Scenario definitions use each professor's top-ranked student set. Ties are allowed.

## all_three_share_top

- episodes: `9`
- percent of analyzed episodes: `0.090`
- consensus rate: `0.778`
- SO rate: `0.556`
- SO|cons rate: `0.714`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 6 | 0.667 | 0.667 | 0.333 | 0.500 | 0.620 | 1.500 | 251.5 | 12.0 |
| instant_decision | 3 | 0.333 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 34.3 | 3.0 |

## only_prof_1_prof_2_share_top

- episodes: `18`
- percent of analyzed episodes: `0.180`
- consensus rate: `0.889`
- SO rate: `0.444`
- SO|cons rate: `0.500`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 11 | 0.611 | 0.818 | 0.364 | 0.444 | 0.740 | 1.778 | 186.5 | 10.4 |
| instant_decision | 7 | 0.389 | 1.000 | 0.571 | 0.571 | 0.977 | 1.429 | 31.1 | 2.4 |

## only_prof_1_prof_3_share_top

- episodes: `21`
- percent of analyzed episodes: `0.210`
- consensus rate: `1.000`
- SO rate: `0.476`
- SO|cons rate: `0.476`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 18 | 0.857 | 1.000 | 0.444 | 0.444 | 0.942 | 1.778 | 167.0 | 8.9 |
| instant_decision | 3 | 0.143 | 1.000 | 0.667 | 0.667 | 0.949 | 1.667 | 31.3 | 2.3 |

## only_prof_2_prof_3_share_top

- episodes: `17`
- percent of analyzed episodes: `0.170`
- consensus rate: `1.000`
- SO rate: `0.412`
- SO|cons rate: `0.412`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 11 | 0.647 | 1.000 | 0.545 | 0.545 | 0.926 | 1.818 | 136.9 | 7.3 |
| instant_decision | 6 | 0.353 | 1.000 | 0.167 | 0.167 | 0.807 | 3.000 | 34.0 | 2.2 |

## no_pair_shares_top

- episodes: `35`
- percent of analyzed episodes: `0.350`
- consensus rate: `0.857`
- SO rate: `0.457`
- SO|cons rate: `0.533`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 24 | 0.686 | 0.792 | 0.417 | 0.526 | 0.762 | 1.789 | 187.5 | 10.0 |
| instant_decision | 11 | 0.314 | 1.000 | 0.545 | 0.545 | 0.923 | 2.182 | 29.9 | 2.3 |

