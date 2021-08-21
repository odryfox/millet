import pickle
from abc import ABC, abstractmethod
from typing import Any, List, Optional, TypeVar

Redis = TypeVar('Redis')


class UserContext:

    def __init__(
        self,
        skill_names: List[str],
        state_names: List[Optional[str]],
        history: List[Any],
        context: dict,
        calls_history: dict,
    ) -> None:
        self.skill_names = skill_names
        self.state_names = state_names
        self.history = history
        self.context = context
        self.calls_history = calls_history

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, self.__class__)
            and other.skill_names == self.skill_names
            and other.state_names == self.state_names
            and other.history == self.history
            and other.context == self.context
            and other.calls_history == self.calls_history
        )


class BaseContextManager(ABC):

    @abstractmethod
    def set_user_context(self, user_id: str, user_context: UserContext) -> None:
        pass

    @abstractmethod
    def get_user_context(self, user_id: str) -> UserContext:
        pass

    @property
    def _empty_user_context(self) -> UserContext:
        return UserContext(skill_names=[], state_names=[], history=[], context={}, calls_history={})


class RAMContextManager(BaseContextManager):

    def __init__(self) -> None:
        self._storage = dict()

    def set_user_context(self, user_id: str, user_context: UserContext) -> None:
        self._storage[user_id] = user_context

    def get_user_context(self, user_id: str) -> UserContext:
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

    def _serialize_user_context(self, user_context: UserContext) -> str:
        return self._serializer.dumps(user_context)

    def _deserialize_user_context(self, serialized_user_context: str) -> UserContext:
        return self._serializer.loads(serialized_user_context)

    def set_user_context(self, user_id: str, user_context: UserContext) -> None:
        serialized_user_context = self._serialize_user_context(user_context)
        self._redis.set(user_id, serialized_user_context)

    def get_user_context(self, user_id: str) -> UserContext:
        serialized_user_context = self._redis.get(user_id)
        if not serialized_user_context:
            return self._empty_user_context

        serialized_user_context = serialized_user_context.decode()
        user_context = self._deserialize_user_context(serialized_user_context)
        return user_context
