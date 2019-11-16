from typing import List

import pytest

from src.dialogus.agent import Skill


@pytest.fixture
def age_skill():
    class AgeSkill(Skill):
        def run(self, message: str) -> List[str]:
            if self.state == 0:
                self.state = 1
                return ['How old are you?']
            if self.state == 1:
                self.state = 0
                return ['Ok']

    return AgeSkill()


@pytest.fixture
def meeting_skill():
    class MeetingSkill(Skill):
        def run(self, message: str) -> List[str]:
            if self.state == 0:
                self.state = 1
                return ['What is your name?']
            if self.state == 1:
                self.state = 0
                return [f'Nice to meet you {message}!']

    return MeetingSkill()
