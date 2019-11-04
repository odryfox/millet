from typing import Callable, List

import pytest

from src.dialogus.agent import Agent


def test_echo_agent():
    def echo_skill(message: str) -> List[str]:
        return [message]

    def skill_classifier(message: str) -> List[Callable[[str], List[str]]]:
        return [echo_skill]

    agent = Agent(skill_classifier=skill_classifier)

    input_message = 'Hello'
    output_message = agent.answer_me(input_message)

    assert output_message == [input_message]


def test_duplicate_agent():
    def duplicate_skill(message: str) -> List[str]:
        return [message * 2]

    def skill_classifier(message: str) -> List[Callable[[str], List[str]]]:
        return [duplicate_skill]

    agent = Agent(skill_classifier=skill_classifier)

    input_message = 'Hello'
    output_message = agent.answer_me(input_message)

    assert output_message == ['HelloHello']


def test_error_type_of_skill_classifier():
    with pytest.raises(TypeError):
        Agent(skill_classifier=None)


def test_choice_of_skills():
    def greeting_skill(message: str) -> List[str]:
        return ['Hi']

    def parting_skill(message: str) -> List[str]:
        return ['Bye']

    def skill_classifier(message: str) -> List[Callable[[str], List[str]]]:
        skills = []
        if 'Hello' in message:
            skills.append(greeting_skill)

        if 'Goodbye' in message:
            skills.append(parting_skill)

        return skills

    agent = Agent(skill_classifier=skill_classifier)

    input_message = 'Hello'
    output_message = agent.answer_me(input_message)

    assert output_message == ['Hi']

    input_message = 'Goodbye'
    output_message = agent.answer_me(input_message)

    assert output_message == ['Bye']

    input_message = 'Hello. Goodbye.'
    output_message = agent.answer_me(input_message)

    assert output_message == ['Hi', 'Bye']

    input_message = 'How are you?'
    output_message = agent.answer_me(input_message)

    assert output_message == []
