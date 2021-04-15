from millet import BaseSkill


class TestSkill:

    def test_say(self):

        class EchoSkill(BaseSkill):
            def start(self, message: str):
                self.say(message)

        skill = EchoSkill()

        result = skill.execute(messages=['hello'], state_name=None)

        assert result.answers == ['hello']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to_state is None

        result = skill.execute(messages=['bye'], state_name=None)

        assert result.answers == ['bye']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to_state is None

    def test_double_say(self):

        class DoubleEchoSkill(BaseSkill):
            def start(self, message: str):
                self.say(message)
                self.say(message)

        skill = DoubleEchoSkill()

        result = skill.execute(messages=['hello'], state_name=None)

        assert result.answers == ['hello', 'hello']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to_state is None

        result = skill.execute(messages=['bye'], state_name=None)

        assert result.answers == ['bye', 'bye']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to_state is None

    def test_ask(self):

        class MeetingSkill(BaseSkill):
            def start(self, message: str):
                name = self.ask('What is your name?')
                self.say(f'Nice to meet you {name}!')

        skill = MeetingSkill()

        result = skill.execute(messages=['hello'], state_name=None)

        assert result.answers == ['What is your name?']
        assert result.is_relevant
        assert not result.is_finished
        assert result.direct_to_state is None

        result = skill.execute(messages=['hello', 'Bob'], state_name=None)

        assert result.answers == ['Nice to meet you Bob!']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to_state is None

    def test_ask_with_direct_to_state(self):

        class MeetingSkillWithStates(BaseSkill):

            def start(self, message: str):
                self.ask('What is your name?', direct_to_state='meeting')

            def meeting(self, name: str):
                self.say(f'Nice to meet you {name}!')

        skill = MeetingSkillWithStates()

        result = skill.execute(messages=['hello'], state_name=None)

        assert result.answers == ['What is your name?']
        assert result.is_relevant
        assert not result.is_finished
        assert result.direct_to_state == 'meeting'

        result = skill.execute(messages=['Bob'], state_name='meeting')

        assert result.answers == ['Nice to meet you Bob!']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to_state is None

    def test_specify(self):

        class AgeSkill(BaseSkill):
            def start(self, message: str):
                try:
                    age = int(message)
                except ValueError:
                    age = self.specify(question='Are you sure?')

                self.say(f'You are {age} years old')

        skill = AgeSkill()

        result = skill.execute(messages=['twenty four'], state_name=None)

        assert result.answers == ['Are you sure?']
        assert not result.is_relevant
        assert not result.is_finished
        assert result.direct_to_state is None

        result = skill.execute(messages=['twenty four', '24'], state_name=None)

        assert result.answers == ['You are 24 years old']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to_state is None

    def test_specify_with_direct_to_state(self):

        class AgeSkillWithDirectTo(BaseSkill):
            def start(self, message: str):
                try:
                    age = int(message)
                except ValueError:
                    self.specify(question='Are you sure?', direct_to_state='start')

                self.say(f'You are {age} years old')

        skill = AgeSkillWithDirectTo()

        result = skill.execute(messages=['twenty four'], state_name=None)

        assert result.answers == ['Are you sure?']
        assert not result.is_relevant
        assert not result.is_finished
        assert result.direct_to_state is 'start'

        result = skill.execute(messages=['24'], state_name=None)

        assert result.answers == ['You are 24 years old']
        assert result.is_relevant
        assert result.is_finished
        assert result.direct_to_state is None
