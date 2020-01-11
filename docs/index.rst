.. Dialogus documentation master file, created by
   sphinx-quickstart on Sat Dec 28 22:27:23 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Dialogus's documentation!
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


A Simple Example
----------------

.. code-block:: python

    from typing import List
    from dialogus import Agent, Skill

    class MeetingSkill(Skill):
        def run(self, message: str):
            name = self.ask("What is your name?")
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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
