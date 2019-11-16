from abc import ABC, abstractmethod
from typing import Callable, List


class Skill(ABC):
    def __init__(self):
        self.state = 0

    @abstractmethod
    def run(self, message: str) -> List[str]:
        pass


class Conversation:
    def __init__(self, agent: 'Agent', user_id: str):
        self.agent = agent
        self.user_id = user_id

    def query(self, message: str) -> List[str]:
        return self.agent.query(message, self.user_id)


class Agent:
    def __init__(self, skill_classifier: Callable[[str], List[Skill]]):
        if not callable(skill_classifier):
            raise TypeError('skill_classifier must be a function')

        self.__skill_classifier = skill_classifier
        self.__context = dict()

    def conversation_with_user(self, user_id: str) -> Conversation:
        return Conversation(agent=self, user_id=user_id)

    def __load_user_context(self, user_id: str) -> dict:
        user_context = self.__context.get(user_id, dict(current_skill_state=None, current_skill=None))
        return user_context

    def __save_user_context(self, user_id: str, user_context: dict):
        self.__context[user_id] = user_context

    def query(self, message: str, user_id: str) -> List[str]:
        user_context = self.__load_user_context(user_id)
        current_skill = user_context['current_skill']

        skills = self.__skill_classifier(message)
        if not skills and current_skill:
            skills = [current_skill]

        answers = []

        for skill in skills:
            answers += skill.run(message)
            current_skill_state = skill.state

            if current_skill_state == 0:
                current_skill = None
            else:
                current_skill = skill
                break

        user_context['current_skill'] = current_skill
        self.__save_user_context(user_id, user_context)

        return answers
