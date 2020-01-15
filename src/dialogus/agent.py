from typing import Callable, List, Optional

from dialogus.context import AgentContext, UserContext, RAMAgentContext
from dialogus.skill import Skill, InputMessageSignal


class Conversation:
    def __init__(self, agent: "Agent", user_id: str):
        self.agent = agent
        self.user_id = user_id

    def query(self, message: str) -> List[str]:
        return self.agent.query(message, self.user_id)


class Agent:
    def __init__(self, skill_classifier: Callable[[str], List[Skill]], context: Optional[AgentContext] = None):
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

        if not user_context.skills:
            user_context.skills = self.__skill_classifier(message)

        skills = user_context.skills

        answers = []

        for skill in skills:
            skill.global_context = user_context.params
            try:
                skill.next_state(message)
                answers += skill.answers[:]
                skill.answers = []
                user_context = UserContext(skills=[], params=user_context.params)
            except InputMessageSignal as ims:
                if ims.is_should_reweigh_skills:
                    skills = self.__skill_classifier(message)
                    if skills:
                        user_context.skills = []
                        self.context.set_user_context(user_id, user_context)
                        return self.query(message, user_id)

                answers += skill.answers[:]
                skill.answers = []
                user_context.skills = [skill]
                break

        self.context.set_user_context(user_id, user_context)

        return answers
