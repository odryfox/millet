from typing import List, Type

import pytest
from redis import Redis

from millet import Agent, Skill
from millet.context import RAMAgentContext, RedisAgentContext


def test_answer_agent(bob_id: str):
    class EchoSkill(Skill):
        def start(self, initial_message: str):
            self.say(initial_message)

    def skill_classifier(message: str) -> List[Skill]:
        return [EchoSkill()]

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user(bob_id)

    assert conversation.query("Hello") == ["Hello"]


def test_incorrect_skill_classifier():
    with pytest.raises(TypeError):
        Agent(skill_classifier=None)


def test_choice_of_skills(bob_id: str):
    class GreetingSkill(Skill):
        def start(self, initial_message: str):
            self.say("Hi")

    class PartingSkill(Skill):
        def start(self, initial_message: str):
            self.say("Bye")

    def skill_classifier(message: str) -> List[Skill]:
        skills = []

        if "Hello" in message:
            skills.append(GreetingSkill())

        if "Goodbye" in message:
            skills.append(PartingSkill())

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user(bob_id)

    assert conversation.query("Hello") == ["Hi"]
    assert conversation.query("Goodbye") == ["Bye"]
    assert conversation.query("How are you?") == []


def test_choice_of_many_skills(bob_id: str):
    class GreetingSkill(Skill):
        def start(self, initial_message: str):
            self.say("Hello")

    class IntroduceYourselfSkill(Skill):
        def start(self, initial_message: str):
            self.say("It's me")

    def skill_classifier(message: str) -> List[Skill]:
        skills = [GreetingSkill(), IntroduceYourselfSkill()]
        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user(bob_id)

    assert conversation.query("Hello") == ["Hello", "It's me"]


def test_separation_context_on_users(bob_id: str, alice_id: str, meeting_agent: Agent):
    conversation_with_bob = meeting_agent.conversation_with_user(bob_id)
    conversation_with_alice = meeting_agent.conversation_with_user(alice_id)

    assert conversation_with_bob.query("Hello") == ["What is your name?"]
    assert conversation_with_alice.query("Hello") == ["What is your name?"]

    assert conversation_with_bob.query("Bob") == ["Nice to meet you Bob!"]
    assert conversation_with_alice.query("Alice") == ["Nice to meet you Alice!"]


def test_query_without_conversation(bob_id: str, meeting_agent: Agent):
    assert meeting_agent.query("Hello", bob_id) == ["What is your name?"]
    assert meeting_agent.query("Bob", bob_id) == ["Nice to meet you Bob!"]


def test_multi_answers(bob_id: str):
    class MoodSkill(Skill):
        def start(self, initial_message: str):
            self.say("Hello")
            self.say("Good day!")
            self.ask("How are you?", direct_to=self.waiting_mood)

        def waiting_mood(self, mood: str):
            self.say("Goodbye")

    def skill_classifier(message: str) -> List[Skill]:
        return [MoodSkill()]

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user(bob_id)

    assert conversation.query("Hello") == ["Hello", "Good day!", "How are you?"]


def test_continuous_conversation(bob_id: str, meeting_agent: Agent):
    conversation = meeting_agent.conversation_with_user(bob_id)

    assert conversation.query("Hello") == ["What is your name?"]
    assert conversation.query("Bob") == ["Nice to meet you Bob!"]


def test_ram_persistent_continuous_conversation(bob_id: str, meeting_skill_class: Agent):
    def skill_classifier(message: str) -> List[Skill]:
        skills = []

        if "Hello" in message:
            skills.append(meeting_skill_class())

        return skills

    agent = Agent(skill_classifier=skill_classifier, context=RAMAgentContext())
    conversation = agent.conversation_with_user(bob_id)
    assert conversation.query("Hello") == ["What is your name?"]

    agent = Agent(skill_classifier=skill_classifier, context=RAMAgentContext())
    conversation = agent.conversation_with_user(bob_id)
    assert conversation.query("Bob") == []


def test_redis_persistent_continuous_conversation(bob_id: str, redis: Redis, age_skill_class: Type[Skill]):
    def skill_classifier(message: str) -> List[Skill]:
        skills = []

        if "age" in message:
            skills.append(age_skill_class())

        return skills

    agent = Agent(skill_classifier=skill_classifier, context=RedisAgentContext(redis=redis))
    conversation = agent.conversation_with_user(bob_id)
    assert conversation.query("What about age?") == ["How old are you?"]

    agent = Agent(skill_classifier=skill_classifier, context=RedisAgentContext(redis=redis))
    conversation = agent.conversation_with_user(bob_id)
    assert conversation.query("42") == ["Ok"]


def test_default_context():
    agent = Agent(skill_classifier=lambda message: [])

    assert isinstance(agent.context, RAMAgentContext)


def test_global_context_change_in_skill(bob_id: str):
    class AgeSkill(Skill):
        def start(self, initial_message: str):
            age = self.global_context.get("age")
            if not age:
                self.ask("How old are you?", direct_to=self.waiting_age)
            self.say(f"You are {age} years old")

        def waiting_age(self, age: str):
            self.global_context["age"] = age
            self.say(f"You are {age} years old")

    def skill_classifier(message: str) -> List[Skill]:
        skills = []

        if "age" in message:
            skills.append(AgeSkill())

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user(bob_id)

    assert conversation.query("What about age?") == ["How old are you?"]
    assert conversation.query("42") == ["You are 42 years old"]
    assert conversation.query("What about age") == ["You are 42 years old"]


def test_specify(bob_id: str, age_skill_class: Type[Skill]):
    def skill_classifier(message: str) -> List[Skill]:
        skills = []

        if "age" in message:
            skills.append(age_skill_class())

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user(bob_id)

    assert conversation.query("What about age?") == ["How old are you?"]
    assert conversation.query("Forty two") == ["Incorrect age: expected number, repeat pls"]
    assert conversation.query("42") == ["Ok"]


def test_move_to_new_skill_when_specify(bob_id: str, age_skill_class: Type[Skill], meeting_skill_class: Type[Skill]):
    def skill_classifier(message: str) -> List[Skill]:
        skills = []

        if "age" in message:
            skills.append(age_skill_class())

        if "Hello" in message:
            skills.append(meeting_skill_class())

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user(bob_id)

    assert conversation.query("What about age?") == ["How old are you?"]
    assert conversation.query("Hello") == ["What is your name?"]


def test_do_not_move_to_new_skill_when_not_specify(bob_id: str, age_skill_class: Type[Skill], meeting_skill_class: Type[Skill]):
    def skill_classifier(message: str) -> List[Skill]:
        skills = []

        if "age" in message:
            skills.append(age_skill_class())

        if "Hello" in message:
            skills.append(meeting_skill_class())

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user(bob_id)

    assert conversation.query("Hello") == ["What is your name?"]
    assert conversation.query("What about age?") == ["Nice to meet you What about age?!"]


def test_inline_ask(bob_id: str):
    class MeetingSkill(Skill):
        def start(self, initial_message: str):
            self.say(f"Hello")
            name = self.ask(question="What is your name?")
            self.say(f"Nice to meet you {name}!")

    def skill_classifier(message: str) -> List[Skill]:
        return [MeetingSkill()]

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user(bob_id)

    assert conversation.query("Hello") == ["Hello", "What is your name?"]
    assert conversation.query("Bob") == ["Nice to meet you Bob!"]
