from typing import List, Type

import pytest

from redis import Redis

from dialogus import Skill, Agent
from dialogus.context import DialogContext, UserContext


@pytest.fixture
def bob_id():
    return "Bob"


@pytest.fixture
def alice_id():
    return "Alice"


@pytest.fixture
def meeting_skill_class() -> Type[Skill]:
    class _MeetingSkill(Skill):
        def run(self, message: str):
            name = self.ask("What is your name?")
            self.say(f"Nice to meet you {name}!")

    return _MeetingSkill


@pytest.fixture
def meeting_agent(meeting_skill_class: Type[Skill]) -> Agent:
    def skill_classifier(message: str) -> List[Type[Skill]]:
        skills = []

        if "Hello" in message:
            skills.append(meeting_skill_class)

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    return agent


# pickle serializer requires global class for serialize/deserialize
class AgeSkill(Skill):
    def run(self, message: str):
        age = self.ask("How old are you?")
        ...
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

    skill_params = {
        "How old are you?": 42,
    }

    dialogs = [DialogContext(skill_class=AgeSkill, params=skill_params)]

    return UserContext(params=global_params, dialogs=dialogs)
