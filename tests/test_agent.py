import random
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from unittest import mock

from millet import Agent, BaseSkill, Conversation
from millet.skill import BaseSkillClassifier


class TestConversation:

    default_user_id = 'bob'

    def test_process_message(self):
        message = 'hello'
        agent = mock.Mock(spec=Agent)

        conversation = Conversation(agent=agent, user_id=self.default_user_id)
        conversation.process_message(message=message)

        agent.process_message.assert_called_once_with(
            message=message, user_id=self.default_user_id
        )


class TestAgent:

    default_user_id = 'bob'

    def test_process_message(self):

        class EchoSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                self.say(message)

        skill = EchoSkill()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'echo': skill,
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                return ['echo']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='hello', user_id=self.default_user_id)
        assert answers == ['hello']

    def test_conversation_with_user(self):

        class EchoSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                self.say(message)

        skill = EchoSkill()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'echo': skill,
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                return ['echo']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)
        conversation = agent.conversation_with_user(self.default_user_id)

        assert conversation.agent == agent
        assert conversation.user_id == self.default_user_id

    def test_query_with_ask(self):

        class MeetingSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                name = self.ask('What is your name?')
                self.say(f'Nice to meet you {name}!')

        skill = MeetingSkill()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'meeting': skill,
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                return ['meeting']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='hello', user_id=self.default_user_id)
        assert answers == ['What is your name?']

        answers = agent.process_message(message='Bob', user_id=self.default_user_id)
        assert answers == ['Nice to meet you Bob!']

    def test_ask_with_direct_to(self):

        class MeetingSkillWithStates(BaseSkill):

            def execute(self, message: str, user_id: str):
                self.ask('What is your name?', direct_to='meeting')

            def meeting(self, name: str, user_id: str):
                self.say(f'Nice to meet you {name}!')

        skill = MeetingSkillWithStates()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'meeting': skill,
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                return ['meeting']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='hello', user_id=self.default_user_id)
        assert answers == ['What is your name?']

        answers = agent.process_message(message='Bob', user_id=self.default_user_id)
        assert answers == ['Nice to meet you Bob!']

    def test_query_with_specify(self):

        class AgeSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                age = self.ask('How old are you?')

                try:
                    age = int(age)
                except ValueError:
                    age = self.specify(question='Send a number pls')

                self.say(f'You are {age} years old')

        skill = AgeSkill()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'age': skill,
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                skill_names = []
                if 'age' in message:
                    skill_names.append('age')
                return skill_names

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='Ask me about age', user_id=self.default_user_id)
        assert answers == ['How old are you?']

        answers = agent.process_message(message='twenty four', user_id=self.default_user_id)
        assert answers == ['Send a number pls']

        answers = agent.process_message(message='24', user_id=self.default_user_id)
        assert answers == ['You are 24 years old']

    def test_query_with_specify_with_direct_to(self):

        class AgeSkillWithDirectTo(BaseSkill):
            def execute(self, message: str, user_id: str):
                age = self.ask('How old are you?')
                self.wait_age(age, user_id)

            def wait_age(self, age: str, user_id: str):
                try:
                    age = int(age)
                except ValueError:
                    self.specify(question='Send a number pls', direct_to='wait_age')

                self.say(f'You are {age} years old')

        skill = AgeSkillWithDirectTo()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'age': skill,
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                skill_names = []
                if 'age' in message:
                    skill_names.append('age')
                return skill_names

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='Ask me about age', user_id=self.default_user_id)
        assert answers == ['How old are you?']

        answers = agent.process_message(message='twenty four', user_id=self.default_user_id)
        assert answers == ['Send a number pls']

        answers = agent.process_message(message='TWENTY FOUR', user_id=self.default_user_id)
        assert answers == ['Send a number pls']

        answers = agent.process_message(message='24', user_id=self.default_user_id)
        assert answers == ['You are 24 years old']

    def test_multi_skills(self):

        class EchoSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                self.say(message)

        skill = EchoSkill()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'echo': skill,
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                return ['echo', 'echo']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='hello', user_id=self.default_user_id)
        assert answers == ['hello', 'hello']

    def test_multi_skills_and_one_continuously(self):

        class EchoSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                self.say(message)

        class AgeSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                age = self.ask('How old are you?')

                try:
                    age = int(age)
                except ValueError:
                    age = self.specify(question='Send a number pls')

                self.say(f'You are {age} years old')

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'echo': EchoSkill(),
                    'age': AgeSkill(),
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                skill_names = []
                if 'age' in message:
                    skill_names.append('echo')
                    skill_names.append('age')
                return skill_names

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='Ask me about age', user_id=self.default_user_id)
        assert answers == ['Ask me about age', 'How old are you?']

        answers = agent.process_message(message='twenty four', user_id=self.default_user_id)
        assert answers == ['Send a number pls']

        answers = agent.process_message(message='24', user_id=self.default_user_id)
        assert answers == ['You are 24 years old']

    def test_long_skill(self):

        class AgeSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                name = self.ask('What is your name?')
                self.say(f'Nice to meet you {name}!')

                age = self.ask(f'{name}, how old are you?')

                try:
                    age = int(age)
                except ValueError:
                    age = self.specify(question=f'{name}, send a number pls')

                self.say(f'You are {age} years old')

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'age': AgeSkill(),
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                skill_names = []
                if 'age' in message:
                    skill_names.append('age')
                return skill_names

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='Ask me about age', user_id=self.default_user_id)
        assert answers == ['What is your name?']

        answers = agent.process_message(message='Bob', user_id=self.default_user_id)
        assert answers == ['Nice to meet you Bob!', 'Bob, how old are you?']

        answers = agent.process_message(message='twenty four', user_id=self.default_user_id)
        assert answers == ['Bob, send a number pls']

        answers = agent.process_message(message='24', user_id=self.default_user_id)
        assert answers == ['You are 24 years old']

    def test_interrupt_skill(self):
        class GreetingSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                self.say('Hello')

        class AgeSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                age = self.ask('How old are you?')

                try:
                    age = int(age)
                except ValueError:
                    age = self.specify(question='Send a number pls')

                self.say(f'You are {age} years old')

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'hello': GreetingSkill(),
                    'age': AgeSkill(),
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                skill_names = []
                if 'age' in message:
                    skill_names.append('age')
                elif 'hello' in message:
                    skill_names.append('hello')
                return skill_names

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='Ask me about age', user_id=self.default_user_id)
        assert answers == ['How old are you?']

        answers = agent.process_message(message='hello', user_id=self.default_user_id)
        assert answers == ['Hello']

    def test_context_using(self):

        class MeetingSkillWithStates(BaseSkill):

            def execute(self, message: str, user_id: str):
                self.context['greeting'] = 'Nice to meet you'
                self.ask('What is your name?', direct_to='meeting')

            def meeting(self, name: str, user_id: str):
                greeting = self.context['greeting']
                self.say(f'{greeting} {name}!')

        skill = MeetingSkillWithStates()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'meeting': skill,
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                return ['meeting']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='hello', user_id=self.default_user_id)
        assert answers == ['What is your name?']

        answers = agent.process_message(message='Bob', user_id=self.default_user_id)
        assert answers == ['Nice to meet you Bob!']

    def test_multi_skills_and_context_using(self):

        class EchoSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                self.context['age'] = 100500
                self.say(message)

        class AgeSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                age = self.context.get('age')
                if age is None:
                    age = self.ask('How old are you?')

                    try:
                        age = int(age)
                    except ValueError:
                        age = self.specify(question='Send a number pls')

                self.say(f'You are {age} years old')

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'echo': EchoSkill(),
                    'age': AgeSkill(),
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                skill_names = []
                if 'age' in message:
                    skill_names.append('echo')
                    skill_names.append('age')
                return skill_names

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='Ask me about age', user_id=self.default_user_id)
        assert answers == ['Ask me about age', 'How old are you?']

        answers = agent.process_message(message='twenty four', user_id=self.default_user_id)
        assert answers == ['Send a number pls']

        answers = agent.process_message(message='24', user_id=self.default_user_id)
        assert answers == ['You are 24 years old']

    @mock.patch('random.randint')
    def test_cached_side_function(self, randint_mock):

        randint_mock.return_value = 35

        class NumberSkill(BaseSkill):

            side_functions = [
                'random.randint',
            ]

            def execute(self, message: str, user_id: str):
                number_expected = random.randint(0, 100)  # side function
                number_actual = int(self.ask('Whats number?'))
                if number_actual == number_expected:
                    self.say('ok')
                else:
                    self.say('wrong')

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'number': NumberSkill(),
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                return ['number']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='start', user_id=self.default_user_id)
        assert answers == ['Whats number?']

        answers = agent.process_message(message='35', user_id=self.default_user_id)
        assert answers == ['ok']

        randint_mock.assert_called_once_with(0, 100)

    @mock.patch('random.randint')
    def test_cached_side_self_method(self, randint_mock):

        randint_mock.return_value = 35

        class NumberSkill(BaseSkill):

            side_methods = [
                ('NumberSkill', 'rand'),
            ]

            def execute(self, message: str, user_id: str):
                number_expected = self.rand()  # side self-method
                number_actual = int(self.ask('Whats number?'))
                if number_actual == number_expected:
                    self.say('ok')
                else:
                    self.say('wrong')

            def rand(self):
                return random.randint(0, 100)

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'number': NumberSkill(),
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                return ['number']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='start', user_id=self.default_user_id)
        assert answers == ['Whats number?']

        answers = agent.process_message(message='35', user_id=self.default_user_id)
        assert answers == ['ok']

        randint_mock.assert_called_once_with(0, 100)

    @mock.patch('random.randint')
    def test_cached_side_method(self, randint_mock):

        randint_mock.return_value = 35

        class Rand:
            def rand(self):
                return random.randint(0, 100)

        class NumberSkill(BaseSkill):

            side_methods = [
                (Rand, 'rand'),
            ]

            def execute(self, message: str, user_id: str):
                number_expected = Rand().rand()  # side method
                number_actual = int(self.ask('Whats number?'))
                if number_actual == number_expected:
                    self.say('ok')
                else:
                    self.say('wrong')

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'number': NumberSkill(),
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                return ['number']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='start', user_id=self.default_user_id)
        assert answers == ['Whats number?']

        answers = agent.process_message(message='35', user_id=self.default_user_id)
        assert answers == ['ok']

        randint_mock.assert_called_once_with(0, 100)

    @mock.patch('random.randint')
    def test_cached_side_cls_method(self, randint_mock):

        randint_mock.return_value = 35

        class Rand:
            @classmethod
            def rand(cls):
                return random.randint(0, 100)

        class NumberSkill(BaseSkill):

            side_methods = [
                (Rand, 'rand'),
            ]

            def execute(self, message: str, user_id: str):
                number_expected = Rand.rand()  # side cls-method
                number_actual = int(self.ask('Whats number?'))
                if number_actual == number_expected:
                    self.say('ok')
                else:
                    self.say('wrong')

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'number': NumberSkill(),
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                return ['number']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='start', user_id=self.default_user_id)
        assert answers == ['Whats number?']

        answers = agent.process_message(message='35', user_id=self.default_user_id)
        assert answers == ['ok']

        randint_mock.assert_called_once_with(0, 100)

    @mock.patch('random.randint')
    def test_cached_side_self_attribute(self, randint_mock):

        randint_mock.return_value = 35

        class IRand(ABC):
            @abstractmethod
            def rand(self):
                pass

        class Rand(IRand):
            def rand(self):
                return random.randint(0, 100)

        class NumberSkill(BaseSkill):

            side_methods = [
                ('self.rand', 'rand'),
            ]

            def __init__(self, rand: IRand):
                self.rand = rand

            def execute(self, message: str, user_id: str):
                number_expected = self.rand.rand()  # side method
                number_actual = int(self.ask('Whats number?'))
                if number_actual == number_expected:
                    self.say('ok')
                else:
                    self.say('wrong')

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'number': NumberSkill(rand=Rand()),
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                return ['number']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='start', user_id=self.default_user_id)
        assert answers == ['Whats number?']

        answers = agent.process_message(message='35', user_id=self.default_user_id)
        assert answers == ['ok']

        randint_mock.assert_called_once_with(0, 100)

    @mock.patch('random.randint')
    def test_cached_side_self_attribute_nested(self, randint_mock):

        randint_mock.return_value = 35

        class RandManager:
            def __init__(self, rand):
                self.rand = rand

            def execute(self):
                return self.rand.rand(0, 100)

        class Rand:
            def rand(self, a, b):
                return random.randint(a, b)

        class NumberSkill(BaseSkill):

            side_methods = [
                ('self.rand_manager.rand', 'rand'),
            ]

            def __init__(self, rand_manager):
                self.rand_manager = rand_manager

            def execute(self, message: str, user_id: str):
                number_expected = self.rand_manager.execute()  # side method
                number_actual = int(self.ask('Whats number?'))
                if number_actual == number_expected:
                    self.say('ok')
                else:
                    self.say('wrong')

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'number': NumberSkill(rand_manager=RandManager(rand=Rand())),
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                return ['number']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='start', user_id=self.default_user_id)
        assert answers == ['Whats number?']

        answers = agent.process_message(message='35', user_id=self.default_user_id)
        assert answers == ['ok']

        randint_mock.assert_called_once_with(0, 100)

    def test_user_id(self):
        class UserIdSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                self.say(user_id)

        skill = UserIdSkill()

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'user_id_skill': skill,
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                return ['user_id_skill']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='hello', user_id=self.default_user_id)
        assert answers == [self.default_user_id]

    def test_action(self):
        class EchoSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                self.say(message)

        class MeetingSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                name = self.ask('What is your name?')
                self.say(f'Nice to meet you {name}!')

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'echo': EchoSkill(),
                    'meeting': MeetingSkill(),
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                if message == 'echo click':
                    return ['echo']
                return ['meeting']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='hello', user_id=self.default_user_id)
        assert answers == ['What is your name?']

        answers = agent.process_action(  # force classify
            message='echo click',
            user_id=self.default_user_id,
        )
        assert answers == ['echo click']

    def test_process_message(self):
        class EchoSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                self.say(message)

        class MeetingSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                name = self.ask('What is your name?')
                self.say(f'Nice to meet you {name}!')

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'echo': EchoSkill(),
                    'meeting': MeetingSkill(),
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                if message == 'echo click':
                    return ['echo']
                return ['meeting']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='hello', user_id=self.default_user_id)
        assert answers == ['What is your name?']

        answers = agent.process_message(
            message='echo click',
            user_id=self.default_user_id,
        )
        assert answers == ['Nice to meet you echo click!']

    def test_process_action(self):
        class EchoSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                self.say(message)

        class MeetingSkill(BaseSkill):
            def execute(self, message: str, user_id: str):
                name = self.ask('What is your name?')
                self.say(f'Nice to meet you {name}!')

        class SkillClassifier(BaseSkillClassifier):
            @property
            def skills_map(self) -> Dict[str, BaseSkill]:
                return {
                    'echo': EchoSkill(),
                    'meeting': MeetingSkill(),
                }

            def classify(self, message: Any, user_id: str) -> List[str]:
                if message == 'echo click':
                    return ['echo']
                return ['meeting']

        skill_classifier = SkillClassifier()

        agent = Agent(skill_classifier=skill_classifier)

        answers = agent.process_message(message='hello', user_id=self.default_user_id)
        assert answers == ['What is your name?']

        answers = agent.process_action(
            message='echo click',
            user_id=self.default_user_id,
        )
        assert answers == ['echo click']
