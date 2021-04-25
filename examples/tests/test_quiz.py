from typing import Dict, List

from examples.quiz import QuizSkill
from millet import Agent
from millet.skill import BaseSkill, BaseSkillClassifier


def test_quiz(greeting_quiz: List[Dict]):
    user_id = 'bob'

    skill = QuizSkill(quiz=greeting_quiz)

    class SkillClassifier(BaseSkillClassifier):
        @property
        def skills_map(self) -> Dict[str, BaseSkill]:
            return {
                'quiz': skill,
            }

        def classify(self, message: str) -> List[str]:
            if 'start' in message:
                return ['quiz']
            return []

    skill_classifier = SkillClassifier()

    agent = Agent(skill_classifier=skill_classifier)

    answers = agent.query('start', user_id)
    assert answers == ['Lets go', 'Indicate your gender.']

    answers = agent.query('MALE', user_id)
    assert answers == ['Incorrect variant!']

    answers = agent.query('male', user_id)
    assert answers == ['How old are you?']

    answers = agent.query('-24', user_id)
    assert answers == ['Not in the interval!']

    answers = agent.query('24', user_id)
    assert answers == ['Tell us about your hobbies.']

    answers = agent.query('I like programming!', user_id)
    assert answers == ['Thank you for your answers.']

    answers = agent.query('Thx', user_id)
    assert answers == []

    assert skill.answers == {'1': 'm', '2': 24, '3': 'I like programming!'}
