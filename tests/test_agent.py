from typing import Optional, Callable

from src.dialogus.agent import Agent


def test_echo_agent():
    def strategy_echo(message: str) -> str:
        return message

    def strategy_activator(message: str) -> Optional[Callable[[str], str]]:
        return strategy_echo

    agent = Agent(strategy_activator=strategy_activator)

    input_message = 'Hello'
    output_message = agent.answer_me(input_message)

    assert output_message == input_message


def test_duplicate_agent():
    def strategy_duplicate(message: str) -> str:
        return message * 2

    def strategy_activator(message: str) -> Optional[Callable[[str], str]]:
        return strategy_duplicate

    agent = Agent(strategy_activator=strategy_activator)

    input_message = 'Hello'
    output_message = agent.answer_me(input_message)

    assert output_message == 'HelloHello'


def test_empty_strategy_activator():
    agent = Agent(strategy_activator=None)

    input_message = 'Hello'
    output_message = agent.answer_me(input_message)

    assert output_message is None


def test_choice_of_strategy():
    def strategy_greeting(message: str) -> str:
        return 'Hi'

    def strategy_parting(message: str) -> str:
        return 'Bye'

    def strategy_activator(message: str) -> Optional[Callable[[str], str]]:
        if message == 'Hello':
            return strategy_greeting

        if message == 'Goodbye':
            return strategy_parting

        return None

    agent = Agent(strategy_activator=strategy_activator)

    input_message = 'Hello'
    output_message = agent.answer_me(input_message)

    assert output_message == 'Hi'

    input_message = 'Goodbye'
    output_message = agent.answer_me(input_message)

    assert output_message == 'Bye'

    input_message = 'How are you?'
    output_message = agent.answer_me(input_message)

    assert output_message is None
