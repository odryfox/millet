from typing import List

from examples.word_chain_game import WordChainSkill
from millet import Agent
from millet.skill import BaseSkill, BaseSkillClassifier


def test_win_game():
    vocabulary = ['hello', 'owl', 'lip', 'plus']

    skill = WordChainSkill(vocabulary=vocabulary)

    class SkillClassifier(BaseSkillClassifier):
        @property
        def skills_map(self) -> dict[str, BaseSkill]:
            return {
                'game': skill,
            }

        def classify(self, message: str) -> List[str]:
            if 'start' in message:
                return ['game']
            return []

    skill_classifier = SkillClassifier()

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('bob')

    answers = conversation.query('start')
    assert answers == ['Lets start', 'My word: hello']

    answers = conversation.query('bye')
    assert answers == ['You are lose!']

    answers = conversation.query('owl')
    assert answers == []


def test_losw_game():
    vocabulary = ['hello', 'owl', 'lip', 'plus']

    skill = WordChainSkill(vocabulary=vocabulary)

    class SkillClassifier(BaseSkillClassifier):
        @property
        def skills_map(self) -> dict[str, BaseSkill]:
            return {
                'game': skill,
            }

        def classify(self, message: str) -> List[str]:
            if 'start' in message:
                return ['game']
            return []

    skill_classifier = SkillClassifier()

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('bob')

    answers = conversation.query('start')
    assert answers == ['Lets start', 'My word: hello']

    answers = conversation.query('owl')
    assert answers == ['My word: lip']

    answers = conversation.query('plus')
    assert answers == ['You are win!']
