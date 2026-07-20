# Category Metrics Summary

- episode_log: `outputs/sft/evaluations/haiku_qwen3_sweep_v1/raw100_step16/episodes.jsonl`
- episode_log files read: `1`
- global_step range: `None` to `None`
- episodes analyzed: `500`
- overall consensus rate: `0.950`
- overall SO rate: `0.554`
- overall SO given consensus rate: `0.583`

| Category                     | Episodes |     % | Consensus |    SO | SO given cons | Avg eff | Avg rank | Avg tokens | Avg turns |
| ---------------------------- | --------: | -----: | ---------: | -----: | -------------: | -------: | --------: | ----------: | ---------: |
| negotiation                  |      330 | 0.660 |     0.924 | 0.500 |         0.541 |   0.867 |    1.849 |      193.1 |       5.5 |
| instant_decision             |      169 | 0.338 |     1.000 | 0.663 |         0.663 |   0.963 |    1.544 |       50.7 |       2.1 |
| stalled_coordination_failure |        1 | 0.002 |     1.000 | 0.000 |         0.000 |   0.967 |    2.000 |      328.0 |      33.0 |
