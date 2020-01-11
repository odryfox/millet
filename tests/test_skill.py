from typing import Type

from dialogus.skill import InputMessageSignal, OutputMessageSignal, Skill, \
    get_or_call


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


def test_specify(bob_id: str, age_skill_class: Type[Skill]):
    age_skill = age_skill_class(global_context={}, skill_context={"What's your name?": "Forty two"})

    try:
        age_skill.specify("Incorrect age: expected number, repeat pls", "What's your name?")
        assert False, f"Expected {InputMessageSignal.__name__}"
    except InputMessageSignal as ims:
        assert ims.message == "Incorrect age: expected number, repeat pls" and ims.key == "What's your name?" and ims.is_should_reweigh_skills


def test_get_or_call():
    class OrderSkill(Skill):
        number_of_orders = 0

        def run(self, message: str):
            return self.get_or_call(self.order, 1)

        def order(self, product_id: int) -> int:
            self.number_of_orders += 1
            return 123

    order_skill = OrderSkill(global_context={}, skill_context={})
    assert order_skill.number_of_orders == 0
    assert order_skill.run("order pls") == 123
    assert order_skill.number_of_orders == 1
    assert order_skill.run("order pls") == 123
    assert order_skill.number_of_orders == 1


def test_get_or_call_decorator():
    class OrderSkill(Skill):
        number_of_orders = 0

        def run(self, message: str):
            return self.order(1)

        @get_or_call
        def order(self, product_id: int) -> int:
            self.number_of_orders += 1
            return 123

    order_skill = OrderSkill(global_context={}, skill_context={})
    assert order_skill.number_of_orders == 0
    assert order_skill.run("order pls") == 123
    assert order_skill.number_of_orders == 1
    assert order_skill.run("order pls") == 123
    assert order_skill.number_of_orders == 1
