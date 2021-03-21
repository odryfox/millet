from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Any, Union

from millet.context import AgentContext, RAMAgentContext
from millet.skill import Skill


class BaseSkillClassifier(ABC):
    @abstractmethod
    def classify(self, message: Any) -> List[Skill]:
        pass


FunctionalSkillClassifier = Callable[[Any], List[Skill]]


class Conversation:
    def __init__(self, agent: "Agent", user_id: str):
        self.agent = agent
        self.user_id = user_id

    def query(self, message: Any) -> List[Any]:
        return self.agent.query(message, self.user_id)


class Agent:
    def __init__(
        self,
        skill_classifier: Union[BaseSkillClassifier, FunctionalSkillClassifier],
        context: Optional[AgentContext] = None,
    ):
        if (
            not isinstance(skill_classifier, BaseSkillClassifier) and
            not callable(skill_classifier)
        ):
            raise TypeError("skill_classifier must be a BaseSkillClassifier instance or a function")

        if not context:
            context = RAMAgentContext()

        self.__skill_classifier = skill_classifier
        self.context = context

    def __skill_classify(self, message: Any) -> List[Skill]:
        if isinstance(self.__skill_classifier, BaseSkillClassifier):
            return self.__skill_classifier.classify(message)

        if callable(self.__skill_classifier):
            return self.__skill_classifier(message)

    def conversation_with_user(self, user_id: str) -> Conversation:
        return Conversation(agent=self, user_id=user_id)

    def query(self, message: Any, user_id: str) -> List[Any]:
        user_context = self.context.get_user_context(user_id)

        if not user_context.skills:
            user_context.skills = self.__skill_classify(message)

        skills = user_context.skills[:]

        answers = []

        i = 0
        while i < len(skills):
            skill = skills[i]
            skill.global_context = user_context.params
            skill_result = skill.send(message)
            if not skill_result.relevant:
                skills = self.__skill_classify(message)
                if skills:
                    user_context.skills = skills
                    self.context.set_user_context(user_id, user_context)
                    return self.query(message, user_id)

            answers += skill_result.answers
            if not skill.finished:
                break

            user_context.skills.pop(0)
            i += 1

        self.context.set_user_context(user_id, user_context)

        return answers