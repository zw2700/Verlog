# Preference Scenario Metrics Summary

- episode_log: `logs/episode_log_train_auton_17323`
- episode_log files read: `32`
- global_step range: `1` to `10`
- episodes analyzed: `3504`

Scenario definitions use each professor's top-ranked student set. Ties are allowed.

## all_three_share_top

- episodes: `266`
- percent of analyzed episodes: `0.076`
- consensus rate: `0.970`
- SO rate: `0.707`
- SO given consensus rate: `0.729`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision             |      136 | 0.511 |     1.000 | 0.816 |         0.816 |   0.956 |    1.309 |       44.3 |       2.5 |
| negotiation                  |      127 | 0.477 |     0.961 | 0.606 |         0.631 |   0.862 |    1.689 |      136.0 |       6.2 |
| stalled_coordination_failure |        3 | 0.011 |     0.000 | 0.000 |            NA |   0.000 |       NA |      212.3 |      28.0 |

## only_prof_1_prof_2_share_top

- episodes: `652`
- percent of analyzed episodes: `0.186`
- consensus rate: `0.937`
- SO rate: `0.543`
- SO given consensus rate: `0.579`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision             |      327 | 0.502 |     0.997 | 0.639 |         0.641 |   0.957 |    1.623 |       47.1 |       2.3 |
| negotiation                  |      320 | 0.491 |     0.891 | 0.453 |         0.509 |   0.828 |    1.863 |      184.7 |       7.7 |
| stalled_coordination_failure |        5 | 0.008 |     0.000 | 0.000 |            NA |   0.000 |       NA |      237.2 |      45.0 |

## only_prof_1_prof_3_share_top

- episodes: `632`
- percent of analyzed episodes: `0.180`
- consensus rate: `0.875`
- SO rate: `0.460`
- SO given consensus rate: `0.526`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation                  |      409 | 0.647 |     0.844 | 0.438 |         0.519 |   0.785 |    1.881 |      213.5 |       8.6 |
| instant_decision             |      210 | 0.332 |     0.990 | 0.533 |         0.538 |   0.925 |    1.846 |       57.8 |       2.3 |
| stalled_coordination_failure |       13 | 0.021 |     0.000 | 0.000 |            NA |   0.000 |       NA |      409.6 |      32.5 |

## only_prof_2_prof_3_share_top

- episodes: `639`
- percent of analyzed episodes: `0.182`
- consensus rate: `0.889`
- SO rate: `0.383`
- SO given consensus rate: `0.431`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation                  |      450 | 0.704 |     0.893 | 0.433 |         0.485 |   0.826 |    1.960 |      195.6 |       7.7 |
| instant_decision             |      170 | 0.266 |     0.965 | 0.282 |         0.293 |   0.856 |    2.445 |       69.7 |       2.3 |
| stalled_coordination_failure |       19 | 0.030 |     0.105 | 0.105 |         1.000 |   0.105 |    1.000 |      423.3 |      30.9 |

## no_pair_shares_top

- episodes: `1259`
- percent of analyzed episodes: `0.359`
- consensus rate: `0.830`
- SO rate: `0.316`
- SO given consensus rate: `0.381`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation                  |      833 | 0.662 |     0.779 | 0.298 |         0.382 |   0.724 |    2.231 |      238.7 |       9.1 |
| instant_decision             |      401 | 0.319 |     0.985 | 0.374 |         0.380 |   0.914 |    2.263 |       53.0 |       2.3 |
| stalled_coordination_failure |       25 | 0.020 |     0.040 | 0.000 |         0.000 |   0.038 |    4.000 |      360.7 |      35.8 |

## multi_pair_without_all_three_common_top

- episodes: `56`
- percent of analyzed episodes: `0.016`
- consensus rate: `0.929`
- SO rate: `0.339`
- SO given consensus rate: `0.365`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation                  |       28 | 0.500 |     0.893 | 0.214 |         0.240 |   0.846 |    1.880 |      204.7 |       9.0 |
| instant_decision             |       27 | 0.482 |     1.000 | 0.481 |         0.481 |   0.957 |    1.778 |       42.7 |       2.4 |
| stalled_coordination_failure |        1 | 0.018 |     0.000 | 0.000 |            NA |   0.000 |       NA |      508.0 |      28.0 |

