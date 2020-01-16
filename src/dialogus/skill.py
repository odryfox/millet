from abc import ABC, abstractmethod
from typing import List, Optional, Callable


class SkillSignal(Exception):
    pass


class OutputMessageSignal(SkillSignal):
    def __init__(self, *, message: str):
        self.message = message


class IterationSignal(SkillSignal):
    def __init__(self, *, relevant: bool):
        self.relevant = relevant


class RestartIterationSignal(IterationSignal):
    pass


class FinishIterationSignal(IterationSignal):
    pass


class SkillResult:
    def __init__(self, *, answers: List[str], relevant: bool):
        self.answers = answers
        self.relevant = relevant

    def __repr__(self):
        return f"{self.__class__.__name__}(answers={self.answers}, relevant={self.relevant})"

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.answers == other.answers and self.relevant == other.relevant


class Skill(ABC):
    def __init__(self):
        self._finished = False
        self._context = {}
        self._expected_question_key = None
        self._current_state = self.start
        self._initial_message = None
        self.global_context = None

    def reset(self) -> None:
        self._finished = False
        self._context = {}
        self._expected_question_key = None
        self._current_state = self.start
        self._initial_message = None

    def restart(self, initial_message: str):
        self._restart(initial_message=initial_message, relevant=True)

    def retry(self, initial_message: str):
        self._restart(initial_message=initial_message, relevant=False)

    def _restart(self, *, initial_message: str, relevant: bool):
        self.reset()
        self._initial_message = initial_message
        raise RestartIterationSignal(relevant=relevant)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self._finished == other._finished
            and self._context == other._context
            and self._expected_question_key == other._expected_question_key
            and self._current_state.__name__ == other._current_state.__name__
            and self._initial_message == other._initial_message
        )

    @property
    def finished(self) -> bool:
        return self._finished

    @abstractmethod
    def start(self, initial_message: str):
        pass

    def say(self, message: str):
        self._have_new_message(message=message)

    def _have_new_message(self, *, message: str):
        if message in self._context:
            return
        self._context[message] = None
        raise OutputMessageSignal(message=message)

    def ask(self, question: str, direct_to: Optional[Callable] = None) -> str:
        return self._need_new_message(question=question, direct_to=direct_to, relevant=True)

    def specify(self, question: str, direct_to: Optional[Callable] = None):
        return self._need_new_message(question=question, direct_to=direct_to, relevant=False)

    def _need_new_message(self, *, question: str, direct_to: Optional[Callable], relevant: bool) -> str:
        self._have_new_message(message=question)
        if direct_to:
            self._context = {}
            self._current_state = direct_to
            self._initial_message = None
        else:
            if question in self._context:
                answer = self._context[question]
                if answer is not None:
                    return answer
            self._expected_question_key = question
        raise FinishIterationSignal(relevant=relevant)

    def _exit(self, *, message: str, relevant: bool):
        self._have_new_message(message=message)
        self.reset()
        self._finished = True
        self._current_state = None
        raise FinishIterationSignal(relevant=relevant)

    def finish(self, message: str):
        self._exit(message=message, relevant=True)

    def abort(self, reason: str):
        self._exit(message=reason, relevant=False)

    def send(self, message: str):
        if self.finished:
            raise StopIteration

        if self._expected_question_key:
            self._context[self._expected_question_key] = message
            self._expected_question_key = None

        answers = []
        relevant = True

        self._initial_message = self._initial_message or message

        while True:
            try:
                self._current_state(self._initial_message)
                self._finished = True
                break
            except OutputMessageSignal as signal:
                answers.append(signal.message)
            except IterationSignal as signal:
                relevant &= signal.relevant
                if isinstance(signal, FinishIterationSignal):
                    break

        return SkillResult(answers=answers, relevant=relevant)
