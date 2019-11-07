from typing import Callable, List, Tuple


class Agent:
    def __init__(self, skill_classifier: Callable[[str], List[Callable[[str], Tuple[List[str], int]]]]):
        if not callable(skill_classifier):
            raise TypeError('skill_classifier must be a function')

        self.__skill_classifier = skill_classifier
        self.__state = 0
        self.__current_skill = None

    def answer_me(self, message: str) -> List[str]:
        answers = []

        skills = self.__skill_classifier(message)
        if not skills and self.__current_skill:
            skills.append(self.__current_skill)

        for skill in skills:
            skill_result = skill(message, self.__state)
            self.__state = skill_result[1]
            answers += skill_result[0]

            if self.__state == 0:
                self.__current_skill = None
            else:
                self.__current_skill = skill
                break

        return answers
