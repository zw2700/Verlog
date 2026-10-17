# Preference Scenario Metrics Summary

- episode_log: `logs/episode_log_train_auton_16403.jsonl`
- episode_log files read: `1`
- global_step range: `1` to `10`
- episodes analyzed: `3585`

Scenario definitions use each professor's top-ranked student set. Ties are allowed.

## all_three_share_top

- episodes: `292`
- percent of analyzed episodes: `0.081`
- consensus rate: `0.986`
- SO rate: `0.712`
- SO given consensus rate: `0.722`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision             |      160 | 0.548 |     1.000 | 0.744 |         0.744 |   0.937 |    1.419 |       43.9 |       2.5 |
| negotiation                  |      130 | 0.445 |     0.985 | 0.685 |         0.695 |   0.913 |    1.430 |      120.8 |       5.8 |
| stalled_coordination_failure |        2 | 0.007 |     0.000 | 0.000 |            NA |   0.000 |       NA |      296.0 |      25.5 |

## only_prof_1_prof_2_share_top

- episodes: `653`
- percent of analyzed episodes: `0.182`
- consensus rate: `0.937`
- SO rate: `0.568`
- SO given consensus rate: `0.606`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision             |      350 | 0.536 |     0.997 | 0.646 |         0.648 |   0.958 |    1.625 |       44.0 |       2.4 |
| negotiation                  |      293 | 0.449 |     0.894 | 0.491 |         0.550 |   0.833 |    1.836 |      179.0 |       7.8 |
| stalled_coordination_failure |       10 | 0.015 |     0.100 | 0.100 |         1.000 |   0.100 |    1.000 |      251.3 |      47.5 |

## only_prof_1_prof_3_share_top

- episodes: `630`
- percent of analyzed episodes: `0.176`
- consensus rate: `0.890`
- SO rate: `0.484`
- SO given consensus rate: `0.544`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation                  |      426 | 0.676 |     0.873 | 0.425 |         0.487 |   0.807 |    2.024 |      203.6 |       8.5 |
| instant_decision             |      189 | 0.300 |     1.000 | 0.656 |         0.656 |   0.954 |    1.582 |       47.9 |       2.4 |
| stalled_coordination_failure |       15 | 0.024 |     0.000 | 0.000 |            NA |   0.000 |       NA |      377.8 |      34.9 |

## only_prof_2_prof_3_share_top

- episodes: `665`
- percent of analyzed episodes: `0.185`
- consensus rate: `0.874`
- SO rate: `0.358`
- SO given consensus rate: `0.410`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation                  |      421 | 0.633 |     0.841 | 0.404 |         0.480 |   0.783 |    1.915 |      221.4 |       8.9 |
| instant_decision             |      226 | 0.340 |     0.996 | 0.296 |         0.298 |   0.886 |    2.293 |       45.4 |       2.4 |
| stalled_coordination_failure |       18 | 0.027 |     0.111 | 0.056 |         0.500 |   0.106 |    2.000 |      411.1 |      31.1 |

## no_pair_shares_top

- episodes: `1294`
- percent of analyzed episodes: `0.361`
- consensus rate: `0.824`
- SO rate: `0.298`
- SO given consensus rate: `0.361`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation                  |      860 | 0.665 |     0.767 | 0.271 |         0.353 |   0.710 |    2.309 |      246.1 |       9.9 |
| instant_decision             |      408 | 0.315 |     0.990 | 0.373 |         0.376 |   0.920 |    2.317 |       48.0 |       2.3 |
| stalled_coordination_failure |       26 | 0.020 |     0.077 | 0.000 |         0.000 |   0.063 |    3.500 |      386.6 |      37.0 |

## multi_pair_without_all_three_common_top

- episodes: `51`
- percent of analyzed episodes: `0.014`
- consensus rate: `0.941`
- SO rate: `0.373`
- SO given consensus rate: `0.396`

| Category         | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation      |       33 | 0.647 |     0.909 | 0.333 |         0.367 |   0.827 |    2.233 |      178.7 |       7.5 |
| instant_decision |       18 | 0.353 |     1.000 | 0.444 |         0.444 |   0.945 |    1.722 |       44.6 |       2.3 |

