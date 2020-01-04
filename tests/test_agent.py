from typing import List

import pytest

from dialogus import Agent, Skill


def test_echo_agent():
    class EchoSkill(Skill):
        def run(self, message: str):
            self.say(message)

    def skill_classifier(message: str) -> List[Skill]:
        return [EchoSkill()]

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('Bob')

    assert conversation.query('Hello') == ['Hello']


def test_duplicate_agent():
    class DuplicateSkill(Skill):
        def run(self, message: str):
            self.say(message * 2)

    def skill_classifier(message: str) -> List[Skill]:
        return [DuplicateSkill()]

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

    def skill_classifier(message: str) -> List[Skill]:
        skills = []

        if 'Hello' in message:
            skills.append(GreetingSkill())

        if 'Goodbye' in message:
            skills.append(PartingSkill())

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('Bob')

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
    conversation = agent.conversation_with_user('Bob')

    assert conversation.query('Hello') == ['What is your name?']
    assert conversation.query('Bob') == ['Nice to meet you Bob!']

    assert conversation.query('What about age?') == ['How old are you?']
    assert conversation.query('42') == ['Ok']

    assert conversation.query('Hello') == ['What is your name?']
    assert conversation.query('What about age?') == ['How old are you?']


def test_separation_of_agent_context_on_users(age_skill: Skill):
    def skill_classifier(message: str) -> List[Skill]:
        skills = []

        if 'age' in message:
            skills.append(age_skill)

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation_with_bob = agent.conversation_with_user('Bob')
    conversation_with_alice = agent.conversation_with_user('Alice')

    assert conversation_with_bob.query('What about age?') == ['How old are you?']
    assert conversation_with_alice.query('What about age?') == ['How old are you?']

    assert conversation_with_bob.query('42') == ['Ok']
    assert conversation_with_alice.query('42') == ['Ok']


def test_agent_query_without_conversation(age_skill: Skill):
    def skill_classifier(message: str) -> List[Skill]:
        skills = []

        if 'age' in message:
            skills.append(age_skill)

        return skills

    agent = Agent(skill_classifier=skill_classifier)

    assert agent.query('What about age?', 'Bob') == ['How old are you?']
    assert agent.query('42', 'Bob') == ['Ok']


def test_initial_message():
    class FriendNamesSkill(Skill):
        def run(self, message: str):
            your_name = message
            self.say(f'Your name is {your_name}')
            friend_name = self.ask("Enter your friend's name")
            self.say(f'Your friend is {friend_name}')

    def skill_classifier(message: str) -> List[Skill]:
        skills = []

        if 'Bob' in message:
            skills.append(FriendNamesSkill())

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('Bob')

    conversation.query('Bob')
    assert conversation.query('Alex') == ['Your friend is Alex']


def test_multi_answers():
    class MoodSkill(Skill):
        def run(self, message: str):
            self.say('Hello')
            self.say('Good day!')
            mood = self.ask('How are you?')
            ...

    def skill_classifier(message: str) -> List[Skill]:
        return [MoodSkill()]

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('Bob')

    answers = conversation.query('Hello')
    assert answers == ['Hello', 'Good day!', 'How are you?']
