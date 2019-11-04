from typing import Callable, List


class Agent:
    def __init__(self, strategy_activator: Callable[[str], Callable[[str], List[str]]]):
        if not callable(strategy_activator):
            raise TypeError('strategy_activator must be a function')

        self.__strategy_activator = strategy_activator

    def answer_me(self, message: str) -> List[str]:
        strategy = self.__strategy_activator(message)
        if strategy is None:
            return []

        return strategy(message)
