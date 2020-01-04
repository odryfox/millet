import pytest

from dialogus import Skill


@pytest.fixture
def age_skill():
    class AgeSkill(Skill):
        def run(self, message: str):
            age = self.ask('How old are you?')
            self.say('Ok')

    return AgeSkill()


@pytest.fixture
def meeting_skill():
    class MeetingSkill(Skill):
        def run(self, message: str):
            name = self.ask('What is your name?')
            self.say(f'Nice to meet you {name}!')

    return MeetingSkill()
