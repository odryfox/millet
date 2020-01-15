from abc import abstractmethod, ABC
from typing import Callable, Optional


class InputMessageSignal(Exception):
    def __init__(self, message: str, direct_to: Optional[Callable], is_should_reweigh_skills: bool = False) -> None:
        self.message = message
        self.direct_to = direct_to
        self.is_should_reweigh_skills = is_should_reweigh_skills


class Skill(ABC):
    def __init__(self) -> None:
        self.answers = []
        self.next_state = self.start
        self.keys = {}
        self.waiting_key = None
        self.initial_message = None

    @abstractmethod
    def start(self, initial_message: str) -> None:
        pass

    def ask(self, question: str, direct_to: Optional[Callable] = None):
        return self._input_message(question, direct_to, False)

    def specify(self, message: str, direct_to: Optional[Callable] = None):
        return self._input_message(message, direct_to, True)

    def _input_message(self, question: str, direct_to: Optional[Callable], is_should_reweigh_skills: bool) -> str:
        if not direct_to:
            result = self.keys.get(question)
            if result:
                return result
            self.waiting_key = question

        self.answers.append(question)
        self.next_state = direct_to or self.next_state
        raise InputMessageSignal(message=question, direct_to=direct_to, is_should_reweigh_skills=is_should_reweigh_skills)

    def say(self, message: str) -> None:
        self._output_message(message)

    def _output_message(self, message):
        result = self.keys.get(message)
        if result:
            return
        self.keys[message] = message
        self.answers.append(message)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.answers == other.answers and self.next_state.__name__ == other.next_state.__name__
