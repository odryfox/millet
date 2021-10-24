from typing import Dict, List

from examples.word_chain_game import WordChainSkill
from millet import Agent
from millet.skill import BaseSkill, BaseSkillClassifier


def test_win_game():
    vocabulary = ['hello', 'owl', 'lip', 'plus']

    skill = WordChainSkill(vocabulary=vocabulary)

    class SkillClassifier(BaseSkillClassifier):
        @property
        def skills_map(self) -> Dict[str, BaseSkill]:
            return {
                'game': skill,
            }

        def classify(self, message: str, user_id: str) -> List[str]:
            if 'start' in message:
                return ['game']
            return []

    skill_classifier = SkillClassifier()

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('100500')

    answers = conversation.process_message('start')
    assert answers == ['Lets start', 'My word: hello']

    answers = conversation.process_message('bye')
    assert answers == ['You are lose!']

    answers = conversation.process_message('owl')
    assert answers == []


def test_losw_game():
    vocabulary = ['hello', 'owl', 'lip', 'plus']

    skill = WordChainSkill(vocabulary=vocabulary)

    class SkillClassifier(BaseSkillClassifier):
        @property
        def skills_map(self) -> Dict[str, BaseSkill]:
            return {
                'game': skill,
            }

        def classify(self, message: str, user_id: str) -> List[str]:
            if 'start' in message:
                return ['game']
            return []

    skill_classifier = SkillClassifier()

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('100500')

    answers = conversation.process_message('start')
    assert answers == ['Lets start', 'My word: hello']

    answers = conversation.process_message('owl')
    assert answers == ['My word: lip']

    answers = conversation.process_message('plus')
    assert answers == ['You are win!']
