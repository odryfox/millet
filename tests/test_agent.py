from typing import Any, List
from unittest import mock

from millet import Agent, BaseSkill, Conversation
from millet.skill import BaseSkillClassifier


class TestConversation:

    default_user_id = 'bob'

    def test_query(self):
        message = 'hello'
        agent = mock.Mock(spec=Agent)

        conversation = Conversation(agent=agent, user_id=self.default_user_id)
        conversation.query(message=message)

        agent.query.assert_called_once_with(message=message, user_id=self.default_user_id)


class TestAgent:

    default_user_id = 'bob'

    def test_query(self):

        class EchoSkill(BaseSkill):
            def start(self, message: str):
                self.say(message)

        skill = EchoSkill()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> dict[str, BaseSkill]:
                return {
                    'echo': skill,
                }

            def classify(self, message: Any) -> List[str]:
                return ['echo']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.query(message='hello', user_id=self.default_user_id)
        assert answers == ['hello']

    def test_conversation_with_user(self):

        class EchoSkill(BaseSkill):
            def start(self, message: str):
                self.say(message)

        skill = EchoSkill()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> dict[str, BaseSkill]:
                return {
                    'echo': skill,
                }

            def classify(self, message: Any) -> List[str]:
                return ['echo']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)
        conversation = agent.conversation_with_user(self.default_user_id)

        assert conversation.agent == agent
        assert conversation.user_id == self.default_user_id

    def test_query_with_ask(self):

        class MeetingSkill(BaseSkill):
            def start(self, message: str):
                name = self.ask('What is your name?')
                self.say(f'Nice to meet you {name}!')

        skill = MeetingSkill()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> dict[str, BaseSkill]:
                return {
                    'meeting': skill,
                }

            def classify(self, message: Any) -> List[str]:
                return ['meeting']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.query(message='hello', user_id=self.default_user_id)
        assert answers == ['What is your name?']

        answers = agent.query(message='Bob', user_id=self.default_user_id)
        assert answers == ['Nice to meet you Bob!']

    def test_ask_with_direct_to(self):

        class MeetingSkillWithStates(BaseSkill):

            def start(self, message: str):
                self.ask('What is your name?', direct_to='meeting')

            def meeting(self, name: str):
                self.say(f'Nice to meet you {name}!')

        skill = MeetingSkillWithStates()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> dict[str, BaseSkill]:
                return {
                    'meeting': skill,
                }

            def classify(self, message: Any) -> List[str]:
                return ['meeting']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.query(message='hello', user_id=self.default_user_id)
        assert answers == ['What is your name?']

        answers = agent.query(message='Bob', user_id=self.default_user_id)
        assert answers == ['Nice to meet you Bob!']

    def test_query_with_specify(self):

        class AgeSkill(BaseSkill):
            def start(self, message: str):
                age = self.ask('How old are you?')

                try:
                    age = int(age)
                except ValueError:
                    age = self.specify(question='Send a number pls')

                self.say(f'You are {age} years old')

        skill = AgeSkill()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> dict[str, BaseSkill]:
                return {
                    'age': skill,
                }

            def classify(self, message: Any) -> List[str]:
                skill_names = []
                if 'age' in message:
                    skill_names.append('age')
                return skill_names

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.query(message='Ask me about age', user_id=self.default_user_id)
        assert answers == ['How old are you?']

        answers = agent.query(message='twenty four', user_id=self.default_user_id)
        assert answers == ['Send a number pls']

        answers = agent.query(message='24', user_id=self.default_user_id)
        assert answers == ['You are 24 years old']

    def test_query_with_specify_with_direct_to(self):

        class AgeSkillWithDirectTo(BaseSkill):
            def start(self, message: str):
                age = self.ask('How old are you?')
                self.wait_age(age)

            def wait_age(self, age: str):
                try:
                    age = int(age)
                except ValueError:
                    self.specify(question='Send a number pls', direct_to='wait_age')

                self.say(f'You are {age} years old')

        skill = AgeSkillWithDirectTo()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> dict[str, BaseSkill]:
                return {
                    'age': skill,
                }

            def classify(self, message: Any) -> List[str]:
                skill_names = []
                if 'age' in message:
                    skill_names.append('age')
                return skill_names

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.query(message='Ask me about age', user_id=self.default_user_id)
        assert answers == ['How old are you?']

        answers = agent.query(message='twenty four', user_id=self.default_user_id)
        assert answers == ['Send a number pls']

        answers = agent.query(message='TWENTY FOUR', user_id=self.default_user_id)
        assert answers == ['Send a number pls']

        answers = agent.query(message='24', user_id=self.default_user_id)
        assert answers == ['You are 24 years old']

    def test_multi_skills(self):

        class EchoSkill(BaseSkill):
            def start(self, message: str):
                self.say(message)

        skill = EchoSkill()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> dict[str, BaseSkill]:
                return {
                    'echo': skill,
                }

            def classify(self, message: Any) -> List[str]:
                return ['echo', 'echo']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.query(message='hello', user_id=self.default_user_id)
        assert answers == ['hello', 'hello']

    def test_multi_skills_and_one_continuously(self):

        class EchoSkill(BaseSkill):
            def start(self, message: str):
                self.say(message)

        class AgeSkill(BaseSkill):
            def start(self, message: str):
                age = self.ask('How old are you?')

                try:
                    age = int(age)
                except ValueError:
                    age = self.specify(question='Send a number pls')

                self.say(f'You are {age} years old')

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> dict[str, BaseSkill]:
                return {
                    'echo': EchoSkill(),
                    'age': AgeSkill(),
                }

            def classify(self, message: Any) -> List[str]:
                skill_names = []
                if 'age' in message:
                    skill_names.append('echo')
                    skill_names.append('age')
                return skill_names

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.query(message='Ask me about age', user_id=self.default_user_id)
        assert answers == ['Ask me about age', 'How old are you?']

        answers = agent.query(message='twenty four', user_id=self.default_user_id)
        assert answers == ['Send a number pls']

        answers = agent.query(message='24', user_id=self.default_user_id)
        assert answers == ['You are 24 years old']
