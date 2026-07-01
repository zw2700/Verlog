# Preference Scenario Metrics Summary

- episode_log: `logs/episode_log_rollout_cmu-gateway_us.anthropic.claude-haiku-4-5-20251001-v1_0_14263_no_all_voted_termination.jsonl`
- global_step range: `None` to `None`
- episodes analyzed: `100`

Scenario definitions use each professor's top-ranked student set. Ties are allowed.

## all_three_share_top

- episodes: `9`
- percent of analyzed episodes: `0.090`
- consensus rate: `1.000`
- SO rate: `1.000`
- SO|cons rate: `1.000`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| instant_decision | 9 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 23.8 | 2.0 |

## only_prof_1_prof_2_share_top

- episodes: `18`
- percent of analyzed episodes: `0.180`
- consensus rate: `1.000`
- SO rate: `0.722`
- SO|cons rate: `0.722`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| instant_decision | 16 | 0.889 | 1.000 | 0.750 | 0.750 | 0.986 | 1.250 | 35.6 | 2.0 |
| negotiation | 2 | 0.111 | 1.000 | 0.500 | 0.500 | 0.993 | 1.500 | 186.5 | 6.5 |

## only_prof_1_prof_3_share_top

- episodes: `21`
- percent of analyzed episodes: `0.210`
- consensus rate: `1.000`
- SO rate: `0.905`
- SO|cons rate: `0.905`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 19 | 0.905 | 1.000 | 0.895 | 0.895 | 0.988 | 1.105 | 80.9 | 3.2 |
| instant_decision | 2 | 0.095 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 26.5 | 2.0 |

## only_prof_2_prof_3_share_top

- episodes: `17`
- percent of analyzed episodes: `0.170`
- consensus rate: `1.000`
- SO rate: `1.000`
- SO|cons rate: `1.000`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 16 | 0.941 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 77.6 | 3.3 |
| instant_decision | 1 | 0.059 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.0 | 3.0 |

## no_pair_shares_top

- episodes: `35`
- percent of analyzed episodes: `0.350`
- consensus rate: `0.971`
- SO rate: `0.400`
- SO|cons rate: `0.412`

| Category | Episodes | % | Consensus | SO | SO|cons | Avg eff | Avg rank | Avg tokens | Avg turns |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| negotiation | 35 | 1.000 | 0.971 | 0.400 | 0.412 | 0.920 | 1.971 | 247.3 | 9.9 |

