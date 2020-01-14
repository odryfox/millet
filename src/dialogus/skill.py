from abc import abstractmethod, ABC
from typing import Callable


class InputMessageSignal(Exception):
    def __init__(self, message: str, direct_to: Callable, is_should_reweigh_skills: bool = False) -> None:
        self.message = message
        self.direct_to = direct_to
        self.is_should_reweigh_skills = is_should_reweigh_skills


class Skill(ABC):
    def __init__(self, *, global_context: dict, skill_context: dict) -> None:
        self.global_context = global_context
        self.__skill_context = skill_context
        self.answers = []

    @abstractmethod
    def start(self, initial_message: str) -> None:
        pass

    def ask(self, question: str, direct_to: Callable):
        self.answers.append(question)
        raise InputMessageSignal(message=question, direct_to=direct_to)

    def specify(self, message: str, direct_to: Callable):
        self.answers.append(message)
        raise InputMessageSignal(message=message, direct_to=direct_to, is_should_reweigh_skills=True)

    def say(self, message: str) -> None:
        self.answers.append(message)
