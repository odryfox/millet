from redis import Redis

from millet.context import UserContext, RedisAgentContext, PickleSerializer, RAMAgentContext


def test_default_user_context(bob_id: str, redis: Redis):
    default_user_context = UserContext(params={}, skills=[])

    agent_context = RedisAgentContext(redis=redis)
    user_context = agent_context.get_user_context(bob_id)

    assert user_context == default_user_context


def test_reload_ram_context(bob_id: str, user_context: UserContext, redis: Redis):
    default_user_context = UserContext(params={}, skills=[])

    agent_context = RAMAgentContext()
    agent_context.set_user_context(bob_id, user_context)

    new_agent_context = RAMAgentContext()
    loaded_user_context = new_agent_context.get_user_context(bob_id)

    assert loaded_user_context == default_user_context


def test_pickle_reserialize(user_context: UserContext):
    serializer = PickleSerializer()
    serialized_user_context = serializer.dumps(user_context)
    serializer = PickleSerializer()
    deserailized_user_context = serializer.loads(serialized_user_context)

    assert deserailized_user_context == user_context


def test_reload_redis_context(bob_id: str, user_context: UserContext, redis: Redis):
    agent_context = RedisAgentContext(redis=redis)
    agent_context.set_user_context(bob_id, user_context)

    new_agent_context = RedisAgentContext(redis=redis)
    loaded_user_context = new_agent_context.get_user_context(bob_id)

    assert loaded_user_context.params == user_context.params
