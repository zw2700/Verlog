# Copyright 2025 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Regression guard: the port's dual-discounting GAE must stay numerically
identical to the original Verlog (verl-0.6) implementation.

`_REF_gae_core` below is a FROZEN copy of verl-0.6 Verlog's
`compute_gae_advantage_return_core` (branch merge-jun26-merged). It pins the
port's `compute_gae_advantage_return_dual` to the original semantics forever: any
future edit to the port's turn/token GAE that changes results will fail here.

Provenance / how this was validated once against the live original repo:
  scratchpad/parity_dual_gae.py  (bit-for-bit across the same scenario grid)
The masked_whiten/mean/var stack was verified byte-identical between the two
repos, so the reference reuses the port's own verl_F for the final whiten.
"""
import numpy as np
import pytest
import torch

import verl.utils.torch_functional as verl_F
from verl.trainer.ppo.core_algos import compute_gae_advantage_return_dual


# ---------------- FROZEN verl-0.6 reference (verbatim math) ----------------
def _REF_gae_core(token_level_rewards, values, response_mask, dones, episode_structure,
                  token_gamma=1.0, step_gamma=1.0, token_lam=1.0, step_lam=1.0):
    with torch.no_grad():
        turn_values = values[:, 0].clone()
        turn_rewards = token_level_rewards.clone().sum(-1)
        turn_advantages = torch.zeros_like(turn_values)
        for ep_indices in episode_structure:
            ep_rewards = turn_rewards[ep_indices].clone()
            ep_values = turn_values[ep_indices].clone()
            ep_dones = dones[ep_indices].clone()
            T = len(ep_indices)
            ep_advantages = torch.zeros_like(ep_values)
            gae = 0
            for t in reversed(range(T)):
                if t == T - 1:
                    ep_advantages[t] = 0.0
                else:
                    next_value = ep_values[t + 1]
                    next_non_terminal = 1.0 - ep_dones[t] * 1.0
                    delta = ep_rewards[t] + step_gamma * next_value * next_non_terminal - ep_values[t]
                    gae = delta + step_gamma * step_lam * next_non_terminal * gae
                    ep_advantages[t] = gae
            turn_advantages[ep_indices] = ep_advantages
        nextvalues = torch.zeros_like(turn_values)
        lastgaelam = torch.zeros_like(turn_values)
        for ep_indices in episode_structure:
            ep_dones = dones[ep_indices].clone()
            ep_values = turn_values[ep_indices].clone()
            next_ep_values = torch.cat([ep_values[1:], torch.tensor([ep_values[-1] / step_gamma], device=ep_values.device)])
            next_ep_values[:-1] *= (1 - ep_dones[:-1] * 1.0)
            nextvalues[ep_indices] = next_ep_values * step_gamma
            ep_gaelam = turn_advantages[ep_indices].clone()
            next_ep_gaelam = torch.cat([ep_gaelam[1:], torch.zeros_like(ep_gaelam[:1])])
            next_ep_gaelam[:-1] *= (1 - ep_dones[:-1] * 1.0)
            lastgaelam[ep_indices] = next_ep_gaelam * step_gamma * step_lam
        advantages_reversed = []
        gen_len = token_level_rewards.shape[-1]
        for t in reversed(range(gen_len)):
            assert token_gamma == 1.0 and token_lam == 1.0
            token_adv = token_level_rewards[:, t:].sum(-1) + nextvalues - values[:, t] + lastgaelam
            advantages_reversed.append(token_adv)
        advantages = torch.stack(advantages_reversed[::-1], dim=1)
        returns = advantages + values
        advantages = verl_F.masked_whiten(advantages, response_mask)
    return advantages, returns


def _build_batch(n_envs, n_agents, turns_per_agent, resp_len, seed):
    g = torch.Generator().manual_seed(seed)
    episode_structure = []
    idx = 0
    for _e in range(n_envs):
        for _a in range(n_agents):
            chain = list(range(idx, idx + turns_per_agent + 1))  # +1 bootstrap row
            idx += turns_per_agent + 1
            episode_structure.append(chain)
    B = idx
    values = torch.randn(B, resp_len, generator=g)
    token_level_rewards = torch.zeros(B, resp_len)
    dones = torch.zeros(B)
    for chain in episode_structure:
        for pos, row in enumerate(chain):
            if pos == len(chain) - 1:
                continue
            tok = torch.randint(0, resp_len, (1,), generator=g).item()
            token_level_rewards[row, tok] = torch.randn(1, generator=g).item()
        dones[chain[-2]] = 1.0
    response_mask = torch.ones(B, resp_len)
    for r in range(B):
        cut = torch.randint(resp_len // 2, resp_len + 1, (1,), generator=g).item()
        response_mask[r, cut:] = 0.0
    return token_level_rewards, values, response_mask, dones, episode_structure


_SCENARIOS = [
    dict(n_envs=4, n_agents=3, turns_per_agent=3, resp_len=8, step_gamma=0.99, step_lam=0.95, seed=1),
    dict(n_envs=2, n_agents=3, turns_per_agent=5, resp_len=6, step_gamma=1.0, step_lam=1.0, seed=2),
    dict(n_envs=8, n_agents=3, turns_per_agent=2, resp_len=12, step_gamma=0.95, step_lam=0.90, seed=3),
    dict(n_envs=1, n_agents=3, turns_per_agent=10, resp_len=4, step_gamma=0.99, step_lam=0.5, seed=4),
    dict(n_envs=3, n_agents=1, turns_per_agent=4, resp_len=10, step_gamma=0.99, step_lam=0.95, seed=5),
]


@pytest.mark.parametrize("s", _SCENARIOS)
def test_dual_gae_matches_verl06_reference(s):
    """Port's gae_dual == frozen verl-0.6 core, bit-for-bit (step_lam_critic=None)."""
    tlr, val, rm, dn, es = _build_batch(s["n_envs"], s["n_agents"], s["turns_per_agent"], s["resp_len"], s["seed"])
    ref_adv, ref_ret = _REF_gae_core(tlr, val, rm, dn, es, step_gamma=s["step_gamma"], step_lam=s["step_lam"])
    port_adv, port_ret = compute_gae_advantage_return_dual(
        token_level_rewards=tlr, values=val, response_mask=rm, dones=dn,
        step_gamma=s["step_gamma"], step_lam=s["step_lam"], step_lam_critic=None, episode_structure=es,
    )
    assert torch.equal(ref_adv, port_adv), "actor advantages diverged from verl-0.6 reference"
    assert torch.equal(ref_ret, port_ret), "returns diverged from verl-0.6 reference"


def test_vc_ppo_decoupled_critic_is_additive():
    """step_lam_critic must leave actor advantages untouched and only change returns."""
    s = _SCENARIOS[0]
    tlr, val, rm, dn, es = _build_batch(s["n_envs"], s["n_agents"], s["turns_per_agent"], s["resp_len"], s["seed"])
    adv_n, ret_n = compute_gae_advantage_return_dual(
        token_level_rewards=tlr, values=val, response_mask=rm, dones=dn,
        step_gamma=s["step_gamma"], step_lam=s["step_lam"], step_lam_critic=None, episode_structure=es)
    adv_c, ret_c = compute_gae_advantage_return_dual(
        token_level_rewards=tlr, values=val, response_mask=rm, dones=dn,
        step_gamma=s["step_gamma"], step_lam=s["step_lam"], step_lam_critic=1.0, episode_structure=es)
    assert torch.equal(adv_n, adv_c), "decoupled critic must not change actor advantages"
    assert (ret_n - ret_c).abs().max().item() > 0, "decoupled critic must produce a different return target"
