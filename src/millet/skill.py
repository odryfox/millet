from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Any


class SkillSignal(Exception):
    pass


class IterationSignal(SkillSignal):
    def __init__(self, *, relevant: bool):
        self.relevant = relevant


class RestartIterationSignal(IterationSignal):
    pass


class FinishIterationSignal(IterationSignal):
    pass


class SkillResult:
    def __init__(self, *, answers: List[Any], relevant: bool):
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
        self._answers = []

    def reset(self) -> None:
        self._finished = False
        self._context = {}
        self._expected_question_key = None
        self._current_state = self.start
        self._initial_message = None

    def restart(self, initial_message: Any):
        self._restart(initial_message=initial_message, relevant=True)

    def retry(self, initial_message: Any):
        self._restart(initial_message=initial_message, relevant=False)

    def _restart(self, *, initial_message: Any, relevant: bool):
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
    def start(self, initial_message: Any):
        pass

    def say(self, message: Any):
        self._have_new_message(message=message)

    def _have_new_message(self, *, message: Any):
        message_str = str(message)
        if message_str in self._context:
            return
        self._context[message_str] = None
        self._answers.append(message)

    def ask(self, question: Any, direct_to: Optional[Callable] = None) -> Any:
        return self._need_new_message(question=question, direct_to=direct_to, relevant=True)

    def specify(self, question: Any, direct_to: Optional[Callable] = None):
        return self._need_new_message(question=question, direct_to=direct_to, relevant=False)

    def _need_new_message(self, *, question: Any, direct_to: Optional[Callable], relevant: bool) -> Any:
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

    def _exit(self, *, message: Any, relevant: bool):
        self._have_new_message(message=message)
        self.reset()
        self._finished = True
        self._current_state = None
        raise FinishIterationSignal(relevant=relevant)

    def finish(self, message: Any):
        self._exit(message=message, relevant=True)

    def abort(self, reason: Any):
        self._exit(message=reason, relevant=False)

    def send(self, message: Any):
        if self.finished:
            raise StopIteration

        if self._expected_question_key:
            self._context[self._expected_question_key] = message
            self._expected_question_key = None

        self._answers = []
        relevant = True

        self._initial_message = self._initial_message or message

        while True:
            try:
                self._current_state(self._initial_message)
                self._finished = True
                break
            except IterationSignal as signal:
                relevant &= signal.relevant
                if isinstance(signal, FinishIterationSignal):
                    break

        return SkillResult(answers=self._answers, relevant=relevant)
