from typing import List, Optional

from millet import BaseSkill


def _choice_next_word(vocabulary: List[str], history_words: List[str]) -> Optional[str]:
    for word in vocabulary:
        if word not in history_words:
            return word
    return None


def _word_is_correct(word: str, vocabulary: List[str], history_words: List[str]) -> bool:
    return word in vocabulary and word not in history_words and word[0] == history_words[-1][-1]


class WordChainSkill(BaseSkill):

    def __init__(self, vocabulary: List[str]):
        self.vocabulary = vocabulary
        self.history_words = list()

    def execute(self, initial_message: str):
        self.say('Lets start')
        self.my_move()

    def my_move(self):
        word = _choice_next_word(self.vocabulary, self.history_words)
        if not word:
            self.say('You are win!')
            return

        self.history_words.append(word)
        self.ask(f'My word: {word}', direct_to=self.user_move)

    def user_move(self, user_word: str):
        if not _word_is_correct(user_word, self.vocabulary, self.history_words):
            self.say('You are lose!')
            return

        self.history_words.append(user_word)
        self.my_move()
