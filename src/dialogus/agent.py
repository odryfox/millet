from typing import Callable, List


class Agent:
    def __init__(self, skill_classifier: Callable[[str], List[Callable[[str], List[str]]]]):
        if not callable(skill_classifier):
            raise TypeError('skill_classifier must be a function')

        self.__skill_classifier = skill_classifier

    def answer_me(self, message: str) -> List[str]:
        answers = []
        skills = self.__skill_classifier(message)

        for skill in skills:
            answers += skill(message)

        return answers
