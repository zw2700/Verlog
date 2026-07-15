"""Environment factory for the Verlog multi-agent rollout.

Minimal port for the async_ticker_admissions consensus game (the only env used by
the Qwen3.5 hiring-env RL task). Other Verlog envs (nle/crafter/babyai/...) are not
ported here — add branches lazily if needed.
"""


def make_env(env_name, task, config, render_mode=None, tokenizer=None):
    """Create an environment instance by name.

    Args:
        env_name (str): environment name (e.g. "async_ticker_admissions").
        task (str): task within the environment (unused for the consensus game).
        config: the full runtime config (Hydra/OmegaConf).
        render_mode: unused here.
        tokenizer: HF tokenizer, passed to the env for token-budget accounting.
    """
    if env_name == "async_ticker_admissions":
        from omegaconf import OmegaConf

        from verl.envs.hiring_env_wrapper import make_async_ticker_env

        env_config = getattr(config.envs, "env_config", config.envs)
        env_config_dict = OmegaConf.to_container(env_config, resolve=True)
        # Inject prompt_length so the env enforces a token-based trim budget on the
        # user observation, keeping the critical header (student table, vote tally) visible.
        try:
            env_config_dict["prompt_length"] = config.actor_rollout_ref.rollout.prompt_length
        except Exception:
            pass
        return make_async_ticker_env(env_config_dict, tokenizer=tokenizer)
    raise ValueError(
        f"Unknown environment: {env_name}. Only 'async_ticker_admissions' is ported on this branch."
    )
