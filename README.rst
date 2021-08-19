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

    from typing import Dict, List
    from millet import Agent, BaseSkill, BaseSkillClassifier


    class MeetingSkill(BaseSkill):
        def start(self, initial_message: str):
            name = self.ask(question='What is your name?')
            self.say(f'Nice to meet you {name}!')


    class SkillClassifier(BaseSkillClassifier):
        @property
        def skills_map(self) -> Dict[str, BaseSkill]:
            return {
                'meeting': MeetingSkill(),
            }

        def classify(self, message: str) -> List[str]:
            return ['meeting']


    skill_classifier = SkillClassifier()
    agent = Agent(skill_classifier=skill_classifier)
    conversation = agent.conversation_with_user('100500')

.. code-block:: python

    >>> conversation.query('Hello')
    ['What is your name?']
    >>> conversation.query('Bob')
    ['Nice to meet you Bob!']
