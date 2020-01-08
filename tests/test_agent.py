from typing import List, Type

import pytest

from dialogus import Agent, Skill
from dialogus.context import RAMAgentContext


def test_echo_agent():
    class EchoSkill(Skill):
        def run(self, message: str):
            self.say(message)

    def skill_classifier(message: str) -> List[Type[Skill]]:
        return [EchoSkill]

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('Bob')

    assert conversation.query('Hello') == ['Hello']


def test_duplicate_agent():
    class DuplicateSkill(Skill):
        def run(self, message: str):
            self.say(message * 2)

    def skill_classifier(message: str) -> List[Type[Skill]]:
        return [DuplicateSkill]

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('Bob')

    assert conversation.query('Hello') == ['HelloHello']


def test_error_type_of_skill_classifier():
    with pytest.raises(TypeError):
        Agent(skill_classifier=None)


def test_choice_of_skills():
    class GreetingSkill(Skill):
        def run(self, message: str):
            self.say('Hi')

    class PartingSkill(Skill):
        def run(self, message: str):
            self.say('Bye')

    def skill_classifier(message: str) -> List[Type[Skill]]:
        skills = []

        if 'Hello' in message:
            skills.append(GreetingSkill)

        if 'Goodbye' in message:
            skills.append(PartingSkill)

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('Bob')

    assert conversation.query('Hello') == ['Hi']
    assert conversation.query('Goodbye') == ['Bye']
    assert conversation.query('Hello. Goodbye.') == ['Hi', 'Bye']
    assert conversation.query('How are you?') == []


def test_continuous_skill(meeting_skill_class: Type[Skill], age_skill_class: Type[Skill]):
    def skill_classifier(message: str) -> List[Type[Skill]]:
        skills = []

        if 'Hello' in message:
            skills.append(meeting_skill_class)

        if 'age' in message:
            skills.append(age_skill_class)

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('Bob')

    assert conversation.query('Hello') == ['What is your name?']
    assert conversation.query('Bob') == ['Nice to meet you Bob!']

    assert conversation.query('What about age?') == ['How old are you?']
    assert conversation.query('42') == ['Ok']


def test_separation_context_on_users(age_skill_class: Type[Skill]):
    def skill_classifier(message: str) -> List[Type[Skill]]:
        skills = []

        if 'age' in message:
            skills.append(age_skill_class)

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation_with_bob = agent.conversation_with_user('Bob')
    conversation_with_alice = agent.conversation_with_user('Alice')

    assert conversation_with_bob.query('What about age?') == ['How old are you?']
    assert conversation_with_alice.query('What about age?') == ['How old are you?']

    assert conversation_with_bob.query('42') == ['Ok']
    assert conversation_with_alice.query('42') == ['Ok']


def test_query_without_conversation(age_skill_class: Type[Skill]):
    def skill_classifier(message: str) -> List[Type[Skill]]:
        skills = []

        if 'age' in message:
            skills.append(age_skill_class)

        return skills

    agent = Agent(skill_classifier=skill_classifier)

    assert agent.query('What about age?', 'Bob') == ['How old are you?']
    assert agent.query('42', 'Bob') == ['Ok']


def test_default_context():
    agent = Agent(skill_classifier=lambda message: [])
    assert isinstance(agent.context, RAMAgentContext)
