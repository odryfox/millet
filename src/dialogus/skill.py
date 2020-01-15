from abc import abstractmethod, ABC
from typing import Callable


class InputMessageSignal(Exception):
    def __init__(self, message: str, direct_to: Callable, is_should_reweigh_skills: bool = False) -> None:
        self.message = message
        self.direct_to = direct_to
        self.is_should_reweigh_skills = is_should_reweigh_skills


class Skill(ABC):
    def __init__(self) -> None:
        self.answers = []
        self.next_state = self.start

    @abstractmethod
    def start(self, initial_message: str) -> None:
        pass

    def ask(self, question: str, direct_to: Callable):
        self.answers.append(question)
        self.next_state = direct_to
        raise InputMessageSignal(message=question, direct_to=direct_to)

    def specify(self, message: str, direct_to: Callable):
        self.answers.append(message)
        self.next_state = direct_to
        raise InputMessageSignal(message=message, direct_to=direct_to, is_should_reweigh_skills=True)

    def say(self, message: str) -> None:
        self.answers.append(message)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.answers == other.answers and self.next_state.__name__ == other.next_state.__name__
