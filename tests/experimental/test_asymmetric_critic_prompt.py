import copy

import pytest

from verl.experimental.agent_loop.tool_agent_loop import build_critic_messages


MESSAGES = [
    {"role": "system", "content": "Actor-private system prompt."},
    {"role": "user", "content": "Public history and current observation."},
]
CONTEXT = {
    "professor_ids": ["prof_1", "prof_2"],
    "student_utilities": {
        "prof_1": [1.25, 2.5],
        "prof_2": [3.75, 4.0],
    },
}


def test_actor_visible_critic_prompt_is_unchanged_copy():
    original = copy.deepcopy(MESSAGES)
    critic_messages = build_critic_messages(MESSAGES, mode="actor_visible")

    assert critic_messages == original
    assert critic_messages is not MESSAGES
    assert MESSAGES == original


def test_all_utilities_are_added_only_to_critic_system_prompt():
    original = copy.deepcopy(MESSAGES)
    critic_messages = build_critic_messages(MESSAGES, mode="all_utilities", critic_context=CONTEXT)

    assert MESSAGES == original
    assert critic_messages[1] == MESSAGES[1]
    system_prompt = critic_messages[0]["content"]
    assert "<CRITIC_ONLY_PRIVILEGED_STATE>" in system_prompt
    assert "student\tprof_1\tprof_2" in system_prompt
    assert "0\t1.2500\t3.7500" in system_prompt
    assert "1\t2.5000\t4.0000" in system_prompt


def test_all_utilities_requires_aligned_vectors():
    bad_context = copy.deepcopy(CONTEXT)
    bad_context["student_utilities"]["prof_2"] = [3.75]

    with pytest.raises(ValueError, match="same number"):
        build_critic_messages(MESSAGES, mode="all_utilities", critic_context=bad_context)
