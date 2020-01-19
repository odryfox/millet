from typing import Optional, List

from millet import Skill


def random_word(words: List[str]) -> Optional[str]:
    if words:
        return words[0]
    return None


def choice_next_word(vocabulary: List[str], history_words: List[str]) -> Optional[str]:
    if not history_words:
        return random_word(vocabulary)

    prev_word = history_words[-1]
    start_of_word = prev_word[-1]
    candidates_with_any_start = list(set(vocabulary) - set(history_words))
    candidates = list(filter(lambda word: word.startswith(start_of_word), candidates_with_any_start))

    return random_word(candidates)


def word_is_correct(word: str, vocabulary: List[str], history_words: List[str]) -> bool:
    return word not in vocabulary or word in history_words or word[0] != history_words[-1][-1]


class WordChainSkill(Skill):
    def __init__(self, vocabulary: List[str]):
        self.vocabulary = vocabulary
        self.history_words = list()
        super().__init__()

    def start(self, initial_message: str):
        self.say("Ok")
        self.my_move()

    def my_move(self):
        word = choice_next_word(self.vocabulary, self.history_words)
        if not word:
            self.finish("You are win!")
        self.history_words.append(word)
        self.ask(f"My word: {word}", direct_to=self.user_move)

    def user_move(self, user_word: str):
        if word_is_correct(user_word, self.vocabulary, self.history_words):
            self.abort("You are lose!")

        self.history_words.append(user_word)
        self.my_move()
