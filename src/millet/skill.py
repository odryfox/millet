from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from millet.timeouts import MessageTimeOut, MessageTimeOutException


class SkillSignal(Exception):

    def __init__(
        self,
        is_relevant: bool,
        direct_to: Optional[str],
        timeout: Optional[int],
    ) -> None:
        self.is_relevant = is_relevant
        self.direct_to = direct_to
        self.timeout = timeout


class SkillResult:

    def __init__(
        self,
        answers: List[Any],
        is_relevant: bool,
        is_finished: bool,
        direct_to: Optional[str],
        context: dict,
        timeout: Optional[int],
    ) -> None:
        self.answers = answers
        self.is_relevant = is_relevant
        self.is_finished = is_finished
        self.direct_to = direct_to
        self.context = context
        self.timeout = timeout


class BaseSkill(ABC):

    initial_state_name = 'execute'

    _history = []
    _answers = []

    context = {}

    side_functions = []
    side_methods = []

    user_id = ''

    @property
    def _is_silent_mood(self):
        return bool(self._history)

    def say(self, message: Any) -> None:
        self._have_new_message(message=message)

    def _have_new_message(self, *, message: Any):
        if self._is_silent_mood:
            return

        self._answers.append(message)

    def ask(
        self,
        question: Any,
        direct_to: Optional[Union[str, callable]] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        self._have_new_message(message=question)
        return self._need_new_message(
            is_relevant=True,
            direct_to=direct_to,
            timeout=timeout,
        )

    def specify(
        self,
        question: Any,
        direct_to: Optional[Union[str, callable]] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        self._have_new_message(message=question)
        return self._need_new_message(
            is_relevant=False,
            direct_to=direct_to,
            timeout=timeout,
        )

    def _need_new_message(
        self,
        is_relevant: bool,
        direct_to: Optional[Union[str, callable]],
        timeout: Optional[int],
    ) -> Any:
        if self._is_silent_mood:
            message = self._history.pop(0)
            if isinstance(message, MessageTimeOut):
                raise MessageTimeOutException
            else:
                return message

        if callable(direct_to):
            direct_to = direct_to.__name__

        raise SkillSignal(
            is_relevant=is_relevant,
            direct_to=direct_to,
            timeout=timeout,
        )

    def run(
        self,
        message: Any,
        history: List[Any],
        state_name: Optional[str],
        context: dict,
    ) -> SkillResult:
        self._history = history
        self._history.append(message)

        self._answers = []
        self.context = context

        initial_message = self._history.pop(0)

        if not state_name:
            state_name = self.initial_state_name

        state = getattr(self, state_name)

        is_finished = False
        is_relevant = True
        direct_to = None
        timeout = None

        try:
            answer = state(initial_message)
            if answer is not None:
                self._answers.append(answer)
            is_finished = True
        except SkillSignal as signal:
            is_relevant = signal.is_relevant
            direct_to = signal.direct_to
            timeout = signal.timeout

        return SkillResult(
            answers=self._answers,
            is_relevant=is_relevant,
            is_finished=is_finished,
            direct_to=direct_to,
            context=self.context,
            timeout=timeout,
        )


class BaseSkillClassifier(ABC):

    @property
    @abstractmethod
    def skills_map(self) -> Dict[str, BaseSkill]:
        pass

    @abstractmethod
    def classify(self, message: Any) -> List[str]:
        pass
