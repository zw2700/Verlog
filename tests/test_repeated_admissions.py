import unittest

from scripts import rollout_frontier as rf
from scripts.repeated_admissions import RepeatedAdmissionsRound, public_round_record


class RepeatedGameTests(unittest.TestCase):
    def config(self, seed=0, round_number=1):
        return {**rf.DEFAULT_ENV_CONFIG, "seed": seed, "vote_threshold": 1.0,
                "session_round": round_number, "session_rounds": 5,
                "fixed_preferences": {"prof_1": [0, 1, 2, 3, 4],
                                      "prof_2": [4, 3, 2, 1, 0],
                                      "prof_3": [2, 0, 1, 4, 3]}}

    def test_unanimity_and_fresh_round(self):
        env = RepeatedAdmissionsRound(self.config())
        _, info = env.reset()
        students = rf.episode_logging.json_safe(env.student_batch)
        for turn in range(3):
            agent = rf.flatten_info(info)["active_agent"]
            _, _, term, trunc, info = env.step({agent: "<THINK>agree</THINK><VOTE>0</VOTE>"})
            self.assertEqual(rf.is_done(term, trunc), turn == 2)
        later = RepeatedAdmissionsRound(self.config(seed=1000, round_number=2))
        later.reset()
        self.assertEqual(rf.episode_logging.json_safe(later.professor_interests), self.config()["fixed_preferences"])
        self.assertNotEqual(rf.episode_logging.json_safe(later.student_batch), students)
        self.assertEqual(later.episode_state["votes"], {})
        self.assertEqual(later.episode_state["tokens_used"], 0)
        self.assertEqual(later.episode_state["step_count"], 0)

    def test_public_memory_and_private_payoffs(self):
        row = {"turns": [{"agent": "prof_1", "output": "SECRET_THOUGHT", "utilities": "SECRET_UTILITY",
                          "actions": {"group_messages": ["PUBLIC_PROPOSAL"], "votes": [0]}}],
               "episode_state": {"votes": {"prof_1": 0}}, "consensus": False}
        public = public_round_record(row, 1)
        self.assertIn("PUBLIC_PROPOSAL", public)
        self.assertNotIn("SECRET", public)
        config = {**self.config(round_number=2), "previous_public_rounds": [public],
                  "private_payoffs": {"prof_1": [1.234567], "prof_2": [9.876543]},
                  "cumulative_utilities": {"prof_1": 1.234567, "prof_2": 9.876543}}
        env = RepeatedAdmissionsRound(config)
        messages, _ = env.reset()
        text = str(messages)
        self.assertIn("PUBLIC_PROPOSAL", text)
        self.assertNotIn("1.234567", text)
        self.assertNotIn("9.876543", text)
        self.assertNotIn("round 2 of 5", text)
        self.assertNotIn("80%", text)
        self.assertNotIn("final round", text)
        self.assertIn("CURRENT DECISION", text)
        self.assertIn("multiple turns", text)
        self.assertIn("100% agreement", text)

    def test_hidden_horizon_is_reproducible_and_unbounded(self):
        from scripts.rollout_repeated_comparison import sample_session_lengths
        lengths = sample_session_lengths(200)
        self.assertEqual(lengths, sample_session_lengths(200))
        self.assertGreater(max(lengths), 10)
        self.assertIn(1, lengths)
        self.assertEqual(sample_session_lengths(20, 0), [1] * 20)

    def test_first_round_scenario_matches_single_round(self):
        base = rf.AsyncTickerAdmissionsEnv({**rf.DEFAULT_ENV_CONFIG, "seed": 9})
        base.reset()
        preferences = rf.episode_logging.json_safe(base.professor_interests)
        students = rf.episode_logging.json_safe(base.student_batch)
        env = RepeatedAdmissionsRound({**self.config(seed=9), "fixed_preferences": preferences})
        env.reset()
        self.assertEqual(rf.episode_logging.json_safe(env.student_batch), students)


if __name__ == "__main__":
    unittest.main()
