from typing import Callable, List, Tuple


class Agent:
    def __init__(self, skill_classifier: Callable[[str], List[Callable[[str], Tuple[List[str], int]]]]):
        if not callable(skill_classifier):
            raise TypeError('skill_classifier must be a function')

        self.__skill_classifier = skill_classifier
        self.__current_skill_state = None
        self.__current_skill = None

    def answer_me(self, message: str) -> List[str]:
        answers = []

        skills = self.__skill_classifier(message)
        if skills:
            self.__current_skill_state = 0
        else:
            if self.__current_skill:
                skills = [self.__current_skill]

        for skill in skills:
            skill_result = skill(message, self.__current_skill_state)
            self.__current_skill_state = skill_result[1]
            answers += skill_result[0]

            if self.__current_skill_state == 0:
                self.__current_skill_state = None
                self.__current_skill = None
            else:
                self.__current_skill = skill
                break

        return answers
