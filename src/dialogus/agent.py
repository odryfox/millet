from typing import Callable, List, Tuple


class Agent:
    def __init__(self, skill_classifier: Callable[[str], List[Callable[[str], Tuple[List[str], int]]]]):
        if not callable(skill_classifier):
            raise TypeError('skill_classifier must be a function')

        self.__skill_classifier = skill_classifier
        self.__context = dict()

    def __load_user_context(self, user_id: str) -> dict:
        user_context = self.__context.get(user_id, dict(current_skill_state=None, current_skill=None))
        return user_context

    def __save_user_context(self, user_id: str, user_context: dict):
        self.__context[user_id] = user_context

    def answer_me(self, message: str, user_id: str) -> List[str]:
        user_context = self.__load_user_context(user_id)

        current_skill_state = user_context['current_skill_state']
        current_skill = user_context['current_skill']

        answers = []

        skills = self.__skill_classifier(message)
        if skills:
            current_skill_state = 0
        else:
            if current_skill:
                skills = [current_skill]

        for skill in skills:
            skill_result = skill(message, current_skill_state)
            current_skill_state = skill_result[1]
            answers += skill_result[0]

            if current_skill_state == 0:
                current_skill_state = None
                current_skill = None
            else:
                current_skill = skill
                break

        user_context['current_skill_state'] = current_skill_state
        user_context['current_skill'] = current_skill

        self.__save_user_context(user_id, user_context)

        return answers
