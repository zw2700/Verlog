"""Smoke test for the ported hiring_env dependency layer (no GPU, no verl trainer)."""
import numpy as np
from transformers import AutoTokenizer

from verl.envs import hiring_episode_logging  # noqa: F401  (import must succeed)
from verl.envs.hiring_env_wrapper import make_async_ticker_env


def main():
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3.5-0.8B", trust_remote_code=False)
    cfg = {
        "professor_ids": ["prof_1", "prof_2", "prof_3"],
        "students_per_batch": 5,
        "feature_dim": 5,
        "token_budget": 1000,
        "max_steps": 100,
        "vote_threshold": 0.5,
        "seed": 0,
        "prompt_length": 4096,
    }
    env = make_async_ticker_env(cfg, tokenizer=tok)
    print("[ok] env constructed:", type(env).__name__)
    print("    possible_agents:", getattr(env, "possible_agents", getattr(getattr(env, "env", None), "possible_agents", None)))

    obs, info = env.reset()
    # info is agent-keyed dict; each value carries active_agent/system_prompts
    first_info = next(iter(info.values())) if isinstance(info, dict) and info else info
    active = first_info.get("active_agent") if isinstance(first_info, dict) else None
    print(f"[ok] reset: obs_type={type(obs).__name__} active_agent={active} info_agents={list(info.keys()) if isinstance(info, dict) else None}")
    assert active is not None, "reset must surface an active_agent"
    assert isinstance(obs, list) and obs and obs[0].get("role"), "obs should be a chat-messages list"

    # step: active agent thinks then waits (no vote yet) — should advance the ticker, not end
    action = {active: {"text": "<THINK>Let me hear others first.</THINK><WAIT>", "metadata": {}}}
    obs2, reward, terminated, truncated, info2 = env.step(action)
    fi2 = next(iter(info2.values())) if isinstance(info2, dict) and info2 else info2
    active2 = fi2.get("active_agent") if isinstance(fi2, dict) else None
    print(f"[ok] step: reward={reward} terminated={terminated} truncated={truncated} next_active={active2}")
    assert active2 is not None
    print("ENV_SMOKE_OK")


if __name__ == "__main__":
    main()
