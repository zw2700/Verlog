"""Unit test for the ported dual-discount GAE + multi-agent episode helpers."""
import numpy as np
import torch

from verl.trainer.ppo import core_algos
from verl.trainer.ppo.ray_trainer import (
    _has_agent_id,
    get_episode_structure,
    get_multiagent_episode_structure,
)


def test_helpers():
    # single-agent contiguous grouping
    assert get_episode_structure(np.array([0, 0, 0, 1, 1, 2])) == [[0, 1, 2], [3, 4], [5]]
    # multi-agent: 1 env, 3 profs x 2 turns; groups ordered by turn_id then index
    env_idx = np.array([0, 0, 0, 0, 0, 0])
    agent_id = np.array(["p1", "p1", "p2", "p2", "p3", "p3"])
    turn_id = np.array([1, 0, 0, 1, 1, 0])
    struct = sorted(tuple(g) for g in get_multiagent_episode_structure(env_idx, agent_id, turn_id))
    # p1 rows {0@t1,1@t0}->(1,0); p2 {2@t0,3@t1}->(2,3); p3 {4@t1,5@t0}->(5,4)
    assert struct == sorted([(1, 0), (2, 3), (5, 4)]), struct
    assert _has_agent_id({"agent_id": agent_id})
    assert not _has_agent_id({"agent_id": np.array([None, None])})
    assert not _has_agent_id({})
    print("[ok] helpers")
    return env_idx, agent_id, turn_id


def test_gae_dual(env_idx, agent_id, turn_id):
    struct = get_multiagent_episode_structure(env_idx, agent_id, turn_id)
    B, L = 6, 4
    rewards = torch.zeros(B, L)
    rewards[:, -1] = torch.tensor([1.0, 0.0, 0.5, 0.0, 2.0, 0.0])  # turn scalar reward on last token
    values = torch.randn(B, L, generator=torch.Generator().manual_seed(0))
    mask = torch.ones(B, L)
    dones = torch.tensor([0.0, 1.0, 0.0, 1.0, 0.0, 1.0])

    fn = core_algos.get_adv_estimator_fn("gae_dual")
    adv, ret = fn(
        token_level_rewards=rewards, values=values, response_mask=mask, dones=dones,
        step_gamma=0.99, step_lam=0.95, token_gamma=1.0, token_lam=1.0,
        episode_structure=struct,
    )
    assert adv.shape == (B, L) and ret.shape == (B, L), (adv.shape, ret.shape)
    assert torch.isfinite(adv).all() and torch.isfinite(ret).all()
    # whitened advantages should be ~zero-mean under the mask
    assert abs(adv.mean().item()) < 1e-4, adv.mean().item()
    print(f"[ok] gae_dual: adv{tuple(adv.shape)} finite, mean={adv.mean().item():.2e}")


if __name__ == "__main__":
    e, a, t = test_helpers()
    test_gae_dual(e, a, t)
    print("ALL_OK")
