from typing import Any, List, Optional, Tuple

from millet.context import BaseContextManager, RAMContextManager, UserContext
from millet.skill import BaseSkill, BaseSkillClassifier


class Conversation:

    def __init__(self, agent: 'Agent', user_id: str) -> None:
        self.agent = agent
        self.user_id = user_id

    def query(self, message: Any) -> List[Any]:
        return self.agent.query(message=message, user_id=self.user_id)


class Agent:

    def __init__(
        self,
        skill_classifier: BaseSkillClassifier,
        context_manager: Optional[BaseContextManager] = RAMContextManager(),
    ) -> None:

        self._skill_classifier = skill_classifier
        self._context_manager = context_manager

    def conversation_with_user(self, user_id: str) -> Conversation:
        return Conversation(agent=self, user_id=user_id)

    def query(self, message: Any, user_id: str) -> List[Any]:
        user_context = self._context_manager.get_user_context(user_id)

        answers, new_user_context = self._query(message, user_context)

        self._context_manager.set_user_context(user_id, new_user_context)
        return answers

    def _query(self, message: Any, user_context: UserContext) -> Tuple[List[Any], UserContext]:
        history = user_context.history

        if user_context.skill_names:
            skill_names = user_context.skill_names
            state_names = user_context.state_names
        else:
            skill_names = self._skill_classifier.classify(message)
            state_names = [None for _ in skill_names]

        answers = []

        new_skill_names = []
        new_state_names = []
        new_history = []

        for skill_name, state_name in zip(skill_names, state_names):
            skill: BaseSkill = self._skill_classifier.skills_map[skill_name]

            skill_result = skill.execute(
                message=message,
                history=history,
                state_name=state_name,
            )

            if not skill_result.is_relevant:
                actual_skill_names = self._skill_classifier.classify(message)
                if actual_skill_names:
                    actual_state_names = [None for _ in actual_skill_names]
                    return self._query(
                        message=message,
                        user_context=UserContext(
                            skill_names=actual_skill_names,
                            state_names=actual_state_names,
                            history=[],
                        )
                    )

            answers.extend(skill_result.answers)

            if not skill_result.is_finished:
                new_skill_names = [skill_name]
                new_state_names = [skill_result.direct_to]

                if skill_result.direct_to:
                    new_history = []
                else:
                    new_history = history + [message]

                break

        new_user_context = UserContext(
            skill_names=new_skill_names,
            state_names=new_state_names,
            history=new_history,
        )
        return answers, new_user_context
