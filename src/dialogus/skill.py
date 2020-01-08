from abc import abstractmethod, ABC
from typing import Optional, List


class InputMessageSignal(Exception):
    def __init__(self, message: str, key: str) -> None:
        self.message = message
        self.key = key


class OutputMessageSignal(Exception):
    def __init__(self, message: str, key: str) -> None:
        self.message = message
        self.key = key


class Skill(ABC):
    def __init__(self, context: dict) -> None:
        self.__context = context

    def ask(self, message: str, key: Optional[str] = None) -> str:
        key = key or message
        answer = self.__context.get(key)
        if answer:
            return answer
        raise InputMessageSignal(message, key)

    def say(self, message: str, key: Optional[str] = None) -> None:
        key = key or message
        question = self.__context.get(key)
        if question:
            return
        raise OutputMessageSignal(message, key)

    @abstractmethod
    def run(self, message: str) -> List[str]:
        pass
