"""Round adapter for inference-only repeated admissions sessions.

The outer sampling runner owns session termination and cumulative utility.
The base environment still terminates at the end of each individual round.
"""
from __future__ import annotations

import numpy as np
from functools import lru_cache

from verl.envs.hiring_env.env import AsyncTickerAdmissionsEnv


MINIMAL_SESSION_PROMPT = "You interact with the same professors over multiple turns. Previous public messages and decisions remain visible."


@lru_cache(maxsize=1)
def context_tokenizer(model, revision):
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(model, revision=revision, local_files_only=True)


class RepeatedAdmissionsRound(AsyncTickerAdmissionsEnv):
    def __init__(self, config, tokenizer=None):
        self.session_round = int(config["session_round"])
        self.context_token_limit = config.get("context_token_limit")
        self.context_tokenizer = None
        if self.context_token_limit:
            self.context_tokenizer = context_tokenizer(config["model"], config["model_revision"])
        self.fixed_preferences = config["fixed_preferences"]
        self.previous_public_rounds = config.get("previous_public_rounds", [])
        self.private_payoffs = config.get("private_payoffs", {})
        self.cumulative_utilities = config.get("cumulative_utilities", {})
        super().__init__(config, tokenizer=tokenizer)

    def _sample_professor_interests(self):
        # Consume the usual preference draws so the first-round student batch
        # matches the existing single-round experiment for the same seed.
        super()._sample_professor_interests()
        return {a: np.asarray(v).copy() for a, v in self.fixed_preferences.items()}

    def _build_chat_messages(self, agent_id):
        messages = super()._build_chat_messages(agent_id)
        messages[0] = {**messages[0], "content": messages[0]["content"] + "\n\n" + MINIMAL_SESSION_PROMPT}
        records = list(self.previous_public_rounds)
        omitted = False
        current = messages[1]["content"]
        while True:
            history = "\n\n".join(records) or "No previous public interaction included."
            notice = "Earlier public interaction omitted to fit the context window.\n" if omitted else ""
            prefix = (
                "PREVIOUS PUBLIC INTERACTION — completed decisions; old candidate indices and votes do not apply now:\n"
                + notice + history
                + "\n\nCURRENT DECISION — use only the candidates and current vote tally below:\n"
            )
            messages[1] = {**messages[1], "content": prefix + current}
            if self.context_tokenizer is None:
                break
            tokens = self.context_tokenizer.apply_chat_template(
                messages, tokenize=True, add_generation_prompt=True, enable_thinking=False)
            if len(tokens) <= self.context_token_limit:
                break
            if not records:
                raise ValueError("Current decision alone exceeds inference context limit")
            records.pop(0)
            omitted = True
        return messages


def public_round_record(row, round_number):
    """Keep public messages/votes/outcome, never private reasoning or utilities."""
    lines = ["Previous decision (completed):"]
    for turn in row["turns"]:
        actions = turn.get("actions") or {}
        for message in actions.get("group_messages", []):
            lines.append(f"{turn['agent']} said: {message}")
    # All final votes are public. Intermediate votes are retained in raw logs,
    # but omitted from this bounded memory to avoid repeated-vote spam.
    lines.append("Final votes: " + str(row.get("episode_state", {}).get("votes", {})))
    if row["consensus"]:
        chosen = row["chosen_student"]
        student = next(s for s in row["student_batch"] if s["index"] == chosen)
        lines.append(f"Unanimously selected past student {chosen}, public profile {student['profile_vector']}.")
    else:
        lines.append("No consensus; nobody received selection utility this round.")
    return "\n".join(lines)


def selection_utilities(row):
    if not row["consensus"]:
        return {agent: 0.0 for agent in row["professor_interests"]}
    chosen = next(s for s in row["student_batch"] if s["index"] == row["chosen_student"])
    return {agent: float(np.dot(prefs, chosen["profile_vector"]))
            for agent, prefs in row["professor_interests"].items()}
