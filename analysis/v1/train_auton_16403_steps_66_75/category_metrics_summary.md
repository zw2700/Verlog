# Category Metrics Summary

- episode_log: `logs/episode_log_train_auton_16403.jsonl`
- episode_log files read: `1`
- global_step range: `66` to `75`
- episodes analyzed: `728`
- overall consensus rate: `0.955`
- overall SO rate: `0.565`
- overall SO given consensus rate: `0.591`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| instant_decision             |      435 | 0.598 |     0.982 | 0.618 |         0.630 |   0.941 |    1.632 |       70.7 |       1.9 |
| negotiation                  |      292 | 0.401 |     0.918 | 0.486 |         0.530 |   0.867 |    1.862 |      158.0 |       4.1 |
| stalled_coordination_failure |        1 | 0.001 |     0.000 | 0.000 |            NA |   0.000 |       NA |      516.0 |      43.0 |
