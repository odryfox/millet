from typing import List

import pytest

from src.dialogus.agent import Agent, Skill


def test_echo_agent():
    class EchoSkill(Skill):
        def run(self, message: str) -> List[str]:
            return [message]

    def skill_classifier(message: str) -> List[Skill]:
        return [EchoSkill()]

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('user_1')

    assert conversation.query('Hello') == ['Hello']


def test_duplicate_agent():
    class DuplicateSkill(Skill):
        def run(self, message: str) -> List[str]:
            return [message * 2]

    def skill_classifier(message: str) -> List[Skill]:
        return [DuplicateSkill()]

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('user_1')

    assert conversation.query('Hello') == ['HelloHello']


def test_error_type_of_skill_classifier():
    with pytest.raises(TypeError):
        Agent(skill_classifier=None)


def test_choice_of_skills():
    class GreetingSkill(Skill):
        def run(self, message: str) -> List[str]:
            return ['Hi']

    class PartingSkill(Skill):
        def run(self, message: str) -> List[str]:
            return ['Bye']

    def skill_classifier(message: str) -> List[Skill]:
        skills = []

        if 'Hello' in message:
            skills.append(GreetingSkill())

        if 'Goodbye' in message:
            skills.append(PartingSkill())

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('user_1')

    assert conversation.query('Hello') == ['Hi']
    assert conversation.query('Goodbye') == ['Bye']
    assert conversation.query('Hello. Goodbye.') == ['Hi', 'Bye']
    assert conversation.query('How are you?') == []


def test_continuous_skill(meeting_skill: Skill, age_skill: Skill):
    def skill_classifier(message: str) -> List[Skill]:
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


def test_separation_of_agent_context_on_users(age_skill: Skill):
    def skill_classifier(message: str) -> List[Skill]:
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


def test_agent_query_without_conversation(age_skill: Skill):
    def skill_classifier(message: str) -> List[Skill]:
        skills = []

        if 'age' in message:
            skills.append(age_skill)

        return skills

    agent = Agent(skill_classifier=skill_classifier)

    assert agent.query('What about age?', 'user_1') == ['How old are you?']
    assert agent.query('23', 'user_1') == ['Ok']
