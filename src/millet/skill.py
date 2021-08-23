from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class SkillSignal(Exception):

    def __init__(self, is_relevant: bool, direct_to: Optional[str]) -> None:
        self.is_relevant = is_relevant
        self.direct_to = direct_to


class SkillResult:

    def __init__(
        self,
        answers: List[Any],
        is_relevant: bool,
        is_finished: bool,
        direct_to: Optional[str],
        context: dict,
    ) -> None:
        self.answers = answers
        self.is_relevant = is_relevant
        self.is_finished = is_finished
        self.direct_to = direct_to
        self.context = context


class BaseSkill(ABC):

    INITIAL_STATE_NAME = 'start'

    _history = []
    _answers = []

    context = {}

    side_functions = []
    side_methods = []

    @property
    def _is_silent_mood(self):
        return bool(self._history)

    def say(self, message: Any) -> None:
        self._have_new_message(message=message)

    def _have_new_message(self, *, message: Any):
        if self._is_silent_mood:
            return

        self._answers.append(message)

    def ask(self, question: Any, direct_to: Optional[Union[str, callable]] = None) -> Any:
        self._have_new_message(message=question)
        return self._need_new_message(
            is_relevant=True,
            direct_to=direct_to,
        )

    def specify(self, question: Any, direct_to: Optional[Union[str, callable]] = None) -> Any:
        self._have_new_message(message=question)
        return self._need_new_message(
            is_relevant=False,
            direct_to=direct_to,
        )

    def _need_new_message(self, is_relevant: bool, direct_to: Optional[Union[str, callable]]) -> Any:
        if self._is_silent_mood:
            message = self._history.pop(0)
            return message

        if callable(direct_to):
            direct_to = direct_to.__name__

        raise SkillSignal(
            is_relevant=is_relevant,
            direct_to=direct_to,
        )

    def execute(
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
            state_name = self.INITIAL_STATE_NAME

        state = getattr(self, state_name)

        is_finished = False
        is_relevant = True
        direct_to = None

        try:
            state(initial_message)
            is_finished = True
        except SkillSignal as signal:
            is_relevant = signal.is_relevant
            direct_to = signal.direct_to

        return SkillResult(
            answers=self._answers,
            is_relevant=is_relevant,
            is_finished=is_finished,
            direct_to=direct_to,
            context=self.context,
        )


class BaseSkillClassifier(ABC):

    @property
    @abstractmethod
    def skills_map(self) -> Dict[str, BaseSkill]:
        pass

    @abstractmethod
    def classify(self, message: Any) -> List[str]:
        pass
