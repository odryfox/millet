from typing import Callable, Optional, List


class Agent:
    def __init__(self, strategy_activator: Optional[Callable[[str], Callable[[str], List[str]]]]):
        self.__strategy_activator = strategy_activator

    def answer_me(self, message: str) -> List[str]:
        if not self.__strategy_activator:
            return []

        strategy = self.__strategy_activator(message)
        if strategy is None:
            return []

        return strategy(message)
