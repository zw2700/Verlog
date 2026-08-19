import pytest
import torch
from omegaconf import OmegaConf

from verl import DataProto
from verl.trainer.ppo.ray_trainer import RayPPOTrainer, as_critic_input, without_critic_inputs


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


def test_actor_and_critic_views_route_disjoint_prompt_tensors():
    actor_ids = torch.tensor([[1, 2, 3]])
    critic_ids = torch.tensor([[7, 8, 9]])
    data = DataProto.from_dict(
        tensors={
            "prompts": actor_ids[:, :2],
            "input_ids": actor_ids,
            "attention_mask": torch.ones_like(actor_ids),
            "position_ids": torch.arange(3).unsqueeze(0),
            "critic_prompts": critic_ids[:, :2],
            "critic_input_ids": critic_ids,
            "critic_attention_mask": torch.ones_like(critic_ids),
            "critic_position_ids": torch.arange(3).unsqueeze(0),
            "responses": torch.tensor([[3]]),
        }
    )

    actor_view = without_critic_inputs(data)
    critic_view = as_critic_input(data)

    assert not any(key.startswith("critic_") for key in actor_view.batch.keys())
    assert torch.equal(actor_view.batch["input_ids"], actor_ids)
    assert not any(key.startswith("critic_") for key in critic_view.batch.keys())
    assert torch.equal(critic_view.batch["input_ids"], critic_ids)
    assert torch.equal(critic_view.batch["responses"], data.batch["responses"])
