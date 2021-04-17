from typing import List, Optional

from millet import BaseSkill


def _interpret_answer(answer_validation: dict, answer: str) -> [Optional[str], Optional[str]]:
    answer_type = answer_validation['type']

    if answer_type == 'variants':
        variants = answer_validation['variants']
        for variant_key, synonyms in variants.items():
            if answer in synonyms:
                return variant_key, None
        return None, 'Incorrect variant!'

    elif answer_type == 'interval':
        lower, upper = answer_validation['interval']
        try:
            answer_int = int(answer)
        except ValueError:
            return None, 'Expected number'
        if lower < answer_int < upper:
            return answer_int, None
        return None, 'Not in the interval!'

    elif answer_type == 'text':
        return answer, None


class QuizSkill(BaseSkill):

    def __init__(self, quiz: List[dict]):
        self.quiz = quiz
        self.current_question_number = 0
        self.answers = {}

    def start(self, initial_message: str):
        self.say('Lets go')
        self.ask_current_question()

    def ask_current_question(self):
        question_text = self.quiz[self.current_question_number]['question']
        self.ask(question=question_text, direct_to=self.waiting_answer)

    def waiting_answer(self, answer: str):
        question = self.quiz[self.current_question_number]
        answer_validation = question['answer_validation']
        clear_answer, error = _interpret_answer(answer_validation, answer)
        if error:
            self.specify(error, direct_to=self.waiting_answer)

        self.answers[question['id']] = clear_answer
        self.current_question_number += 1
        if self.current_question_number >= len(self.quiz):
            self.say('Thank you for your answers.')
            return
        self.ask_current_question()
