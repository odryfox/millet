from typing import Any, Dict, List
from unittest import mock

from millet import Agent, BaseSkill, BaseSkillClassifier
from millet.timeouts import (
    BaseTimeoutsBroker,
    MessageTimeOut,
    MessageTimeOutException
)


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
        message=MessageTimeOut(),
        history=['hello'],
        state_name=None,
        context={},
    )

    assert result.answers == ['I repeat the question: what is your name?']
    assert result.is_relevant
    assert not result.is_finished
    assert result.direct_to is None
    assert result.context == {}
    assert result.timeout is None

    result = skill.run(
        message='Bob',
        history=['hello', MessageTimeOut()],
        state_name=None,
        context={},
    )

    assert result.answers == ['Nice to meet you Bob!']
    assert result.is_relevant
    assert result.is_finished
    assert result.direct_to is None
    assert result.context == {}
    assert result.timeout is None


def test_agent_timeout_happened():

    class MeetingSkill(BaseSkill):
        def execute(self, message: str):
            try:
                name = self.ask('What is your name?', timeout=10)
            except MessageTimeOutException:
                name = self.ask('I repeat the question: what is your name?')

            return f'Nice to meet you {name}!'

    class SkillClassifier(BaseSkillClassifier):
        @property
        def skills_map(self) -> Dict[str, BaseSkill]:
            return {
                'meeting_skill': MeetingSkill(),
            }

        def classify(self, message: Any) -> List[str]:
            return ['meeting_skill']

    skill_classifier = SkillClassifier()

    async_task_mock = mock.Mock()
    # apply async_task(user_id, timeout_uid) after timeout
    #     agent.process_timeout(timeout_uid=timeout_uid, user_id=user_id)

    class FakeTimeoutsBroker(BaseTimeoutsBroker):
        def execute(self, user_id: str, timeout: int, timeout_uid: str):
            async_task_mock(user_id, timeout, timeout_uid)

        def generate_timeout_uid(self, user_id: str, timeout: int) -> str:
            return '12345'

    fake_timeouts_broker = FakeTimeoutsBroker()

    agent = Agent(
        skill_classifier=skill_classifier,
        timeouts_broker=fake_timeouts_broker,
    )

    answers = agent.process_message(message='hello', user_id='100500')
    assert answers == ['What is your name?']

    answers = agent.process_timeout(timeout_uid='12345', user_id='100500')
    assert answers == ['I repeat the question: what is your name?']

    async_task_mock.assert_called_once_with('100500', 10, '12345')


def test_agent_timeout_did_not_happened():

    class MeetingSkill(BaseSkill):
        def execute(self, message: str):
            try:
                name = self.ask('What is your name?', timeout=10)
            except MessageTimeOutException:
                name = self.ask('I repeat the question: what is your name?')

            age = self.ask(f'Nice to meet you {name}! How old are you?')
            return age

    class SkillClassifier(BaseSkillClassifier):
        @property
        def skills_map(self) -> Dict[str, BaseSkill]:
            return {
                'meeting_skill': MeetingSkill(),
            }

        def classify(self, message: Any) -> List[str]:
            return ['meeting_skill']

    skill_classifier = SkillClassifier()

    async_task_mock = mock.Mock()
    # apply async_task(user_id, timeout_uid) after timeout
    #     agent.process_timeout(timeout_uid=timeout_uid, user_id=user_id)

    class FakeTimeoutsBroker(BaseTimeoutsBroker):
        def execute(self, user_id: str, timeout: int, timeout_uid: str):
            async_task_mock(user_id, timeout, timeout_uid)

        def generate_timeout_uid(self, user_id: str, timeout: int) -> str:
            return '12345'

    fake_timeouts_broker = FakeTimeoutsBroker()

    agent = Agent(
        skill_classifier=skill_classifier,
        timeouts_broker=fake_timeouts_broker,
    )

    answers = agent.process_message(message='hello', user_id='100500')
    assert answers == ['What is your name?']

    answers = agent.process_message(message='Bob', user_id='100500')
    assert answers == ['Nice to meet you Bob! How old are you?']

    answers = agent.process_timeout(timeout_uid='12345', user_id='100500')
    assert answers == []

    async_task_mock.assert_called_once_with('100500', 10, '12345')


def test_agent_timeout_happened_without_timeouts_broker():

    class MeetingSkill(BaseSkill):
        def execute(self, message: str):
            try:
                name = self.ask('What is your name?', timeout=10)
            except MessageTimeOutException:
                name = self.ask('I repeat the question: what is your name?')

            return f'Nice to meet you {name}!'

    class SkillClassifier(BaseSkillClassifier):
        @property
        def skills_map(self) -> Dict[str, BaseSkill]:
            return {
                'meeting_skill': MeetingSkill(),
            }

        def classify(self, message: Any) -> List[str]:
            return ['meeting_skill']

    skill_classifier = SkillClassifier()

    agent = Agent(skill_classifier=skill_classifier)

    answers = agent.process_message(message='hello', user_id='100500')
    assert answers == ['What is your name?']

    answers = agent.process_timeout(timeout_uid='12345', user_id='100500')
    assert answers == []

    answers = agent.process_message(message='Bob', user_id='100500')
    assert answers == ['Nice to meet you Bob!']


def test_agent_timeout_happened_after_other_timeout():

    class MeetingSkill(BaseSkill):
        def execute(self, message: str):
            try:
                name = self.ask('What is your name?', timeout=10)
            except MessageTimeOutException:
                name = self.ask('I repeat the question: what is your name?')

            return f'Nice to meet you {name}!'

    class SkillClassifier(BaseSkillClassifier):
        @property
        def skills_map(self) -> Dict[str, BaseSkill]:
            return {
                'meeting_skill': MeetingSkill(),
            }

        def classify(self, message: Any) -> List[str]:
            return ['meeting_skill']

    skill_classifier = SkillClassifier()

    async_task_mock = mock.Mock()
    # apply async_task(user_id, timeout_uid) after timeout
    #     agent.process_message(message=MessageTimeOut(timeout_uid), user_id=user_id)

    class FakeTimeoutsBroker(BaseTimeoutsBroker):
        def execute(self, user_id: str, timeout: int, timeout_uid: str):
            async_task_mock(user_id, timeout, timeout_uid)

        def generate_timeout_uid(self, user_id: str, timeout: int) -> str:
            return '12345'

    fake_timeouts_broker = FakeTimeoutsBroker()

    agent = Agent(
        skill_classifier=skill_classifier,
        timeouts_broker=fake_timeouts_broker,
    )

    answers = agent.process_message(message='hello', user_id='100500')
    assert answers == ['What is your name?']

    answers = agent.process_timeout(timeout_uid='12346', user_id='100500')
    assert answers == []

    answers = agent.process_timeout(timeout_uid='12345', user_id='100500')
    assert answers == ['I repeat the question: what is your name?']

    async_task_mock.assert_called_once_with('100500', 10, '12345')
