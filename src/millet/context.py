import pickle
from abc import ABC, abstractmethod
from typing import Any, TypeVar

Redis = TypeVar('Redis')


# UserContext is dict for best compatibility
# skill_names: List[str]
# state_names: List[Optional[str]]
# history: List[Any]
# context: dict
# calls_history: dict
# timeout_uid: Optional[str]


class BaseContextManager(ABC):

    @abstractmethod
    def set_user_context(self, user_id: str, user_context: dict) -> None:
        pass

    @abstractmethod
    def get_user_context(self, user_id: str) -> dict:
        pass

    @property
    def _empty_user_context(self) -> dict:
        return dict(
            skill_names=[],
            state_names=[],
            history=[],
            context={},
            calls_history={},
            timeout_uid=None,
        )


class RAMContextManager(BaseContextManager):

    def __init__(self) -> None:
        self._storage = dict()

    def set_user_context(self, user_id: str, user_context: dict) -> None:
        self._storage[user_id] = user_context

    def get_user_context(self, user_id: str) -> dict:
        return self._storage.get(user_id, self._empty_user_context)


class PickleSerializer:

    def loads(self, serialized_param: str) -> Any:
        param = pickle.loads(serialized_param.encode())
        return param

    def dumps(self, param: Any) -> str:
        serialized_param = pickle.dumps(param, 0).decode()
        return serialized_param


class RedisContextManager(BaseContextManager):

    def __init__(self, redis: Redis):
        self._redis = redis
        self._serializer = PickleSerializer()

    def _serialize_user_context(self, user_context: dict) -> str:
        return self._serializer.dumps(user_context)

    def _deserialize_user_context(self, serialized_user_context: str) -> dict:
        return self._serializer.loads(serialized_user_context)

    def set_user_context(self, user_id: str, user_context: dict) -> None:
        serialized_user_context = self._serialize_user_context(user_context)
        self._redis.set(user_id, serialized_user_context)

    def get_user_context(self, user_id: str) -> dict:
        serialized_user_context = self._redis.get(user_id)
        if not serialized_user_context:
            return self._empty_user_context

        serialized_user_context = serialized_user_context.decode()
        user_context = self._deserialize_user_context(serialized_user_context)
        return user_context
