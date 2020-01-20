from typing import List

from examples.quiz import QuizSkill
from millet.skill import SkillResult


def test_quiz(greeting_quiz: List[dict]):
    skill = QuizSkill(quiz=greeting_quiz)

    assert skill.send("Hello") == SkillResult(answers=["Let's go", "Indicate your gender."], relevant=True) and not skill.finished
    assert skill.send("MALE") == SkillResult(answers=["Incorrect variant!"], relevant=False) and not skill.finished
    assert skill.send("male") == SkillResult(answers=["How old are you?"], relevant=True) and not skill.finished
    assert skill.send("-42") == SkillResult(answers=["Not in the interval!"], relevant=False) and not skill.finished
    assert skill.send("42") == SkillResult(answers=["Tell us about your hobbies."], relevant=True) and not skill.finished
    assert skill.send("I like programming!") == SkillResult(answers=["Thank you for your answers."], relevant=True) and skill.finished
    assert skill.answers == {"1": "m", "2": 42, "3": "I like programming!"}
