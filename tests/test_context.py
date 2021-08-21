import pytest
from redis import Redis

from millet.context import (
    PickleSerializer,
    RAMContextManager,
    RedisContextManager,
    UserContext
)

_empty_user_context = UserContext(
    skill_names=[],
    state_names=[],
    history=[],
    context={},
    calls_history={},
)


class TestRAMContextManager:

    def setup_method(self):
        self.context_manager = RAMContextManager()

    def test_get_user_context__user_context_doesnt_exist(self):
        other_user_context = UserContext(
            skill_names=['GreetingSkill', 'BuySkill'],
            state_names=[None, 'payment'],
            history=['hello, i want to buy iPhone'],
            context={'age': '25'},
            calls_history={},
        )
        self.context_manager.set_user_context('Alice', other_user_context)

        actual_user_context = self.context_manager.get_user_context('Bob')

        assert actual_user_context == _empty_user_context

    def test_reload_user_context__context_manager_in_ram(self):
        user_context = UserContext(
            skill_names=['GreetingSkill', 'BuySkill'],
            state_names=[None, 'payment'],
            history=['hello, i want to buy iPhone'],
            context={'age': '25'},
            calls_history={},
        )
        self.context_manager.set_user_context('Bob', user_context)

        reloaded_user_context = self.context_manager.get_user_context('Bob')

        assert reloaded_user_context == user_context

    def test_reload_user_context__context_manager_was_erased_from_ram(self):
        user_context = UserContext(
            skill_names=['GreetingSkill', 'BuySkill'],
            state_names=[None, 'payment'],
            history=['hello, i want to buy iPhone'],
            context={'age': '25'},
            calls_history={},
        )
        self.context_manager.set_user_context('Bob', user_context)

        context_manager = RAMContextManager()
        reloaded_user_context = context_manager.get_user_context('Bob')

        assert reloaded_user_context == _empty_user_context


class TestPickleSerializer:

    def test_reload(self):
        user_context = UserContext(
            skill_names=['GreetingSkill', 'BuySkill'],
            state_names=[None, 'payment'],
            history=['hello, i want to buy iPhone'],
            context={},
            calls_history={},
        )
        serializer = PickleSerializer()
        serialized_user_context = serializer.dumps(user_context)

        serializer = PickleSerializer()
        reloaded_user_context = serializer.loads(serialized_user_context)

        assert reloaded_user_context == user_context


class TestRedisContextManager:

    @pytest.fixture(autouse=True)
    def setup_method_fixture(self, redis: Redis):
        self.redis = redis
        self.context_manager = RedisContextManager(redis=redis)

    def test_get_user_context__user_context_doesnt_exist(self):
        other_user_context = UserContext(
            skill_names=['GreetingSkill', 'BuySkill'],
            state_names=[None, 'payment'],
            history=['hello, i want to buy iPhone'],
            context={'age': '25'},
            calls_history={},
        )
        self.context_manager.set_user_context('Alice', other_user_context)

        actual_user_context = self.context_manager.get_user_context('Bob')

        assert actual_user_context == _empty_user_context

    def test_reload_user_context__context_manager_in_ram(self):
        user_context = UserContext(
            skill_names=['GreetingSkill', 'BuySkill'],
            state_names=[None, 'payment'],
            history=['hello, i want to buy iPhone'],
            context={'age': '25'},
            calls_history={},
        )
        self.context_manager.set_user_context('Bob', user_context)

        reloaded_user_context = self.context_manager.get_user_context('Bob')

        assert reloaded_user_context == user_context

    def test_reload_user_context__context_manager_was_erased_from_ram(self):
        user_context = UserContext(
            skill_names=['GreetingSkill', 'BuySkill'],
            state_names=[None, 'payment'],
            history=['hello, i want to buy iPhone'],
            context={'age': '25'},
            calls_history={},
        )
        self.context_manager.set_user_context('Bob', user_context)

        context_manager = RedisContextManager(redis=self.redis)
        reloaded_user_context = context_manager.get_user_context('Bob')

        assert reloaded_user_context == user_context
