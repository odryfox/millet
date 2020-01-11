Dialogus
========

A simple framework for building complex dialogue systems.

.. image:: https://badge.fury.io/py/Dialogus.svg
    :target: https://badge.fury.io/py/Dialogus

.. image:: https://readthedocs.org/projects/dialogus/badge/?version=latest
    :target: https://dialogus.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/odryfox/dialogus.svg?branch=dev
    :target: https://travis-ci.org/odryfox/dialogus

.. image:: https://coveralls.io/repos/github/odryfox/dialogus/badge.svg?branch=dev
    :target: https://coveralls.io/github/odryfox/dialogus?branch=dev

A Simple Example
----------------

.. code-block:: python

    from typing import List, Type
    from dialogus import Agent, Skill

    class MeetingSkill(Skill):
        def run(self, message: str):
            name = self.ask("What is your name?")
            self.say(f"Nice to meet you {name}!")

    def skill_classifier(message: str) -> List[Type[Skill]]:
        return [MeetingSkill]

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user("Bob")

.. code-block:: python

    >>> conversation.query("Hello")
    ["What is your name?"]
    >>> conversation.query("Bob")
    ["Nice to meet you Bob!"]
