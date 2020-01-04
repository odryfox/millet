from abc import ABC, abstractmethod
from typing import Callable, List, Optional


class InputMessageSignal(Exception):
    def __init__(self, message: str, key: str) -> None:
        self.message = message
        self.key = key


class OutputMessageSignal(Exception):
    def __init__(self, message: str, key: str) -> None:
        self.message = message
        self.key = key


class Skill(ABC):
    def __init__(self) -> None:
        self.__context = dict()

    def set_context(self, context: dict) -> None:
        self.__context = context

    def ask(self, message: str, key: Optional[str] = None) -> str:
        key = key or message
        answer = self.__context.get(key)
        if answer:
            return answer
        raise InputMessageSignal(message, key)

    def say(self, message: str, key: Optional[str] = None) -> None:
        key = key or message
        question = self.__context.get(key)
        if question:
            return
        raise OutputMessageSignal(message, key)

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
        user_context = self.__context.get(user_id, dict(current_skill_state=0, current_skill=None))
        return user_context

    def __save_user_context(self, user_id: str, user_context: dict):
        self.__context[user_id] = user_context

    def query(self, message: str, user_id: str) -> List[str]:
        user_context = self.__load_user_context(user_id)

        current_skill = None

        waiting_key = user_context.get('waiting_key')
        if waiting_key:
            user_context[waiting_key] = message
            user_context['waiting_key'] = None

        skills = self.__skill_classifier(message)
        if not skills:
            current_skill = user_context['current_skill']

            if current_skill:
                skills = [current_skill]

        answers = []

        i = 0
        while i < len(skills):
            skill = skills[i]
            skill.set_context(user_context)
            try:
                skill.run(message)
                user_context = dict()
                i += 1
            except InputMessageSignal as ims:
                user_context['waiting_key'] = ims.key
                answers.append(ims.message)
                current_skill = skill
                break
            except OutputMessageSignal as oms:
                user_context[oms.message] = oms.message
                answers.append(oms.message)

        user_context['current_skill'] = current_skill
        self.__save_user_context(user_id, user_context)

        return answers
