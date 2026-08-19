# Category Metrics Summary

- episode_log: `logs/episode_log_train_auton_16403.jsonl`
- episode_log files read: `1`
- global_step range: `1` to `10`
- episodes analyzed: `3585`
- overall consensus rate: `0.880`
- overall SO rate: `0.426`
- overall SO given consensus rate: `0.484`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation                  |     2163 | 0.603 |     0.835 | 0.383 |         0.458 |   0.774 |    2.041 |      215.3 |       8.9 |
| instant_decision             |     1351 | 0.377 |     0.996 | 0.515 |         0.517 |   0.931 |    1.915 |       46.0 |       2.4 |
| stalled_coordination_failure |       71 | 0.020 |     0.070 | 0.028 |         0.400 |   0.064 |    2.400 |      369.4 |      36.2 |
