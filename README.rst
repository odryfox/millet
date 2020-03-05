Millet
======

A simple framework for building complex dialogue systems.

.. image:: https://badge.fury.io/py/Millet.svg
    :target: https://badge.fury.io/py/Millet

.. image:: https://readthedocs.org/projects/millet/badge/?version=latest
    :target: https://millet.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/odryfox/millet.svg?branch=master
    :target: https://travis-ci.org/odryfox/millet

.. image:: https://coveralls.io/repos/github/odryfox/millet/badge.svg?branch=master
    :target: https://coveralls.io/github/odryfox/millet?branch=master


Installing
----------

.. code-block:: text

    pip install Millet


A Simple Example
----------------

.. code-block:: python

    from typing import List, Type
    from millet import Agent, Skill

    class MeetingSkill(Skill):
        def start(self, initial_message: str):
            name = self.ask(question="What is your name?")
            self.say(f"Nice to meet you {name}!")

    def skill_classifier(message: str) -> List[Skill]:
        return [MeetingSkill()]

    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user("Bob")

.. code-block:: python

    >>> conversation.query("Hello")
    ["What is your name?"]
    >>> conversation.query("Bob")
    ["Nice to meet you Bob!"]
