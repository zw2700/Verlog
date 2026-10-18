import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).parents[2] / "verl/envs/hiring_episode_logging.py"
SPEC = importlib.util.spec_from_file_location("hiring_episode_logging", MODULE_PATH)
episode_logging = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(episode_logging)


def test_worker_shard_path_uses_run_specific_directory(tmp_path):
    base_path = tmp_path / "episode_log_train_auton_17323.jsonl"

    shard_path = episode_logging.worker_shard_path(base_path, 3)

    assert shard_path == (tmp_path / "episode_log_train_auton_17323" / "episode_log_train_auton_17323.worker03.jsonl")


def test_append_episode_log_creates_run_directory_and_worker_file(tmp_path):
    base_path = tmp_path / "episode_log_train_auton_17323.jsonl"

    for env_idx in (0, 1):
        episode_logging.append_episode_jsonl_log(
            base_path,
            epoch=1,
            global_steps=2,
            env_idx=env_idx,
            episode_index=4,
            turns=[],
            reward=1.0,
            info=None,
        )

    shard_path = episode_logging.worker_shard_path(base_path, 0)
    assert shard_path.is_file()
    assert episode_logging.worker_shard_path(base_path, 1).is_file()
    assert not base_path.exists()
    assert json.loads(shard_path.read_text())["episode_uid"] == "epoch1:step2:env0:episode4"


def test_action_summary_recognizes_readiness_and_pass_without_casting_a_vote():
    summary = episode_logging.parse_action_summary("<READY_TO_VOTE>")
    assert summary["readiness"] == ["ready_to_vote"]
    assert summary["votes"] == []
    summary = episode_logging.parse_action_summary("<PASS>")
    assert summary["pass_count"] == 1
    assert summary["group_messages"] == []


def test_legacy_episode_logs_identify_original_protocol():
    row = episode_logging.build_episode_log_row(
        epoch=1,
        global_steps=0,
        env_idx=0,
        episode_index=0,
        turns=[],
        reward=0,
        info=None,
    )
    assert row["protocol"] == "async_ticker"
