from typing import List, Type

from dialogus import Skill, Agent
from dialogus.context import UserContext, Redis, RedisAgentContext, PickleSerializer


class AgeSkill(Skill):
    def run(self, message: str):
        age = self.ask('How old are you?')
        ...
        self.say('Ok')


def test_pickle_reserialize(user_context: UserContext):
    serializer = PickleSerializer()
    serialized_user_context = serializer.dumps(user_context)
    deserailized_user_context = serializer.loads(serialized_user_context)

    assert deserailized_user_context == user_context


def test_reload_context(user_context: UserContext, redis: Redis):
    agent_context = RedisAgentContext(redis=redis)
    agent_context.set_user_context('Bob', user_context)

    new_agent_context = RedisAgentContext(redis=redis)
    loaded_user_context = new_agent_context.get_user_context('Bob')

    assert user_context == loaded_user_context


def test_default_user_context(redis: Redis):
    default_user_context = UserContext(params={}, dialogs=[])

    agent_context = RedisAgentContext(redis=redis)
    user_context = agent_context.get_user_context('Bob')

    assert user_context == default_user_context


def test_persistent_context(redis: Redis):
    def skill_classifier(message: str) -> List[Type[Skill]]:
        skills = []

        if 'age' in message:
            skills.append(AgeSkill)

        return skills

    agent = Agent(skill_classifier=skill_classifier, context=RedisAgentContext(redis=redis))
    agent.query('What about age?', 'Bob')  # ['How old are you?']

    agent = Agent(skill_classifier=skill_classifier, context=RedisAgentContext(redis=redis))
    assert agent.query('42', 'Bob') == ['Ok']


def test_ram_context():
    def skill_classifier(message: str) -> List[Type[Skill]]:
        skills = []

        if 'age' in message:
            skills.append(AgeSkill)

        return skills

    agent = Agent(skill_classifier=skill_classifier)
    agent.query('What about age?', 'Bob')  # ['How old are you?']

    agent = Agent(skill_classifier=skill_classifier)
    assert agent.query('42', 'Bob') == []
    assert agent.query('What about age?', 'Bob') == ['How old are you?']
