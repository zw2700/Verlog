import pytest
from omegaconf import OmegaConf

from verl.trainer.ppo.ray_trainer import RayPPOTrainer


class _Tracking:
    instances = []

    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        self.finish_calls = []
        self.instances.append(self)

    def finish(self, exit_code=0):
        self.finish_calls.append(exit_code)


def _trainer(monkeypatch, fit_impl):
    monkeypatch.setattr("verl.utils.tracking.Tracking", _Tracking)
    _Tracking.instances.clear()

    trainer = RayPPOTrainer.__new__(RayPPOTrainer)
    trainer.config = OmegaConf.create(
        {
            "trainer": {
                "project_name": "test-project",
                "experiment_name": "test-run",
                "logger": ["wandb"],
            }
        }
    )
    trainer.config_provenance = {"primary_config": "train_auton"}
    trainer._fit = fit_impl
    return trainer


def test_fit_finishes_tracking_with_success_exit_code(monkeypatch):
    trainer = _trainer(monkeypatch, lambda logger: "complete")

    assert trainer.fit() == "complete"

    tracking = _Tracking.instances[0]
    assert tracking.finish_calls == [0]
    assert tracking.init_kwargs["config"]["config_provenance"] == {"primary_config": "train_auton"}


def test_fit_finishes_tracking_with_failure_exit_code(monkeypatch):
    def fail(_logger):
        raise RuntimeError("training failed")

    trainer = _trainer(monkeypatch, fail)

    with pytest.raises(RuntimeError, match="training failed"):
        trainer.fit()

    assert _Tracking.instances[0].finish_calls == [1]
