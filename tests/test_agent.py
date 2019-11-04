from typing import Callable, List, Tuple

import pytest

from src.dialogus.agent import Agent


def test_echo_agent():
    def echo_skill(message: str, state: int) -> Tuple[List[str], int]:
        return [message], 0

    def skill_classifier(message: str) -> List[Callable[[str], Tuple[List[str], int]]]:
        return [echo_skill]

    agent = Agent(skill_classifier=skill_classifier)

    input_message = 'Hello'
    output_message = agent.answer_me(input_message)

    assert output_message == [input_message]


def test_duplicate_agent():
    def duplicate_skill(message: str, state: int) -> Tuple[List[str], int]:
        return [message * 2], 0

    def skill_classifier(message: str) -> List[Callable[[str], Tuple[List[str], int]]]:
        return [duplicate_skill]

    agent = Agent(skill_classifier=skill_classifier)

    input_message = 'Hello'
    output_message = agent.answer_me(input_message)

    assert output_message == ['HelloHello']


def test_error_type_of_skill_classifier():
    with pytest.raises(TypeError):
        Agent(skill_classifier=None)


def test_choice_of_skills():
    def greeting_skill(message: str, state: int) -> Tuple[List[str], int]:
        return ['Hi'], 0

    def parting_skill(message: str, state: int) -> Tuple[List[str], int]:
        return ['Bye'], 0

    def skill_classifier(message: str) -> List[Callable[[str], Tuple[List[str], int]]]:
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


def test_continuous_skill():
    def continuous_skill(message: str, state: int) -> Tuple[List[str], int]:
        if state == 0:
            return ['How old are you?'], 1
        if state == 1:
            return ['Ok'], 0

    def skill_classifier(message: str) -> List[Callable[[str], Tuple[List[str], int]]]:
        return [continuous_skill]

    agent = Agent(skill_classifier=skill_classifier)

    assert agent.answer_me('Hello') == ['How old are you?']
    assert agent.answer_me('23') == ['Ok']
