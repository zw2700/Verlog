"""Terminal reward ablations without changing observations or game mechanics."""

import math

from verl.envs.hiring_env.env import AsyncTickerAdmissionsEnv


class RewardComparisonAdmissionsEnv(AsyncTickerAdmissionsEnv):
    """Individual/group numerical rewards and individual/group binary optima.

    Binary refers to the terminal selection reward. Existing per-action penalties
    and trainer KL regularization are independent and remain configurable.
    """

    def __init__(self, config, tokenizer=None):
        super().__init__(config, tokenizer=tokenizer)
        self.reward_optimum_atol = float(config.get("reward_optimum_atol", 1e-9))
        if not math.isfinite(self.reward_optimum_atol) or self.reward_optimum_atol < 0:
            raise ValueError("reward_optimum_atol must be finite and nonnegative")
        if self.reward_mode not in {
            "individual", "group", "combined", "binary_individual", "binary_social_optimum"
        }:
            raise ValueError(f"Unsupported hiring reward mode: {self.reward_mode}")

    def _is_optimal(self, values, choice):
        return math.isclose(values[choice], max(values), rel_tol=0, abs_tol=self.reward_optimum_atol)

    def _rank_from_descending_values(self, values, item_idx):
        """Use the same roundoff tolerance for reported ranks and binary rewards."""
        selected = values[item_idx]
        return 1 + sum(
            value > selected and not math.isclose(
                value, selected, rel_tol=0, abs_tol=self.reward_optimum_atol
            )
            for value in values
        )

    def _calculate_rewards(self):
        if self.reward_mode not in {"binary_individual", "binary_social_optimum"}:
            return super()._calculate_rewards()
        rewards = dict.fromkeys(self.professor_ids, 0.0)
        if not self.episode_state["consensus_reached"]:
            return rewards
        choice = self._get_valid_final_choice()
        if choice is None:
            return rewards
        utilities = self._get_student_utilities_by_agent()
        if self.reward_mode == "binary_individual":
            return {agent: float(self._is_optimal(values, choice)) for agent, values in utilities.items()}
        success = self._is_optimal(self._get_collective_utilities(utilities), choice)
        return dict.fromkeys(self.professor_ids, float(success))
