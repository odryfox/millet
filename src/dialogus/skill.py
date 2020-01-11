from abc import abstractmethod, ABC
from typing import Optional


class InputMessageSignal(Exception):
    def __init__(self, message: str, key: str, is_should_reweigh_skills: bool = False) -> None:
        self.message = message
        self.key = key
        self.is_should_reweigh_skills = is_should_reweigh_skills


class OutputMessageSignal(Exception):
    def __init__(self, message: str, key: str) -> None:
        self.message = message
        self.key = key


class Skill(ABC):
    def __init__(self, *, global_context: dict, skill_context: dict) -> None:
        self.global_context = global_context
        self.__skill_context = skill_context

    def ask(self, message: str, key: Optional[str] = None) -> str:
        key = key or message
        answer = self.__skill_context.get(key)
        if answer:
            return answer
        raise InputMessageSignal(message, key)

    def specify(self, message: str, key: str) -> None:
        raise InputMessageSignal(message, key, True)

    def say(self, message: str, key: Optional[str] = None) -> None:
        key = key or message
        question = self.__skill_context.get(key)
        if question:
            return
        raise OutputMessageSignal(message, key)

    @abstractmethod
    def run(self, message: str) -> None:
        pass
