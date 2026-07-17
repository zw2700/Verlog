"""Deterministic single-repo env driver. Run with the repo root as argv[1] so its
local `verl/` shadows any editable install. Seeds global np.random, runs a fixed
action script against AsyncTickerAdmissionsEnv, and dumps the reward trajectory as
JSON so two repos can be diffed. cap=None => original-default behaviour.
"""
import sys, os, json

REPO = sys.argv[1]
REWARD_MODE = sys.argv[2] if len(sys.argv) > 2 else "individual"
os.chdir(REPO)
sys.path.insert(0, REPO)

import numpy as np
from verl.envs.hiring_env.env import AsyncTickerAdmissionsEnv

SEED = 12345
np.random.seed(SEED)

config = {
    "professor_ids": ["prof_1", "prof_2", "prof_3"],
    "students_per_batch": 5,
    "feature_dim": 5,
    "token_budget": 500,
    "vote_threshold": 0.5,
    "max_steps": 50,
    "reward_mode": REWARD_MODE,
    "utility_mode": "linear",
    "randomize_turn_order": False,   # deterministic, no RNG for turn order
    "format_penalty": 0.1,
    "invalid_action_penalty": 0.1,
    "format_penalty_cap": None,      # original-default => reward-identical path
    "seed": SEED,
}

env = AsyncTickerAdmissionsEnv(config, tokenizer=None)
np.random.seed(SEED)          # re-seed right before reset so batch/interests are fixed
env.reset()

# Fixed action script — same strings fed to both repos. Mixes a discuss and a
# malformed action (both trigger the format/invalid penalty path) with votes that
# drive 3-of-3 consensus on student 0.
ACTIONS = [
    "<THINK>weighing options</THINK><GROUP>I think student 0 looks strong.</GROUP>",  # discuss -> format penalty
    "<THINK>ok</THINK><VOTE>0</VOTE>",
    "no tags here at all",                                                            # malformed -> penalty
    "<THINK>ok</THINK><VOTE>0</VOTE>",
    "<THINK>ok</THINK><VOTE>0</VOTE>",
    "<THINK>ok</THINK><VOTE>0</VOTE>",
    "<THINK>ok</THINK><VOTE>0</VOTE>",
    "<THINK>ok</THINK><VOTE>0</VOTE>",
]

trajectory = []
done_all = False
for i, act in enumerate(ACTIONS):
    if done_all:
        break
    active = env.episode_state["active_agent"]
    obs, rewards, terms, truncs, infos = env.step(act)
    trajectory.append({
        "i": i,
        "active": active,
        "rewards": {k: float(v) for k, v in sorted(rewards.items())},
        "term": {k: bool(v) for k, v in sorted(terms.items())},
        "trunc": {k: bool(v) for k, v in sorted(truncs.items())},
    })
    done_all = all(terms.values()) or all(truncs.values())

out = {
    "reward_mode": REWARD_MODE,
    "professor_interests": {k: [int(x) for x in np.asarray(v).tolist()]
                            for k, v in sorted(env.professor_interests.items())},
    "students": [[round(float(x), 12) for x in s["profile_vector"]] for s in env.student_batch],
    "consensus_reached": bool(env.episode_state["consensus_reached"]),
    "consensus_choice": env.episode_state["consensus_choice"],
    "votes": {k: v for k, v in sorted((env.episode_state.get("votes") or {}).items())},
    "trajectory": trajectory,
}
print("PARITY_JSON_BEGIN")
print(json.dumps(out, sort_keys=True))
print("PARITY_JSON_END")
