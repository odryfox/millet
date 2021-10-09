import uuid
from abc import ABC, abstractmethod


class MessageTimeOutException(Exception):
    pass


class MessageTimeOut:
    pass


class BaseTimeoutsBroker(ABC):

    def generate_timeout_uid(self, user_id: str, timeout: int) -> str:
        return str(uuid.uuid4())

    @abstractmethod
    def execute(self, user_id: str, timeout: int, timeout_uid: str):
        pass
