from typing import Type

from dialogus.skill import InputMessageSignal, Skill


def test_say(bob_id: str, meeting_skill_class: Type[Skill]):
    meeting_skill = meeting_skill_class(global_context={}, skill_context={})
    meeting_skill.say("Hello")
    assert meeting_skill.answers == ["Hello"]


def test_ask(bob_id: str, meeting_skill_class: Type[Skill]):
    meeting_skill = meeting_skill_class(global_context={}, skill_context={})

    try:
        meeting_skill.ask("What's your name?", direct_to=meeting_skill.start)
        assert False, f"Expected {InputMessageSignal.__name__}"
    except InputMessageSignal as ims:
        assert ims.message == "What's your name?" and ims.direct_to == meeting_skill.start and not ims.is_should_reweigh_skills
        assert meeting_skill.answers == ["What's your name?"]


def test_specify(bob_id: str, age_skill_class: Type[Skill]):
    age_skill = age_skill_class(global_context={}, skill_context={})

    try:
        age_skill.specify("Incorrect age: expected number, repeat pls", direct_to=age_skill.start)
        assert False, f"Expected {InputMessageSignal.__name__}"
    except InputMessageSignal as ims:
        assert ims.message == "Incorrect age: expected number, repeat pls" and ims.direct_to == age_skill.start and ims.is_should_reweigh_skills
        assert age_skill.answers == ["Incorrect age: expected number, repeat pls"]
