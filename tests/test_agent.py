from typing import Callable, List, Tuple

import pytest

from src.dialogus.agent import Agent


def test_echo_agent():
    def echo_skill(message: str, state: int) -> Tuple[List[str], int]:
        return [message], 0

    def skill_classifier(message: str) -> List[Callable[[str], Tuple[List[str], int]]]:
        return [echo_skill]

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('user_1')

    assert conversation.query('Hello') == ['Hello']


def test_duplicate_agent():
    def duplicate_skill(message: str, state: int) -> Tuple[List[str], int]:
        return [message * 2], 0

    def skill_classifier(message: str) -> List[Callable[[str], Tuple[List[str], int]]]:
        return [duplicate_skill]

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('user_1')

    assert conversation.query('Hello') == ['HelloHello']


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
    conversation = agent.conversation_with_user('user_1')

    assert conversation.query('Hello') == ['Hi']
    assert conversation.query('Goodbye') == ['Bye']
    assert conversation.query('Hello. Goodbye.') == ['Hi', 'Bye']
    assert conversation.query('How are you?') == []


def test_continuous_skill():
    def age_skill(message: str, state: int) -> Tuple[List[str], int]:
        if state == 0:
            return ['How old are you?'], 1
        if state == 1:
            return ['Ok'], 0

    def meeting_skill(message: str, state: int) -> Tuple[List[str], int]:
        if state == 0:
            return ['What is your name?'], 1
        if state == 1:
            return [f'Nice to meet you {message}!'], 0

    def skill_classifier(message: str) -> List[Callable[[str], Tuple[List[str], int]]]:
        skills = []
        if 'Hello' in message:
            skills.append(meeting_skill)

        if 'age' in message:
            skills.append(age_skill)

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('user_1')

    assert conversation.query('Hello') == ['What is your name?']
    assert conversation.query('John') == ['Nice to meet you John!']

    assert conversation.query('What about age?') == ['How old are you?']
    assert conversation.query('23') == ['Ok']

    assert conversation.query('Hello') == ['What is your name?']
    assert conversation.query('What about age?') == ['How old are you?']


def test_separation_of_agent_context_on_users():
    def age_skill(message: str, state: int) -> Tuple[List[str], int]:
        if state == 0:
            return ['How old are you?'], 1
        if state == 1:
            return ['Ok'], 0

    def skill_classifier(message: str) -> List[Callable[[str], Tuple[List[str], int]]]:
        skills = []

        if 'age' in message:
            skills.append(age_skill)

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation_with_user_1 = agent.conversation_with_user('user_1')
    conversation_with_user_2 = agent.conversation_with_user('user_2')

    assert conversation_with_user_1.query('What about age?') == ['How old are you?']
    assert conversation_with_user_2.query('What about age?') == ['How old are you?']

    assert conversation_with_user_1.query('23') == ['Ok']
    assert conversation_with_user_2.query('25') == ['Ok']


def test_agent_query_without_conversation():
    def age_skill(message: str, state: int) -> Tuple[List[str], int]:
        if state == 0:
            return ['How old are you?'], 1
        if state == 1:
            return ['Ok'], 0

    def skill_classifier(message: str) -> List[Callable[[str], Tuple[List[str], int]]]:
        skills = []

        if 'age' in message:
            skills.append(age_skill)

        return skills

    agent = Agent(skill_classifier=skill_classifier)

    assert agent.query('What about age?', 'user_1') == ['How old are you?']
    assert agent.query('23', 'user_1') == ['Ok']
