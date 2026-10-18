"""Opt-in deliberation, collective closure, and sealed-ballot hiring protocol.

The submodule's async ticker protocol stays unchanged. Actor observations use
an explicit visibility filter; privileged episode info remains research logging
metadata, just as in the original environment, and must never become a prompt.
"""

from __future__ import annotations

import math
import random
import re
from collections import Counter
from copy import deepcopy
from typing import Any

from verl.envs.hiring_env.history_manager import HistoryManager
from verl.envs.hiring_reward_modes import RewardComparisonAdmissionsEnv


class DeliberationHistory(HistoryManager):
    """Apply ownership before message type, including for vote-shaped events."""

    def add_private_action(self, agent_id, text, ticker_time, token_count, **fields):
        self._all_messages.append(
            {
                "agent_id": agent_id,
                "text": text,
                "ticker_time": ticker_time,
                "token_count": token_count,
                **fields,
                "private": True,
            }
        )

    def _get_visible_messages_for_agent(self, agent_id):
        visible = []
        for event in self._all_messages:
            if event.get("private"):
                if event["agent_id"] == agent_id:
                    visible.append(event)
            elif event["message_type"] in {"communication", "wait"}:
                visible.append(event)
        # Insertion order is the protocol's chronology; private reasoning length
        # must not reorder messages or expose another professor's thinking time.
        return visible


class DeliberationVotingAdmissionsEnv(RewardComparisonAdmissionsEnv):
    """Round-robin messages -> simultaneous readiness check -> one ballot.

    Simultaneous means choices are collected against the same public transcript,
    without showing earlier submissions, even though model calls are sequential.
    Only GROUP content spends the discussion budget. Invalid actions consume one
    opportunity, preventing malformed outputs from stalling a finite episode.
    """

    def __init__(self, config, tokenizer=None):
        # Use an independent scheduling RNG so ordering does not consume draws
        # from the baseline's scenario generator.
        base_config = {**config, "randomize_turn_order": False}
        super().__init__(base_config, tokenizer=tokenizer)
        n = len(self.professor_ids)
        if n < 2 or len(set(self.professor_ids)) != n:
            raise ValueError("deliberation_voting requires at least two distinct professor IDs")
        options = config.get("deliberation", {})
        unknown_options = set(options) - {"max_rounds", "readiness_quorum", "communication_enabled"}
        if unknown_options:
            raise ValueError(f"Unknown deliberation options: {sorted(unknown_options)}")
        self.max_discussion_rounds = options.get("max_rounds", 10)
        quorum = options.get("readiness_quorum")
        self.readiness_quorum = n - 1 if quorum is None else quorum
        self.communication_enabled = options.get("communication_enabled", True)
        if not isinstance(self.communication_enabled, bool):
            raise ValueError("deliberation.communication_enabled must be a boolean")
        if not isinstance(self.max_discussion_rounds, int) or self.max_discussion_rounds < 1:
            raise ValueError("deliberation.max_rounds must be a positive integer")
        if not isinstance(self.readiness_quorum, int) or not 1 <= self.readiness_quorum <= n:
            raise ValueError("deliberation.readiness_quorum must be an integer between 1 and the group size")
        if not math.isfinite(self.vote_threshold) or not 0 < self.vote_threshold <= 1:
            raise ValueError("vote_threshold must be in (0, 1]")
        self.decision_quorum = max(n // 2 + 1, math.ceil(n * self.vote_threshold))
        if self.token_budget <= 0:
            raise ValueError("token_budget must be positive")
        # A custom baseline system prompt would contradict the new action space.
        if self.system_prompt is not None:
            raise ValueError("deliberation_voting uses its own phase-aware system prompt")
        self._order_rng = random.Random(self.seed_value)
        self.phase = "discussion"
        self.discussion_round = 1
        self._round_order: list[str] = []
        self._phase_position = 0
        self._readiness: dict[str, bool] = {}
        self._ballots: dict[str, int | None] = {}
        self._readiness_results: list[dict[str, Any]] = []
        self._closure_reason: str | None = None
        self._phase_turns = dict.fromkeys(("discussion", "readiness", "ballot"), 0)

    def build_system_prompt(self, professor_id, preference_vector=None):
        communication_notice = (
            "PUBLIC COMMUNICATION IS DISABLED in this condition: GROUP messages are retained only "
            "in your private history and are not delivered to other professors. They still consume "
            "the same discussion budget; you may PASS. Readiness counts and budget status remain public.\n"
            if not self.communication_enabled
            else ""
        )
        payoff = {
            "individual": "Your selection reward is your own utility for the selected student.",
            "group": (
                "Every professor's selection reward is the SUM of all professors' utilities for the selected student."
            ),
            "combined": (
                f"Your selection reward is {self.reward_alpha} * your own utility + "
                f"{1 - self.reward_alpha} * the SUM of all professors' utilities for the selected student."
            ),
            "binary_individual": (
                "Your selection reward is 1 if the selected student maximizes YOUR utility, otherwise 0. Ties count."
            ),
            "binary_social_optimum": (
                "Every professor's selection reward is 1 if the selected student maximizes the SUM of utilities, "
                "otherwise 0. Ties count."
            ),
        }[self.reward_mode]
        return (
            f"You are Professor {professor_id}, a member of an admissions committee.\n"
            f"Committee members: {', '.join(self.professor_ids)}. Choose among {self.students_per_batch} students.\n"
            "Your utility table is private. Other professors have their own private utility tables.\n"
            f"PAYOFFS: {payoff} No agreement gives everyone 0 selection reward.\n"
            "PROCEDURE:\n"
            "1. DISCUSSION: Each professor gets one opportunity per round to send <GROUP>message</GROUP> "
            "or <PASS>. The initial speaking order is shuffled; the first speaker rotates each round. "
            "Statements and promises in messages do not cast ballots or bind anyone.\n"
            f"{communication_notice}"
            "2. READINESS: After a complete round, each professor independently submits <READY_TO_VOTE> "
            "or <CONTINUE_DISCUSSION>. Submissions stay private; the count is announced only after all respond. "
            f"At least {self.readiness_quorum} ready signals close discussion. Signals reset each check.\n"
            f"3. DEADLINE: Discussion closes after {self.max_discussion_rounds} rounds or when its "
            f"{self.token_budget}-token public-message budget is exhausted. Either deadline opens voting.\n"
            "4. BALLOT: Each professor submits exactly one binding <VOTE>N</VOTE>, "
            f"where N is a student index from 0 to {self.students_per_batch - 1}. "
            "All professors vote independently against the same frozen public discussion. "
            "Ballots stay private, including after the election. Earlier submissions are hidden. "
            "The result is determined ONLY after every professor's ballot opportunity, "
            f"and requires {self.decision_quorum} matching valid ballots. Otherwise there is no agreement. "
            "An invalid/missing ballot is an abstention. There is one ballot round.\n"
            "FORMAT: Begin every response with <THINK>private reasoning</THINK>, followed by exactly "
            "one action allowed in the current phase. Your THINK blocks and private actions are visible "
            "only to you in later observations. You may pass without sending a message. "
            "Only GROUP content spends the shared discussion budget; THINK, readiness, and ballots do not.\n"
            f"Malformed responses cost {self.format_penalty}; invalid actions cost {self.invalid_action_penalty}. "
            "An invalid discussion action becomes a pass; invalid readiness means continue. "
            "There is no reward for speaking, passing, readiness, or discussion length."
        )

    def reset(self):
        self.phase = "discussion"
        self.discussion_round = 1
        self._phase_position = 0
        self._readiness = {}
        self._ballots = {}
        self._readiness_results = []
        self._closure_reason = None
        self._phase_turns = dict.fromkeys(("discussion", "readiness", "ballot"), 0)
        # super.reset builds an initial observation, so give it the filtered
        # empty history before rebuilding with our independent round order.
        super().reset()
        self.history_manager = DeliberationHistory(self.professor_ids)
        self._round_order = list(self.professor_ids)
        self._order_rng.shuffle(self._round_order)
        self.episode_state["active_agent"] = self._round_order[0]
        self._sync_state()
        return self._transition_result(dict.fromkeys(self.professor_ids, 0.0), False)

    def _sync_state(self):
        self.episode_state.update(
            protocol="deliberation_voting",
            phase=self.phase,
            discussion_round=self.discussion_round,
            discussion_closure_reason=self._closure_reason,
            readiness_results=deepcopy(self._readiness_results),
            message_history=self.history_manager.get_episode_message_history_snapshot(),
        )

    def _build_chat_messages(self, agent_id):
        if agent_id not in self.professor_ids:
            raise ValueError(f"unknown professor id {agent_id!r}")
        system = self.build_system_prompt(agent_id)
        instructions = {
            "discussion": "<GROUP>message</GROUP> or <PASS>",
            "readiness": "<READY_TO_VOTE> or <CONTINUE_DISCUSSION>",
            "ballot": "<VOTE>N</VOTE>",
            "done": "Episode finished. No further action.",
        }[self.phase]
        table = []
        for student in self.student_batch:
            utility = self._calculate_utility_for_student(self.professor_interests[agent_id], student["profile_vector"])
            abilities = f" {student['profile_vector']}" if self.show_ability_vectors else ""
            table.append(f"  {student['name']} | {utility:.6g} |{abilities}")
        public_features = " | Public ability vector" if self.show_ability_vectors else " (abilities hidden)"
        readiness = (
            "; ".join(f"round {result['round']}: {result['ready_count']} ready" for result in self._readiness_results)
            or "No completed readiness checks."
        )
        header = (
            f"=== YOUR TURN: {agent_id} ===\n"
            f"PHASE: {self.phase}; discussion round {self.discussion_round}/{self.max_discussion_rounds}\n"
            f"Allowed action after <THINK>...</THINK>: {instructions}\n"
            f"Discussion tokens used: {self.episode_state['tokens_used']}/{self.token_budget}\n"
            f"STUDENTS — Student | Your PRIVATE Utility{public_features}\n"
            + "\n".join(table)
            + f"\nCOMPLETED READINESS CHECKS: {readiness}\n"
        )
        if self.phase == "done":
            choice = self.episode_state["consensus_choice"]
            outcome = "no agreement" if choice is None else f"selected student {choice}"
            # Canonical ordering prevents a tally's dict insertion order from
            # revealing which candidate was first mentioned in sealed ballots.
            tally = dict(sorted(self._vote_counts().items()))
            header += f"ELECTION RESULT: {outcome}; tally {tally}.\n"
        history = []
        for event in self.history_manager._get_visible_messages_for_agent(agent_id):
            marker = "YOUR PRIVATE" if event.get("private") else "PUBLIC"
            history.append(f"[{marker} {event['message_type']}; {event['agent_id']}] {event['text']}")

        # Preserve the phase/utility header and newest visible events. Filtering
        # happens BEFORE trimming, so hidden events cannot affect the prompt.
        def render():
            return header + "\nVISIBLE HISTORY (chronological):\n" + "\n".join(history)

        def fits(text):
            if self.prompt_length is not None and self.tokenizer is not None:
                available = self.prompt_length - self._count_tokens(system) - 25
                return self._count_tokens(text) <= available
            return self.max_prompt_words is None or len(text.split()) <= self.max_prompt_words

        self.last_prompt_truncated = False
        while history and not fits(render()):
            history.pop(0)
            self.last_prompt_truncated = True
        user = render()
        if not fits(user):
            raise ValueError("prompt budget cannot fit the deliberation phase and private utility table")
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    def _parse_protocol_action(self, text):
        """Fail closed: never rebroadcast malformed or unfinished reasoning."""
        match = re.fullmatch(r"\s*<THINK>(.*?)</THINK>\s*(.*?)\s*", text, re.DOTALL | re.IGNORECASE)
        if match is None:
            return {"thought": text, "action": "", "malformed": True, "invalid": False}
        thought, action = match.groups()
        result = {"thought": thought, "action": action, "malformed": False, "invalid": False}
        group = re.fullmatch(r"<GROUP>(.*?)</GROUP>", action, re.DOTALL | re.IGNORECASE)
        vote = re.fullmatch(r"<VOTE>(.*?)</VOTE>", action, re.DOTALL | re.IGNORECASE)
        if self.phase == "discussion" and group:
            content = group[1].strip()
            # Reject nested protocol tags; they must not provide a second path
            # for accidentally publishing a THINK block.
            if content and not re.search(r"</?(?:THINK|GROUP)\b", content, re.IGNORECASE):
                result["message"] = content
            else:
                result["invalid"] = True
        elif self.phase == "discussion" and re.fullmatch(r"<PASS\s*/?>", action, re.IGNORECASE):
            pass
        elif self.phase == "readiness" and re.fullmatch(r"<READY_TO_VOTE\s*/?>", action, re.IGNORECASE):
            result["ready"] = True
        elif self.phase == "readiness" and re.fullmatch(r"<CONTINUE_DISCUSSION\s*/?>", action, re.IGNORECASE):
            result["ready"] = False
        elif self.phase == "ballot" and vote:
            value = vote[1].strip()
            if value.isascii() and value.isdigit() and 0 <= int(value) < len(self.student_batch):
                result["choice"] = int(value)
            else:
                result["invalid"] = True
        else:
            # A valid-looking action in the wrong phase is invalid. Multiple
            # action tags or stray text are also malformed.
            result["invalid"] = True
            known_action = re.fullmatch(
                r"<(GROUP|VOTE)>.*?</\1>|<(?:PASS|READY_TO_VOTE|CONTINUE_DISCUSSION)\s*/?>",
                action,
                re.DOTALL | re.IGNORECASE,
            )
            result["malformed"] = known_action is None
        return result

    def _extract_action(self, action, active_agent):
        if isinstance(action, dict):
            if active_agent in action:
                action = action[active_agent]
            elif "text" not in action:
                raise ValueError("action must belong to the active professor")
            if isinstance(action, dict):
                action = action.get("text", "")
        return "" if action is None else str(action)

    def step(self, action):
        if self.phase == "done":
            raise RuntimeError("episode finished; call reset before stepping again")
        actor = self.episode_state["active_agent"]
        parsed = self._parse_protocol_action(self._extract_action(action, actor))
        phase = self.phase
        self.episode_state["step_count"] += 1
        turn = self.episode_state["step_count"]
        self._phase_turns[phase] += 1
        if parsed["thought"]:
            self.history_manager.add_think(actor, parsed["thought"], turn, self._count_tokens(parsed["thought"]))
        fields = {"phase": phase, "malformed": parsed["malformed"], "invalid": parsed["invalid"]}
        if phase == "discussion" and "message" in parsed:
            # Admit only messages that fit; an oversized message becomes a
            # private invalid action, so the hard budget cannot be bypassed.
            cost = self._count_tokens(parsed["message"])
            if cost <= self.token_budget - self.episode_state["tokens_used"]:
                self.episode_state["tokens_used"] += cost
                if self.communication_enabled:
                    self.history_manager.add_public(
                        actor,
                        f"<GROUP>{parsed['message']}</GROUP>",
                        turn,
                        self._count_tokens(parsed["action"]),
                        "communication",
                        fields,
                    )
                else:
                    # Keep the action and its budget cost without delivering
                    # text to other professors or counting it as public speech.
                    self.history_manager.add_private_action(
                        actor,
                        f"<GROUP>{parsed['message']}</GROUP>",
                        turn,
                        self._count_tokens(parsed["action"]),
                        message_type="wait",
                        withheld_message=True,
                        **fields,
                    )
            else:
                parsed["invalid"] = fields["invalid"] = True
                self.history_manager.add_private_action(
                    actor,
                    "Message exceeds remaining discussion budget; treated as a pass.",
                    turn,
                    self._count_tokens(parsed["action"]),
                    message_type="wait",
                    **fields,
                )
        else:
            message_type = "vote" if phase == "ballot" and "choice" in parsed else "wait"
            if phase == "readiness":
                self._readiness[actor] = parsed.get("ready", False)
            elif phase == "ballot":
                self._ballots[actor] = parsed.get("choice")
            if parsed["malformed"] or parsed["invalid"]:
                text = "Invalid response; this opportunity was consumed without a valid action."
            else:
                text = parsed["action"]
            choice_fields = {"choice": parsed["choice"]} if "choice" in parsed else {}
            self.history_manager.add_private_action(
                actor,
                text,
                turn,
                self._count_tokens(parsed["action"]),
                message_type=message_type,
                **fields,
                **choice_fields,
            )
        self._advance_phase()
        self._sync_state()
        done = self.phase == "done"
        rewards = self._calculate_rewards() if done else dict.fromkeys(self.professor_ids, 0.0)
        rewards[actor] -= self.format_penalty * parsed["malformed"]
        rewards[actor] -= self.invalid_action_penalty * parsed["invalid"]
        return self._transition_result(rewards, done)

    def _open_ballot(self, reason):
        self.phase = "ballot"
        self._closure_reason = reason
        self._phase_position = 0

    def _vote_counts(self):
        return Counter(choice for choice in self._ballots.values() if choice is not None)

    def _advance_phase(self):
        self._phase_position += 1
        n = len(self.professor_ids)
        if self.phase == "discussion":
            if self.episode_state["tokens_used"] >= self.token_budget:
                self._open_ballot("token_budget")
            elif self._phase_position == n:
                # Give the final round its readiness check too; the deadline
                # opens voting afterward regardless of the readiness result.
                self.phase = "readiness"
                self._readiness = {}
                self._phase_position = 0
        elif self.phase == "readiness" and self._phase_position == n:
            ready_count = sum(self._readiness.values())
            self._readiness_results.append({"round": self.discussion_round, "ready_count": ready_count})
            if ready_count >= self.readiness_quorum:
                self._open_ballot("readiness")
            elif self.discussion_round >= self.max_discussion_rounds:
                self._open_ballot("round_limit")
            else:
                self.discussion_round += 1
                self._round_order = self._round_order[1:] + self._round_order[:1]
                self.phase = "discussion"
                self._phase_position = 0
        elif self.phase == "ballot" and self._phase_position == n:
            # No running tally or early terminal event, even if the first two
            # submissions already suffice. This is a simultaneous decision.
            self.episode_state["votes"] = {
                agent: choice for agent, choice in self._ballots.items() if choice is not None
            }
            winner = next(
                (choice for choice, count in self._vote_counts().items() if count >= self.decision_quorum), None
            )
            self.episode_state["consensus_reached"] = winner is not None
            self.episode_state["consensus_choice"] = winner
            self.phase = "done"
        if self.phase != "done":
            self.episode_state["active_agent"] = self._round_order[self._phase_position]

    def _transition_result(self, rewards, done):
        actor = self.episode_state["active_agent"]
        observations = self._build_chat_messages(actor)
        # These are privileged trainer/logger diagnostics, never actor input.
        base_info = {
            "active_agent": actor,
            "agent_idx": self.professor_ids.index(actor),
            "episode_state": deepcopy(self.episode_state),
            "agent_rewards": rewards,
            "student_batch": self.student_batch,
            "professor_interests": self.professor_interests,
        }
        if done:
            metrics = self._calculate_episode_metrics(rewards)
            base_info.update(episode_metrics=metrics, metrics=self._flatten_metrics_for_logging(metrics))
        infos = {agent: deepcopy(base_info) for agent in self.professor_ids}
        if self.episode_state["step_count"] == 0:
            return observations, infos
        return (
            observations,
            rewards,
            dict.fromkeys(self.professor_ids, done),
            dict.fromkeys(self.professor_ids, False),
            infos,
        )

    def _calculate_episode_metrics(self, rewards):
        metrics = super()._calculate_episode_metrics(rewards)
        metrics["negotiation_dynamics"]["turns_to_consensus"] = (
            self.episode_state["step_count"] if self.episode_state["consensus_reached"] else None
        )
        # Sequential vote-following metrics have no behavioral meaning for a
        # simultaneous ballot. No voter observes a running tally.
        metrics["negotiation_dynamics"]["second_vote_matches_first"] = None
        metrics["voting_dynamics"]["minority_persistence_total"] = None
        for values in metrics["voting_dynamics"]["by_agent"].values():
            values["minority_persistence"] = None
        for key in metrics["influence"]:
            if "plurality" in key:
                metrics["influence"][key] = None
        metrics["deliberation"] = {
            "rounds": self.discussion_round,
            "readiness_checks": len(self._readiness_results),
            **{f"{phase}_turns": count for phase, count in self._phase_turns.items()},
            "valid_ballots": len(self.episode_state["votes"]),
            "abstentions": len(self.professor_ids) - len(self.episode_state["votes"]),
            "communication_enabled": int(self.communication_enabled),
            "withheld_messages": sum(
                bool(event.get("withheld_message")) for event in self.history_manager._all_messages
            ),
            **{
                f"closed_by_{reason}": int(self._closure_reason == reason)
                for reason in ("readiness", "token_budget", "round_limit")
            },
        }
        return metrics

    def _flatten_metrics_for_logging(self, metrics):
        flat = super()._flatten_metrics_for_logging(metrics)
        flat.update({f"deliberation/{key}": value for key, value in metrics["deliberation"].items()})
        return flat
