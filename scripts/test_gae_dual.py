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


def test_decoupled_critic_lambda():
    """VC-PPO decoupled-GAE: step_lam_critic changes the critic RETURN target, not the advantage.

    Uses a single length-4 (env, agent) chain (3 real turns + 1 bootstrap) so step_lam actually
    bites — with only 1 real turn the future-GAE term vanishes and step_lam has no effect.
    """
    struct = [[0, 1, 2, 3]]  # one chain: turns 0,1,2 real, turn 3 = value-carrier bootstrap
    B, L = 4, 4
    rewards = torch.zeros(B, L)
    rewards[:, -1] = torch.tensor([1.0, 0.5, 2.0, 0.0])  # per-turn scalar reward on last token
    values = torch.randn(B, L, generator=torch.Generator().manual_seed(1))
    mask = torch.ones(B, L)
    dones = torch.tensor([0.0, 0.0, 0.0, 0.0])
    core = core_algos.compute_gae_advantage_return_dual_core
    kw = dict(token_level_rewards=rewards, values=values, response_mask=mask, dones=dones,
              episode_structure=struct, step_gamma=0.99)

    adv_c, ret_c = core(step_lam=0.95, step_lam_critic=None, **kw)       # coupled (current)
    adv_d, ret_d = core(step_lam=0.95, step_lam_critic=1.0, **kw)        # VC-PPO decoupled
    adv_e, ret_e = core(step_lam=0.95, step_lam_critic=0.95, **kw)       # explicit == step_lam

    # advantage (actor) must be identical regardless of critic lambda
    assert torch.allclose(adv_c, adv_d, atol=1e-5), "critic-lambda must NOT change the actor advantage"
    # step_lam_critic == step_lam recovers coupled returns
    assert torch.allclose(ret_c, ret_e, atol=1e-5), "step_lam_critic==step_lam must equal coupled"
    # decoupled (lam=1) returns should actually differ from coupled (lam=0.95)
    assert not torch.allclose(ret_c, ret_d, atol=1e-4), "step_lam_critic=1.0 should change the return target"
    assert torch.isfinite(ret_d).all()
    print(f"[ok] decoupled critic lambda: adv unchanged, returns differ "
          f"(coupled mean={ret_c.mean():.3f} vs decoupled mean={ret_d.mean():.3f})")


if __name__ == "__main__":
    e, a, t = test_helpers()
    test_gae_dual(e, a, t)
    test_decoupled_critic_lambda()
    print("ALL_OK")
