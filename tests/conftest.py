from typing import List, Type

import pytest

from redis import Redis

from millet import Skill, Agent
from millet.context import UserContext


@pytest.fixture
def bob_id():
    return "Bob"


@pytest.fixture
def alice_id():
    return "Alice"


@pytest.fixture
def meeting_skill_class() -> Type[Skill]:
    class MeetingSkill(Skill):
        def start(self, initial_message: str):
            self.ask(question="What is your name?", direct_to=self.waiting_name)

        def waiting_name(self, name: str):
            self.say(f"Nice to meet you {name}!")

    return MeetingSkill


@pytest.fixture
def meeting_agent(meeting_skill_class: Type[Skill]) -> Agent:
    def skill_classifier(message: str) -> List[Skill]:
        skills = []

        if "Hello" in message:
            skills.append(meeting_skill_class())

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    return agent


# pickle serializer requires global class for serialize/deserialize
class AgeSkill(Skill):
    def start(self, initial_message: str):
        self.ask("How old are you?", direct_to=self.waiting_age)

    def waiting_age(self, age: str):
        try:
            age = int(age)
        except:
            self.specify("Incorrect age: expected number, repeat pls", direct_to=self.waiting_age)
        self.say("Ok")


@pytest.fixture
def age_skill_class():
    return AgeSkill


@pytest.fixture
def redis():
    redis = Redis()
    redis.flushdb()
    yield redis
    redis.flushdb()


@pytest.fixture
def user_context():
    global_params = {
        "name": "Bob",
        "age": 42,
    }

    return UserContext(params=global_params, skills=[AgeSkill()])
