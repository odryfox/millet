from millet import BaseSkill
from millet.timeouts import MessageTimeOut, MessageTimeOutException


def test_skill_timeout_happened():

    class MeetingSkill(BaseSkill):
        def execute(self, message: str):
            try:
                name = self.ask('What is your name?', timeout=10)
            except MessageTimeOutException:
                name = self.ask('I repeat the question: what is your name?')

            return f'Nice to meet you {name}!'

    skill = MeetingSkill()

    result = skill.run(
        message='hello', history=[], state_name=None, context={}
    )

    assert result.answers == ['What is your name?']
    assert result.is_relevant
    assert not result.is_finished
    assert result.direct_to is None
    assert result.context == {}
    assert result.timeout == 10

    result = skill.run(
        message=MessageTimeOut(), history=['hello'], state_name=None, context={}
    )

    assert result.answers == ['I repeat the question: what is your name?']
    assert result.is_relevant
    assert not result.is_finished
    assert result.direct_to is None
    assert result.context == {}
    assert result.timeout is None

    result = skill.run(
        message='Bob', history=['hello', MessageTimeOut()], state_name=None, context={}
    )

    assert result.answers == ['Nice to meet you Bob!']
    assert result.is_relevant
    assert result.is_finished
    assert result.direct_to is None
    assert result.context == {}
    assert result.timeout is None
