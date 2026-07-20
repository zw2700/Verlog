from omegaconf import OmegaConf

from verl.trainer.main_ppo import _build_config_provenance, _resolved_config_changes


def test_resolved_config_changes_records_changed_added_and_removed_values():
    original = {
        "model_path": "Qwen/Qwen3-4B",
        "trainer": {"save_freq": -1, "deprecated": True},
    }
    overridden = {
        "model_path": "Qwen/Qwen2.5-3B-Instruct",
        "trainer": {"save_freq": 20, "new_option": "enabled"},
    }

    assert _resolved_config_changes(original, overridden) == {
        "model_path": {
            "change_type": "changed",
            "original": "Qwen/Qwen3-4B",
            "overridden": "Qwen/Qwen2.5-3B-Instruct",
        },
        "trainer.deprecated": {
            "change_type": "removed",
            "original": True,
            "overridden": None,
        },
        "trainer.new_option": {
            "change_type": "added",
            "original": None,
            "overridden": "enabled",
        },
        "trainer.save_freq": {
            "change_type": "changed",
            "original": -1,
            "overridden": 20,
        },
    }


def test_build_config_provenance_saves_original_config_and_exact_overrides():
    original = OmegaConf.create(
        {
            "tag": "base",
            "model_path": "Qwen/Qwen3-4B",
            "trainer": {"experiment_name": "unscripted_auton_base_123"},
        }
    )
    overridden = OmegaConf.create(
        {
            "tag": "qwen2p5",
            "model_path": "Qwen/Qwen2.5-3B-Instruct",
            "trainer": {"experiment_name": "unscripted_auton_qwen2p5_123"},
        }
    )
    task_overrides = ["tag=qwen2p5", "model_path=Qwen/Qwen2.5-3B-Instruct"]

    provenance = _build_config_provenance(
        original_config=original,
        overridden_config=overridden,
        primary_config="train_auton",
        task_overrides=task_overrides,
    )

    assert provenance["primary_config"] == "train_auton"
    assert provenance["hydra_task_overrides"] == task_overrides
    assert provenance["original_config"] == OmegaConf.to_container(original, resolve=True)
    assert provenance["resolved_changes"]["tag"] == {
        "change_type": "changed",
        "original": "base",
        "overridden": "qwen2p5",
    }
    assert provenance["resolved_changes"]["trainer.experiment_name"] == {
        "change_type": "changed",
        "original": "unscripted_auton_base_123",
        "overridden": "unscripted_auton_qwen2p5_123",
    }
