from abc import ABC, abstractmethod
from typing import Any, List, Optional


class SkillSignal(Exception):

    def __init__(self, is_relevant: bool, direct_to_state: Optional[str]) -> None:
        self.is_relevant = is_relevant
        self.direct_to_state = direct_to_state


class SkillResult:

    def __init__(
        self,
        answers: List[Any],
        is_relevant: bool,
        is_finished: bool,
        direct_to_state: Optional[str],
    ) -> None:
        self.answers = answers
        self.is_relevant = is_relevant
        self.is_finished = is_finished
        self.direct_to_state = direct_to_state


class BaseSkill(ABC):

    INITIAL_STATE_NAME = 'start'

    _history = []
    _answers = []

    @property
    def _is_silent_mood(self):
        return bool(self._history)

    def say(self, message: Any) -> None:
        self._have_new_message(message=message)

    def _have_new_message(self, *, message: Any):
        if self._is_silent_mood:
            return

        self._answers.append(message)

    def ask(self, question: Any, direct_to_state: Optional[str] = None) -> Any:
        self._have_new_message(message=question)
        return self._need_new_message(
            is_relevant=True,
            direct_to_state=direct_to_state,
        )

    def specify(self, question: Any, direct_to_state: Optional[str] = None) -> Any:
        self._have_new_message(message=question)
        return self._need_new_message(
            is_relevant=False,
            direct_to_state=direct_to_state,
        )

    def _need_new_message(self, is_relevant: bool, direct_to_state: Optional[str]) -> Any:
        if self._is_silent_mood:
            message = self._history.pop(0)
            return message

        raise SkillSignal(
            is_relevant=is_relevant,
            direct_to_state=direct_to_state,
        )

    def execute(self, message: Any, history: List[Any], state_name: Optional[str]) -> SkillResult:
        self._history = history
        self._history.append(message)

        self._answers = []

        initial_message = self._history.pop(0)

        if not state_name:
            state_name = self.INITIAL_STATE_NAME

        state = getattr(self, state_name)

        is_finished = False
        is_relevant = True
        direct_to_state = None

        try:
            state(initial_message)
            is_finished = True
        except SkillSignal as signal:
            is_relevant = signal.is_relevant
            direct_to_state = signal.direct_to_state

        return SkillResult(
            answers=self._answers,
            is_relevant=is_relevant,
            is_finished=is_finished,
            direct_to_state=direct_to_state,
        )


class BaseSkillClassifier(ABC):

    @property
    @abstractmethod
    def skills_map(self) -> dict[str, BaseSkill]:
        pass

    @abstractmethod
    def classify(self, message: Any) -> List[str]:
        pass
