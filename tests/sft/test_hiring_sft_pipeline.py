from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import pytest

from scripts.rollout_frontier import Completion
from scripts.sft.build_dataset import (
    DatasetBuildError,
    build_decision_rows,
    choose_validation_scenarios,
    compact_teacher_output,
    episode_sort_key,
    select_exact_scenario_count,
)
from scripts.sft.collect_teacher_rollouts import assert_scenario_fingerprints, collection_summary
from scripts.sft.compare_evaluations import assert_comparable, exact_mcnemar_pvalue, paired_primary_report
from scripts.sft.evaluate_policy import summarize_evaluation
from scripts.sft.make_sweep_datasets import rank_scenarios, subset_scenario_ids
from scripts.sft.rollout_core import (
    DEFAULT_ENV_CONFIG,
    env_config_hash,
    is_clean_socially_optimal,
    load_dotenv_file,
    make_scenario_id,
    run_captured_episode,
)


class CharacterTokenizer:
    """Small reversible tokenizer sufficient for pipeline and environment tests."""

    def encode(self, text: str, add_special_tokens: bool = False) -> list[int]:
        del add_special_tokens
        return [ord(character) for character in text]

    def decode(self, token_ids: list[int], skip_special_tokens: bool = True) -> str:
        del skip_special_tokens
        return "".join(chr(token_id) for token_id in token_ids)

    def apply_chat_template(
        self,
        messages: list[dict[str, Any]],
        *,
        tokenize: bool,
        add_generation_prompt: bool,
        enable_thinking: bool = False,
        **_: Any,
    ) -> str | list[int]:
        del enable_thinking
        rendered = "".join(f"<{message['role']}>{message['content']}</{message['role']}>" for message in messages)
        if add_generation_prompt:
            rendered += "<assistant>"
        return self.encode(rendered) if tokenize else rendered


class FixedVoteClient:
    def complete(self, messages: list[dict[str, str]]) -> Completion:
        prompt_tokens = sum(len(message["content"]) for message in messages)
        text = "<THINK>The group should coordinate on student 1.</THINK>\n<VOTE>1</VOTE>"
        return Completion(
            text=text,
            prompt_tokens=prompt_tokens,
            response_tokens=len(text),
            raw={"choices": [{"finish_reason": "stop"}]},
        )


def make_episode(seed: int = 7, *, attempt: int = 0) -> dict[str, Any]:
    config_hash = env_config_hash(DEFAULT_ENV_CONFIG)
    output = (
        "<THINK>Student 1 is plausible. The aggregate utilities clearly favor student 2.</THINK>\n"
        "<GROUP>I favor student 2.</GROUP>\n<VOTE>2</VOTE>"
    )
    return {
        "scenario_seed": seed,
        "scenario_id": make_scenario_id(config_hash, seed),
        "env_config_hash": config_hash,
        "episode_uid": f"episode-{seed}-{attempt}",
        "attempt": attempt,
        "consensus": True,
        "socially_optimal": True,
        "social_welfare_efficiency": 1.0,
        "tokens_used": 32,
        "llm_output_tokens": 100,
        "teacher_model": "haiku",
        "agent_turn_stats": {
            "prof_1": {"format_errors": 0, "invalid_errors": 0},
        },
        "turns": [
            {
                "episode_turn_id": 0,
                "agent": "prof_1",
                "messages": [
                    {"role": "system", "content": "Negotiate and vote."},
                    {"role": "user", "content": "Student utilities and current state."},
                ],
                "output": output,
                "action_text": "<GROUP>I favor student 2.</GROUP>\n<VOTE>2</VOTE>",
                "completion_truncated": False,
            }
        ],
    }


def test_config_hash_and_scenario_identity_are_stable() -> None:
    first = env_config_hash(DEFAULT_ENV_CONFIG)
    reordered = dict(reversed(list(DEFAULT_ENV_CONFIG.items())))
    assert env_config_hash(reordered) == first
    changed = {**DEFAULT_ENV_CONFIG, "token_budget": 501}
    assert env_config_hash(changed) != first
    assert make_scenario_id(first, 11) == f"{first}:seed11"


def test_dotenv_loader_handles_quotes_comments_and_environment_precedence(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / "rollout.env"
    env_file.write_text(
        '# comment\nPROVIDER=cmu-gateway\nMODEL="model with spaces" # inline comment\nexport TEMPERATURE=0.7\nEMPTY=\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("PROVIDER", "already-exported")
    for name in ("MODEL", "TEMPERATURE", "EMPTY"):
        monkeypatch.delenv(name, raising=False)

    loaded = load_dotenv_file(env_file)
    assert loaded["PROVIDER"] == "cmu-gateway"
    assert os.environ["PROVIDER"] == "already-exported"
    assert os.environ["MODEL"] == "model with spaces"
    assert os.environ["TEMPERATURE"] == "0.7"
    assert os.environ["EMPTY"] == ""


def test_clean_filter_is_strict() -> None:
    episode = make_episode()
    assert is_clean_socially_optimal(episode)

    truncated = make_episode()
    truncated["turns"][0]["completion_truncated"] = True
    assert not is_clean_socially_optimal(truncated)

    invalid = make_episode()
    invalid["agent_turn_stats"]["prof_1"]["invalid_errors"] = 1
    assert not is_clean_socially_optimal(invalid)


def test_compact_think_preserves_action_exactly() -> None:
    tokenizer = CharacterTokenizer()
    raw_output = make_episode()["turns"][0]["output"]
    compact = compact_teacher_output(raw_output, tokenizer, max_think_tokens=64)
    assert compact.startswith("<THINK>The aggregate utilities clearly favor student 2.</THINK>")
    assert compact.endswith("<GROUP>I favor student 2.</GROUP>\n<VOTE>2</VOTE>")


def test_compactor_uses_final_well_formed_block_without_fragment_tail() -> None:
    tokenizer = CharacterTokenizer()
    raw = """<THINK>
Let me analyze the situation. Student 4 may be useful.
</THINKING>
<THINK>
I need to analyze my options:
- If I vote for Student 1, we get consensus immediately
- This guarantees my utility versus risking further negotiation

The pragmatic move is to vote for Student 1 to close out consensus quickly and secure my best outcome.
</THINK>
<VOTE>1</VOTE>"""
    compact = compact_teacher_output(raw, tokenizer, max_think_tokens=256)
    assert compact == (
        "<THINK>The pragmatic move is to vote for Student 1 to close out consensus quickly "
        "and secure my best outcome.</THINK>\n<VOTE>1</VOTE>"
    )
    assert "risking further negotiation" not in compact


def test_compactor_prefers_substantive_proposal_over_meta_sentence() -> None:
    tokenizer = CharacterTokenizer()
    raw = """<THINK>
My top choices are Students 0 and 2. Student 0 has strong CompBio, while Student 2 is more balanced.
I'll propose Student 2 as it's more versatile, but I'm open to negotiation.
I should keep this concise and invite discussion.
</THINK>
<GROUP>I'd like to propose Student 2. What are your thoughts?</GROUP>"""
    compact = compact_teacher_output(raw, tokenizer, max_think_tokens=256)
    assert compact == (
        "<THINK>I'll propose Student 2 as it's more versatile, but I'm open to negotiation.</THINK>\n"
        "<GROUP>I'd like to propose Student 2. What are your thoughts?</GROUP>"
    )
    assert "keep this concise" not in compact


def test_compactor_recovers_qwen_underscore_think_typo() -> None:
    tokenizer = CharacterTokenizer()
    raw = (
        "<_THINK>Student 1 has the highest utility, so I should propose it.</THINK>"
        "<GROUP>I propose Student 1.</GROUP>"
    )
    compact = compact_teacher_output(raw, tokenizer, max_think_tokens=256)
    assert compact.startswith("<THINK>")
    assert "<_THINK>" not in compact
    assert compact.endswith("<GROUP>I propose Student 1.</GROUP>")


def test_compactor_aligns_student_rationale_with_emitted_vote() -> None:
    tokenizer = CharacterTokenizer()
    raw = """<THINK>
1. Switch to Student 0 for consensus
Student 2 is my clear preference with the highest utility.
I should introduce Student 2 as the balanced alternative.
</THINK>
<GROUP>I propose Student 2.</GROUP><VOTE>2</VOTE>"""
    compact = compact_teacher_output(raw, tokenizer, max_think_tokens=256)
    assert "Student 2" in compact
    assert "Switch to Student 0" not in compact
    assert compact.endswith("<GROUP>I propose Student 2.</GROUP><VOTE>2</VOTE>")


def test_build_decision_rows_captures_exact_prompt_and_target() -> None:
    episode = make_episode()
    rows = build_decision_rows(
        episode,
        CharacterTokenizer(),
        target_format="raw",
        max_think_tokens=64,
        max_prompt_tokens=4096,
        max_response_tokens=512,
        max_sequence_tokens=4608,
        target_enable_thinking=False,
    )
    assert len(rows) == 1
    assert [message["role"] for message in rows[0]["messages"]] == ["system", "user", "assistant"]
    assert rows[0]["messages"][-1]["content"] == episode["turns"][0]["output"]
    assert rows[0]["scenario_seed"] == episode["scenario_seed"]

    with pytest.raises(DatasetBuildError, match="response"):
        build_decision_rows(
            episode,
            CharacterTokenizer(),
            target_format="raw",
            max_think_tokens=64,
            max_prompt_tokens=4096,
            max_response_tokens=8,
            max_sequence_tokens=4608,
            target_enable_thinking=False,
        )


def test_episode_selection_prefers_shorter_trajectory() -> None:
    shorter = make_episode(attempt=1)
    longer = make_episode(attempt=0)
    longer["turns"] = longer["turns"] * 2
    assert min([longer, shorter], key=episode_sort_key) is shorter


def test_exact_scenario_selection_is_deterministic_and_requires_enough_data() -> None:
    selected = [(make_episode(seed), [{"seed": seed}]) for seed in range(10)]
    first = select_exact_scenario_count(selected, count=4, selection_seed=7)
    second = select_exact_scenario_count(list(reversed(selected)), count=4, selection_seed=7)
    assert [row[0]["scenario_id"] for row in first] == [row[0]["scenario_id"] for row in second]
    with pytest.raises(ValueError, match="need 11"):
        select_exact_scenario_count(selected, count=11, selection_seed=7)


def test_fractional_validation_split_is_exact_and_scenario_level() -> None:
    selected = [(make_episode(seed), [{"seed": seed}]) for seed in range(10)]
    first = choose_validation_scenarios(
        selected,
        validation_fraction=0.2,
        validation_seeds=None,
        split_seed=123,
    )
    second = choose_validation_scenarios(
        list(reversed(selected)),
        validation_fraction=0.2,
        validation_seeds=None,
        split_seed=123,
    )
    assert first == second
    assert len(first) == 2

    explicit = choose_validation_scenarios(
        selected,
        validation_fraction=0.9,
        validation_seeds={3, 8},
        split_seed=123,
    )
    assert explicit == {make_episode(seed)["scenario_id"] for seed in (3, 8)}


def test_sweep_subsets_are_deterministic_and_nested() -> None:
    scenarios = [f"scenario-{index}" for index in range(316)]
    ranked = rank_scenarios(reversed(scenarios), subset_seed=7)
    assert ranked == rank_scenarios(scenarios, subset_seed=7)
    raw25 = subset_scenario_ids(ranked, 0.25)
    raw50 = subset_scenario_ids(ranked, 0.50)
    raw100 = subset_scenario_ids(ranked, 1.0)
    assert len(raw25) == 79
    assert len(raw50) == 158
    assert len(raw100) == 316
    assert raw25 < raw50 < raw100


def test_collection_and_evaluation_summaries() -> None:
    successful = make_episode(seed=1)
    failed = make_episode(seed=2)
    failed["consensus"] = False
    failed["socially_optimal"] = False
    failed["social_welfare_efficiency"] = 0.0
    rows = [successful, failed]

    collection = collection_summary(rows, [1, 2, 3])
    assert collection["successful_scenarios"] == 1
    assert collection["scenario_success_rate"] == pytest.approx(1 / 3)

    evaluation = summarize_evaluation(rows)
    assert evaluation["episodes"] == 2
    assert evaluation["socially_optimal_rate"] == 0.5
    assert evaluation["socially_optimal_rate_95ci"][0] < 0.5
    assert evaluation["socially_optimal_rate_95ci"][1] > 0.5


def test_collection_rejects_changed_scenario_fingerprints() -> None:
    rows = [
        {"scenario_seed": 3, "scenario_fingerprint": "first"},
        {"scenario_seed": 3, "scenario_fingerprint": "second"},
    ]
    with pytest.raises(ValueError, match="fingerprint changed"):
        assert_scenario_fingerprints(rows)


def test_paired_evaluation_report_uses_locked_seed_outcomes() -> None:
    baseline = {
        seed: {"socially_optimal": outcome}
        for seed, outcome in enumerate((True, False, True, False, False))
    }
    candidate = {
        seed: {"socially_optimal": outcome}
        for seed, outcome in enumerate((True, True, False, True, False))
    }
    report = paired_primary_report(
        baseline,
        candidate,
        bootstrap_replicates=200,
        bootstrap_seed=3,
    )
    assert report["both_socially_optimal"] == 1
    assert report["candidate_only_socially_optimal"] == 2
    assert report["baseline_only_socially_optimal"] == 1
    assert report["paired_rate_difference"] == pytest.approx(0.2)
    assert exact_mcnemar_pvalue(2, 1) == 1.0


def test_paired_comparison_checks_realized_scenario_fingerprints() -> None:
    baseline = {0: {**make_episode(0), "scenario_fingerprint": "scenario-a"}}
    candidate = {0: {**make_episode(0), "scenario_fingerprint": "scenario-b"}}
    with pytest.raises(ValueError, match="realized scenario differs"):
        assert_comparable({"base": baseline, "candidate": candidate})


def test_captured_rollout_uses_target_tokenizer_and_saves_messages() -> None:
    tokenizer = CharacterTokenizer()
    episode = run_captured_episode(
        client=FixedVoteClient(),
        env_config=DEFAULT_ENV_CONFIG,
        scenario_seed=19,
        attempt=0,
        target_tokenizer=tokenizer,
        target_tokenizer_name="character-test-tokenizer",
        target_enable_thinking=False,
        provider_name="fake",
        model_name="fixed-vote",
        temperature=0.0,
        top_p=1.0,
        top_k=-1,
        max_output_tokens=512,
    )
    assert episode["scenario_seed"] == 19
    assert episode["env_config_hash"] == env_config_hash(DEFAULT_ENV_CONFIG)
    assert episode["consensus"]
    # With three professors and a 0.5 vote threshold, two matching votes reach consensus.
    assert len(episode["turns"]) == 2
    assert all(turn["messages"][-1]["role"] == "user" for turn in episode["turns"])
    assert all(turn["target_prompt_tokens"] > 0 for turn in episode["turns"])
    assert all(turn["target_response_tokens"] > 0 for turn in episode["turns"])
    assert episode["teacher_top_p"] == 1.0
    assert episode["teacher_top_k"] == -1
    assert episode["scenario_fingerprint"]


def test_threaded_rollouts_keep_seeded_scenarios_stable() -> None:
    tokenizer = CharacterTokenizer()

    def capture(seed: int) -> tuple[int, str]:
        episode = run_captured_episode(
            client=FixedVoteClient(),
            env_config=DEFAULT_ENV_CONFIG,
            scenario_seed=seed,
            attempt=0,
            target_tokenizer=tokenizer,
            target_tokenizer_name="character-test-tokenizer",
            target_enable_thinking=False,
            provider_name="fake",
            model_name="fixed-vote",
            temperature=0.0,
        )
        return seed, episode["scenario_fingerprint"]

    seeds = [31, 32, 33, 31, 32, 33]
    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(capture, seeds))
    by_seed: dict[int, set[str]] = {}
    for seed, fingerprint in results:
        by_seed.setdefault(seed, set()).add(fingerprint)
    assert all(len(fingerprints) == 1 for fingerprints in by_seed.values())
