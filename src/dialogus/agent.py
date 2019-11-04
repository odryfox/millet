from typing import Callable, List


class Agent:
    def __init__(self, strategies_activator: Callable[[str], List[Callable[[str], List[str]]]]):
        if not callable(strategies_activator):
            raise TypeError('strategies_activator must be a function')

        self.__strategies_activator = strategies_activator

    def answer_me(self, message: str) -> List[str]:
        answers = []
        strategies = self.__strategies_activator(message)

        for strategy in strategies:
            answers += strategy(message)

        return answers
