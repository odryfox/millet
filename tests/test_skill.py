from typing import List, Type

from dialogus import Skill, Agent


def test_initial_message(friend_name_skill: Type[Skill]):
    def skill_classifier(message: str) -> List[Type[Skill]]:
        skills = []

        if 'Bob' in message:
            skills.append(friend_name_skill)

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('Bob')

    conversation.query('Bob')
    assert conversation.query('Alex') == ['Your friend is Alex']


def test_multi_answers(mood_skill_class: Type[Skill]):
    def skill_classifier(message: str) -> List[Type[Skill]]:
        return [mood_skill_class]

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('Bob')

    answers = conversation.query('Hello')
    assert answers == ['Hello', 'Good day!', 'How are you?']
