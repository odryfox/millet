from typing import Type

from dialogus.skill import InputMessageSignal, OutputMessageSignal, Skill


def test_say(bob_id: str, meeting_skill_class: Type[Skill]):
    meeting_skill = meeting_skill_class(global_context={}, skill_context={})

    try:
        meeting_skill.say("Hello")
        assert False, f"Expected {OutputMessageSignal.__name__}"
    except OutputMessageSignal as oms:
        assert oms.message == oms.key == "Hello"


def test_already_said(bob_id: str, meeting_skill_class: Type[Skill]):
    meeting_skill = meeting_skill_class(global_context={}, skill_context={"Hello": "Hello"})

    assert meeting_skill.say("Hello") is None


def test_say_with_custom_key(bob_id: str, meeting_skill_class: Type[Skill]):
    meeting_skill = meeting_skill_class(global_context={}, skill_context={})

    try:
        meeting_skill.say("Hello", "hello_key")
        assert False, f"Expected {OutputMessageSignal.__name__}"
    except OutputMessageSignal as oms:
        assert oms.message == "Hello" and oms.key == "hello_key"


def test_already_said_with_custom_key(bob_id: str, meeting_skill_class: Type[Skill]):
    meeting_skill = meeting_skill_class(global_context={}, skill_context={"hello_key": "Hello"})

    assert meeting_skill.say("Hello", "hello_key") is None


def test_ask(bob_id: str, meeting_skill_class: Type[Skill]):
    meeting_skill = meeting_skill_class(global_context={}, skill_context={})

    try:
        meeting_skill.ask("What's your name?")
        assert False, f"Expected {InputMessageSignal.__name__}"
    except InputMessageSignal as ims:
        assert ims.message == ims.key == "What's your name?"


def test_already_asked(bob_id: str, meeting_skill_class: Type[Skill]):
    meeting_skill = meeting_skill_class(global_context={}, skill_context={"What's your name?": "Bob"})

    assert meeting_skill.ask("What's your name?") == "Bob"


def test_ask_with_custom_key(bob_id: str, meeting_skill_class: Type[Skill]):
    meeting_skill = meeting_skill_class(global_context={}, skill_context={})

    try:
        meeting_skill.ask("What's your name?", "name_key")
        assert False, f"Expected {InputMessageSignal.__name__}"
    except InputMessageSignal as ims:
        assert ims.message == "What's your name?" and ims.key == "name_key"


def test_already_asked_with_custom_key(bob_id: str, meeting_skill_class: Type[Skill]):
    meeting_skill = meeting_skill_class(global_context={}, skill_context={"name_key": "Bob"})

    assert meeting_skill.ask("What's your name?", "name_key") == "Bob"
