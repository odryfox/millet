from abc import abstractmethod, ABC
from typing import Optional, Callable, Any


class InputMessageSignal(Exception):
    def __init__(self, message: str, key: str, is_should_reweigh_skills: bool = False) -> None:
        self.message = message
        self.key = key
        self.is_should_reweigh_skills = is_should_reweigh_skills


class OutputMessageSignal(Exception):
    def __init__(self, message: str, key: str) -> None:
        self.message = message
        self.key = key


class Skill(ABC):
    def __init__(self, *, global_context: dict, skill_context: dict) -> None:
        self.global_context = global_context
        self.__skill_context = skill_context

    def ask(self, message: str, key: Optional[str] = None) -> str:
        key = key or message
        answer = self.__skill_context.get(key)
        if answer:
            return answer
        raise InputMessageSignal(message, key)

    def specify(self, message: str, key: str) -> None:
        raise InputMessageSignal(message, key, True)

    def say(self, message: str, key: Optional[str] = None) -> None:
        key = key or message
        question = self.__skill_context.get(key)
        if question:
            return
        raise OutputMessageSignal(message, key)

    def get_or_call(self, function: Callable, *args, **kwargs) -> Any:
        key = f"{function.__name__}{args}{kwargs}"
        result = self.__skill_context.get(key)
        if result:
            return result
        result = function(*args, **kwargs)
        self.__skill_context[key] = result
        return result

    @abstractmethod
    def run(self, message: str) -> None:
        pass


def get_or_call(method: Callable) -> Callable:
    from functools import wraps

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        return self.get_or_call(method, *((self, ) + args), **kwargs)

    return wrapper
