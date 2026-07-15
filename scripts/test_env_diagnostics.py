"""Drive the hiring env to consensus and confirm the re-added RL diagnostics are emitted."""
from transformers import AutoTokenizer

from verl.envs.hiring_env_wrapper import make_async_ticker_env


def active_of(info):
    fi = next(iter(info.values())) if isinstance(info, dict) and info else info
    return (fi.get("active_agent") if isinstance(fi, dict) else None), fi


def main():
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3.5-0.8B", trust_remote_code=False)
    cfg = dict(professor_ids=["prof_1", "prof_2", "prof_3"], students_per_batch=5, feature_dim=5,
               token_budget=2000, max_steps=60, vote_threshold=0.5, seed=1, prompt_length=4096)
    env = make_async_ticker_env(cfg, tok)
    obs, info = env.reset()
    active, _ = active_of(info)

    flat = None
    for _ in range(60):
        action = {active: {"text": "<THINK>vote 0</THINK><VOTE>0</VOTE>", "metadata": {}}}
        obs, reward, terminated, truncated, info = env.step(action)
        active, fi = active_of(info)
        done = (any(terminated.values()) if isinstance(terminated, dict) else terminated) or \
               (any(truncated.values()) if isinstance(truncated, dict) else truncated)
        if isinstance(fi, dict) and fi.get("metrics"):
            flat = fi["metrics"]
        if done:
            break

    assert flat is not None, "no flattened metrics emitted (episode never ended)"
    diag = {k: v for k, v in flat.items() if k.startswith("diagnostics/")}
    print("[diagnostics keys]")
    for k in sorted(diag):
        print(f"   {k} = {diag[k]}")
    for req in ["diagnostics/optimal_surfaced", "diagnostics/maj_optimal_rate",
                "diagnostics/reward_maj", "diagnostics/reward_other",
                "diagnostics/reward_maj_suboptimal", "diagnostics/coalition_size"]:
        assert req in diag, f"missing {req}"
    print("consensus_reached:", flat.get("negotiation/consensus_reached"),
          "chosen_rank_global:", flat.get("outcome/chosen_student_rank_global"))
    print("DIAG_SMOKE_OK")


if __name__ == "__main__":
    main()
