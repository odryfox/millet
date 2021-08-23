import builtins
import sys
from copy import deepcopy
from typing import Any, List, Optional, Tuple
from unittest import mock

from millet.context import BaseContextManager, RAMContextManager, UserContext
from millet.skill import BaseSkill, BaseSkillClassifier


class Conversation:

    def __init__(self, agent: 'Agent', user_id: str) -> None:
        self.agent = agent
        self.user_id = user_id

    def query(self, message: Any) -> List[Any]:
        return self.agent.query(message=message, user_id=self.user_id)


class Agent:

    def __init__(
        self,
        skill_classifier: BaseSkillClassifier,
        context_manager: Optional[BaseContextManager] = RAMContextManager(),
    ) -> None:

        self._skill_classifier = skill_classifier
        self._context_manager = context_manager

    def conversation_with_user(self, user_id: str) -> Conversation:
        return Conversation(agent=self, user_id=user_id)

    def query(self, message: Any, user_id: str) -> List[Any]:
        user_context = self._context_manager.get_user_context(user_id)

        answers, new_user_context = self._query(message, user_context)

        self._context_manager.set_user_context(user_id, new_user_context)
        return answers

    def _query(
        self,
        message: Any,
        user_context: UserContext,
    ) -> Tuple[List[Any], UserContext]:
        history = user_context.history

        if user_context.skill_names:
            skill_names = user_context.skill_names
            state_names = user_context.state_names

            context = user_context.context

            calls_history_global = deepcopy(user_context.calls_history)
            calls_history = deepcopy(user_context.calls_history)
        else:
            skill_names = self._skill_classifier.classify(message)
            state_names = [None for _ in skill_names]

            context = {}

            calls_history_global = {}
            calls_history = {}

        answers = []

        new_skill_names = []
        new_state_names = []
        new_history = []
        new_context = {}
        calls_new = {}

        for skill_name, state_name in zip(skill_names, state_names):
            skill: BaseSkill = self._skill_classifier.skills_map[skill_name]

            calls_current = {}

            def cached_decorator_func(func):
                def cached_func(*args, **kwargs):
                    if isinstance(func, mock.MagicMock):
                        func_name = str(func)
                    else:
                        func_name = func.__name__

                    if func_name in calls_history and calls_history[func_name]:
                        value = calls_history[func_name].pop(0)
                        return value

                    if isinstance(getattr(func, '__self__', None), type):
                        # it's cls method
                        args = args[1:]

                    result = func(*args, **kwargs)

                    if func_name not in calls_current:
                        calls_current[func_name] = []
                    calls_current[func_name].append(result)

                    return result

                return cached_func

            cached_decorators = []

            for side_func_name in skill.side_functions:
                if str(side_func_name) in {'print', '<built-in function print>'}:
                    side_func_name = 'print'
                    side_func = builtins.print
                else:
                    side_func_path_parts = side_func_name.split('.')
                    current_module = sys.modules[skill.__module__]

                    for side_func_path_part in side_func_path_parts:
                        current_module = current_module.__dict__[side_func_path_part]

                    side_func = current_module

                side_func_full_path = '.'.join([skill.__module__, side_func_name])
                decorator = mock.patch(
                    target=side_func_full_path,
                    new=cached_decorator_func(side_func),
                )
                cached_decorators.append(decorator)

            for side_class, side_method_name in skill.side_methods:
                if isinstance(side_class, str):
                    if side_class == skill.__class__.__name__:
                        side_class = skill.__class__
                    else:
                        side_class_parts = side_class.split('.')

                        if side_class_parts[0] == 'self':
                            side_class_parts = side_class_parts[1:]
                            side_class = skill

                            for side_class_part in side_class_parts:
                                side_class = getattr(side_class, side_class_part)

                side_method = getattr(side_class, side_method_name)
                decorator = mock.patch.object(
                    target=side_class,
                    attribute=side_method_name,
                    new=cached_decorator_func(side_method),
                )
                cached_decorators.append(decorator)

            def execute_skill(*args):
                skill_result = skill.execute(
                    message=message,
                    history=deepcopy(history),
                    state_name=state_name,
                    context=context,
                )
                return skill_result

            for dec in cached_decorators:
                execute_skill = dec(execute_skill)

            skill_result = execute_skill()

            if not skill_result.is_relevant:
                actual_skill_names = self._skill_classifier.classify(message)
                if actual_skill_names:
                    actual_state_names = [None for _ in actual_skill_names]
                    return self._query(
                        message=message,
                        user_context=UserContext(
                            skill_names=actual_skill_names,
                            state_names=actual_state_names,
                            history=[],
                            context={},
                            calls_history={},
                        )
                    )

            answers.extend(skill_result.answers)

            if not skill_result.is_finished:
                new_skill_names = [skill_name]
                new_state_names = [skill_result.direct_to]

                if skill_result.direct_to:
                    new_history = []
                    calls_new = []
                else:
                    new_history = history + [message]

                    calls_new = calls_history_global
                    for func_name in calls_current:
                        if func_name not in calls_new:
                            calls_new[func_name] = []
                        calls_new[func_name].extend(calls_current[func_name])

                new_context = skill_result.context

                break

            context = {}
            history = []

            calls_history_global = {}
            calls_history = {}

        new_user_context = UserContext(
            skill_names=new_skill_names,
            state_names=new_state_names,
            history=new_history,
            context=new_context,
            calls_history=calls_new,
        )
        return answers, new_user_context
