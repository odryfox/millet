from typing import Callable, Optional


class Agent:
    def __init__(self, strategy_activator: Optional[Callable[[str], Callable[[str], str]]]):
        self.__strategy_activator = strategy_activator

    def answer_me(self, message: str) -> Optional[str]:
        if not self.__strategy_activator:
            return None

        strategy = self.__strategy_activator(message)
        if strategy is None:
            return None

        return strategy(message)
