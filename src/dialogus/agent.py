from typing import Callable, List, Type, Optional

from dialogus.context import AgentContext, UserContext, DialogContext, RAMAgentContext
from dialogus.skill import Skill, InputMessageSignal


class Conversation:
    def __init__(self, agent: "Agent", user_id: str):
        self.agent = agent
        self.user_id = user_id

    def query(self, message: str) -> List[str]:
        return self.agent.query(message, self.user_id)


class Agent:
    def __init__(self, skill_classifier: Callable[[str], List[Type[Skill]]], context: Optional[AgentContext] = None):
        if not callable(skill_classifier):
            raise TypeError("skill_classifier must be a function")

        if not context:
            context = RAMAgentContext()

        self.__skill_classifier = skill_classifier
        self.context = context

    def conversation_with_user(self, user_id: str) -> Conversation:
        return Conversation(agent=self, user_id=user_id)

    def query(self, message: str, user_id: str) -> List[str]:
        user_context = self.context.get_user_context(user_id)

        if not user_context.dialogs:
            skill_classes = self.__skill_classifier(message)
            user_context.dialogs = [DialogContext(skill_class=skill_class, params={"initial_message": message}) for skill_class in skill_classes]

        dialogs = user_context.dialogs

        answers = []

        for dialog in dialogs:
            skill = dialog.skill_class(global_context=user_context.params, skill_context=dialog.params)
            state_name = dialog.params.get("next_state_name", "start")
            state = getattr(skill, state_name)
            try:
                state(message)
                answers += skill.answers
                user_context = UserContext(dialogs=[], params=user_context.params)
            except InputMessageSignal as ims:
                if ims.is_should_reweigh_skills:
                    skill_classes = self.__skill_classifier(message)
                    if skill_classes:
                        user_context.dialogs = []
                        self.context.set_user_context(user_id, user_context)
                        return self.query(message, user_id)

                dialog.params["next_state_name"] = ims.direct_to.__name__
                answers += skill.answers
                break

        self.context.set_user_context(user_id, user_context)

        return answers
