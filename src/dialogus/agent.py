from typing import Callable, List, Type, Optional

from dialogus.context import AgentContext, UserContext, DialogContext, RAMAgentContext
from dialogus.skill import Skill, OutputMessageSignal, InputMessageSignal


class Conversation:
    def __init__(self, agent: 'Agent', user_id: str):
        self.agent = agent
        self.user_id = user_id

    def query(self, message: str) -> List[str]:
        return self.agent.query(message, self.user_id)


class Agent:
    def __init__(self, skill_classifier: Callable[[str], List[Type[Skill]]], context: Optional[AgentContext] = None):
        if not callable(skill_classifier):
            raise TypeError('skill_classifier must be a function')

        if not context:
            context = RAMAgentContext()

        self.__skill_classifier = skill_classifier
        self.context = context

    def conversation_with_user(self, user_id: str) -> Conversation:
        return Conversation(agent=self, user_id=user_id)

    def query(self, message: str, user_id: str) -> List[str]:
        user_context = self.context.get_user_context(user_id)

        if not user_context.dialogs:
            skill_classes = self.__skill_classifier(message)
            user_context.dialogs = [DialogContext(skill_class=skill_class, params={'initial_message': message}) for skill_class in skill_classes]

        dialogs = user_context.dialogs

        if dialogs:
            waiting_key = dialogs[0].params.get('waiting_key')
            if waiting_key:
                dialogs[0].params[waiting_key] = message
                dialogs[0].params['waiting_key'] = None

        answers = []

        i = 0
        while i < len(dialogs):
            dialog = dialogs[i]
            skill = dialog.skill_class(dialog.params)
            try:
                initial_message = dialog.params['initial_message']
                skill.run(initial_message)
                user_context = UserContext(dialogs=[], params={})
                i += 1
            except InputMessageSignal as ims:
                dialog.params['waiting_key'] = ims.key
                answers.append(ims.message)
                break
            except OutputMessageSignal as oms:
                dialog.params[oms.message] = oms.message
                answers.append(oms.message)

        self.context.set_user_context(user_id, user_context)

        return answers
