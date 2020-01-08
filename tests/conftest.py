import pytest

from redis import Redis

from dialogus import Skill
from dialogus.context import DialogContext, UserContext


@pytest.fixture
def age_skill_class():
    class AgeSkill(Skill):
        def run(self, message: str):
            age = self.ask('How old are you?')
            self.say('Ok')

    return AgeSkill


@pytest.fixture
def meeting_skill_class():
    class MeetingSkill(Skill):
        def run(self, message: str):
            name = self.ask('What is your name?')
            self.say(f'Nice to meet you {name}!')

    return MeetingSkill


@pytest.fixture
def mood_skill_class():
    class MoodSkill(Skill):
        def run(self, message: str):
            self.say('Hello')
            self.say('Good day!')
            mood = self.ask('How are you?')
            ...

    return MoodSkill


@pytest.fixture
def friend_name_skill():
    class FriendNamesSkill(Skill):
        def run(self, message: str):
            your_name = message
            self.say(f'Your name is {your_name}')
            friend_name = self.ask("Enter your friend's name")
            self.say(f'Your friend is {friend_name}')

    return FriendNamesSkill


@pytest.fixture()
def redis():
    redis = Redis()
    redis.flushdb()
    yield redis
    redis.flushdb()


class EmptySkill(Skill):
    def run(self, message: str):
        pass


@pytest.fixture()
def user_context():
    global_params = {
        "name": "Bob",
    }

    skill_params = {
        "test": "123",
    }

    dialogs = [DialogContext(skill_class=EmptySkill, params=skill_params)]

    return UserContext(params=global_params, dialogs=dialogs)
