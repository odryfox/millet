from millet import BaseSkill


class TestSkill:

    def test_say(self):

        class EchoSkill(BaseSkill):
            def start(self, message: str):
                self.say(message)

        skill = EchoSkill()

        result = skill.execute(
            message='hello', history=[], state_name=None, context={}
        )

        assert result.answers == ['hello']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to is None
        assert result.context == {}

        result = skill.execute(
            message='bye', history=[], state_name=None, context=result.context
        )

        assert result.answers == ['bye']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to is None
        assert result.context == {}

    def test_double_say(self):

        class DoubleEchoSkill(BaseSkill):
            def start(self, message: str):
                self.say(message)
                self.say(message)

        skill = DoubleEchoSkill()

        result = skill.execute(
            message='hello', history=[], state_name=None, context={}
        )

        assert result.answers == ['hello', 'hello']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to is None
        assert result.context == {}

        result = skill.execute(
            message='bye', history=[], state_name=None, context=result.context
        )

        assert result.answers == ['bye', 'bye']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to is None
        assert result.context == {}

    def test_ask(self):

        class MeetingSkill(BaseSkill):
            def start(self, message: str):
                name = self.ask('What is your name?')
                self.say(f'Nice to meet you {name}!')

        skill = MeetingSkill()

        result = skill.execute(
            message='hello', history=[], state_name=None, context={}
        )

        assert result.answers == ['What is your name?']
        assert result.is_relevant
        assert not result.is_finished
        assert result.direct_to is None
        assert result.context == {}

        result = skill.execute(
            message='Bob', history=['hello'], state_name=None, context=result.context
        )

        assert result.answers == ['Nice to meet you Bob!']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to is None
        assert result.context == {}

    def test_ask_with_direct_to(self):

        class MeetingSkillWithStates(BaseSkill):

            def start(self, message: str):
                self.ask('What is your name?', direct_to='meeting')

            def meeting(self, name: str):
                self.say(f'Nice to meet you {name}!')

        skill = MeetingSkillWithStates()

        result = skill.execute(
            message='hello', history=[], state_name=None, context={}
        )

        assert result.answers == ['What is your name?']
        assert result.is_relevant
        assert not result.is_finished
        assert result.direct_to == 'meeting'
        assert result.context == {}

        result = skill.execute(
            message='Bob', history=[], state_name='meeting', context=result.context
        )

        assert result.answers == ['Nice to meet you Bob!']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to is None
        assert result.context == {}

    def test_ask_with_direct_to_callable(self):

        class MeetingSkillWithStates(BaseSkill):

            def start(self, message: str):
                self.ask('What is your name?', direct_to=self.meeting)

            def meeting(self, name: str):
                self.say(f'Nice to meet you {name}!')

        skill = MeetingSkillWithStates()

        result = skill.execute(
            message='hello', history=[], state_name=None, context={}
        )

        assert result.answers == ['What is your name?']
        assert result.is_relevant
        assert not result.is_finished
        assert result.direct_to == 'meeting'
        assert result.context == {}

        result = skill.execute(
            message='Bob', history=[], state_name='meeting', context=result.context
        )

        assert result.answers == ['Nice to meet you Bob!']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to is None
        assert result.context == {}

    def test_specify(self):

        class AgeSkill(BaseSkill):
            def start(self, message: str):
                try:
                    age = int(message)
                except ValueError:
                    age = self.specify(question='Are you sure?')

                self.say(f'You are {age} years old')

        skill = AgeSkill()

        result = skill.execute(
            message='twenty four', history=[], state_name=None, context={}
        )

        assert result.answers == ['Are you sure?']
        assert not result.is_relevant
        assert not result.is_finished
        assert result.direct_to is None
        assert result.context == {}

        result = skill.execute(
            message='24', history=['twenty four'],
            state_name=None, context=result.context,
        )

        assert result.answers == ['You are 24 years old']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to is None
        assert result.context == {}

    def test_specify_with_direct_to(self):

        class AgeSkillWithDirectTo(BaseSkill):
            def start(self, message: str):
                try:
                    age = int(message)
                except ValueError:
                    self.specify(question='Are you sure?', direct_to='start')

                self.say(f'You are {age} years old')

        skill = AgeSkillWithDirectTo()

        result = skill.execute(
            message='twenty four', history=[], state_name=None, context={}
        )

        assert result.answers == ['Are you sure?']
        assert not result.is_relevant
        assert not result.is_finished
        assert result.direct_to is 'start'
        assert result.context == {}

        result = skill.execute(
            message='24', history=[], state_name='start', context=result.context
        )

        assert result.answers == ['You are 24 years old']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to is None
        assert result.context == {}

    def test_specify_with_direct_to_callable(self):

        class AgeSkillWithDirectTo(BaseSkill):
            def start(self, message: str):
                try:
                    age = int(message)
                except ValueError:
                    self.specify(question='Are you sure?', direct_to=self.start)

                self.say(f'You are {age} years old')

        skill = AgeSkillWithDirectTo()

        result = skill.execute(
            message='twenty four', history=[], state_name=None, context={}
        )

        assert result.answers == ['Are you sure?']
        assert not result.is_relevant
        assert not result.is_finished
        assert result.direct_to is 'start'
        assert result.context == {}

        result = skill.execute(
            message='24', history=[], state_name='start', context=result.context
        )

        assert result.answers == ['You are 24 years old']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to is None
        assert result.context == {}

    def test_override_initial_state_name(self):

        class EchoSkill(BaseSkill):

            INITIAL_STATE_NAME = 'echo'

            def echo(self, message: str):
                self.say(message)

        skill = EchoSkill()

        result = skill.execute(
            message='hello', history=[], state_name=None, context={}
        )

        assert result.answers == ['hello']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to is None
        assert result.context == {}

        result = skill.execute(
            message='bye', history=[], state_name='echo', context=result.context
        )

        assert result.answers == ['bye']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to is None
        assert result.context == {}

    def test_context_using(self):
        class MeetingSkillWithStates(BaseSkill):

            def start(self, message: str):
                self.context['greeting'] = 'Nice to meet you'
                self.ask('What is your name?', direct_to=self.meeting)

            def meeting(self, name: str):
                greeting = self.context['greeting']
                self.say(f'{greeting} {name}!')

        skill = MeetingSkillWithStates()

        result = skill.execute(
            message='hello', history=[], state_name=None, context={}
        )

        assert result.answers == ['What is your name?']
        assert result.is_relevant
        assert not result.is_finished
        assert result.direct_to == 'meeting'
        assert result.context == {'greeting': 'Nice to meet you'}

        result = skill.execute(
            message='Bob', history=[], state_name='meeting', context=result.context
        )

        assert result.answers == ['Nice to meet you Bob!']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to is None
        assert result.context == {'greeting': 'Nice to meet you'}
