import pytest
from redis import Redis


@pytest.fixture
def redis() -> Redis:
    redis = Redis()
    redis.flushdb()
    yield redis
    redis.flushdb()
