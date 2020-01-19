from millet.skill import SkillResult
from examples.word_chain_game import WordChainSkill


def test_game():
    vocabulary = ["hello", "owl", "lip", "plus"]

    skill = WordChainSkill(vocabulary=vocabulary)

    assert skill.send("Let's start!") == SkillResult(answers=["Ok", "My word: hello"], relevant=True) and not skill.finished
    assert skill.send("no") == SkillResult(answers=["You are lose!"], relevant=False) and skill.finished

    skill = WordChainSkill(vocabulary=vocabulary)

    assert skill.send("Let's start!") == SkillResult(answers=["Ok", "My word: hello"], relevant=True) and not skill.finished
    assert skill.send("owl") == SkillResult(answers=["My word: lip"], relevant=True) and not skill.finished
    assert skill.send("plus") == SkillResult(answers=["You are win!"], relevant=True) and skill.finished
