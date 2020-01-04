from typing import List

from dialogus import Skill, Agent


def test_initial_message():
    class FriendNamesSkill(Skill):
        def run(self, message: str):
            your_name = message
            self.say(f'Your name is {your_name}')
            friend_name = self.ask("Enter your friend's name")
            self.say(f'Your friend is {friend_name}')

    def skill_classifier(message: str) -> List[Skill]:
        skills = []

        if 'Bob' in message:
            skills.append(FriendNamesSkill())

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('Bob')

    conversation.query('Bob')
    assert conversation.query('Alex') == ['Your friend is Alex']


def test_multi_answers():
    class MoodSkill(Skill):
        def run(self, message: str):
            self.say('Hello')
            self.say('Good day!')
            mood = self.ask('How are you?')
            ...

    def skill_classifier(message: str) -> List[Skill]:
        return [MoodSkill()]

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('Bob')

    answers = conversation.query('Hello')
    assert answers == ['Hello', 'Good day!', 'How are you?']
