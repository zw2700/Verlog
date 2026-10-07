import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).parents[2] / "analysis/v1/compute_category_metrics.py"
SPEC = importlib.util.spec_from_file_location("compute_category_metrics", MODULE_PATH)
category_metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(category_metrics)


def test_episode_log_files_prefers_worker_shards_and_sorts_naturally(tmp_path):
    shard_10 = tmp_path / "episode_log.worker10.jsonl"
    shard_2 = tmp_path / "episode_log.worker02.jsonl"
    merged = tmp_path / "merged.jsonl"
    for path in (shard_10, shard_2, merged):
        path.write_text("")

    assert category_metrics.episode_log_files(tmp_path) == [shard_2, shard_10]


def test_episode_log_files_supports_single_unsharded_file(tmp_path):
    episode_log = tmp_path / "episode_log.jsonl"
    episode_log.write_text("")

    assert category_metrics.episode_log_files(episode_log) == [episode_log]
