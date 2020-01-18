import pickle
from abc import ABC, abstractmethod
from typing import List, Any

from redis import Redis

from millet.skill import Skill


class UserContext:
    def __init__(self, params: dict, skills: List[Skill]):
        self.params = params
        self.skills = skills

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.params == other.params and self.skills == other.skills


class AgentContext(ABC):
    @property
    def empty_user_context(self) -> UserContext:
        return UserContext(params={}, skills=[])

    @abstractmethod
    def set_user_context(self, user_id: str, user_context: UserContext) -> None:
        pass

    @abstractmethod
    def get_user_context(self, user_id: str) -> UserContext:
        pass


class RAMAgentContext(AgentContext):
    def __init__(self):
        self.__storage = dict()

    def set_user_context(self, user_id: str, user_context: UserContext) -> None:
        self.__storage[user_id] = user_context

    def get_user_context(self, user_id: str) -> UserContext:
        return self.__storage.get(user_id, self.empty_user_context)


class PickleSerializer:
    def loads(self, serialized_param: str) -> Any:
        param = pickle.loads(serialized_param.encode())
        return param

    def dumps(self, param: Any) -> str:
        serialized_param = pickle.dumps(param, 0).decode()
        return serialized_param


class RedisAgentContext(AgentContext):
    def __init__(self, redis: Redis):
        self.redis = redis
        self.serializer = PickleSerializer()

    def __serialize_user_context(self, user_context: UserContext) -> str:
        return self.serializer.dumps(user_context)

    def __deserialize_user_context(self, serialized_user_context: str) -> UserContext:
        return self.serializer.loads(serialized_user_context)

    def set_user_context(self, user_id: str, user_context: UserContext) -> None:
        serialized_user_context = self.__serialize_user_context(user_context)
        self.redis.set(user_id, serialized_user_context)

    def get_user_context(self, user_id: str) -> UserContext:
        serialized_user_context = self.redis.get(user_id)
        if not serialized_user_context:
            return self.empty_user_context

        serialized_user_context = serialized_user_context.decode()
        user_context = self.__deserialize_user_context(serialized_user_context)
        return user_context
