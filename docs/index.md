# Welcome to Millet

## Installing

```bash
pip install Millet
```

## A Simple Example

```python
from typing import List
from millet import Agent, Skill

class MeetingSkill(Skill):
    def start(self, initial_message: str):
        name = self.ask(question="What is your name?")
        self.say(f"Nice to meet you {name}!")

def skill_classifier(message: str) -> List[Skill]:
    return [MeetingSkill()]

agent = Agent(skill_classifier=skill_classifier)
conversation = agent.conversation_with_user("Bob")
```

```bash
>>> conversation.query("Hello")
["What is your name?"]
>>> conversation.query("Bob")
["Nice to meet you Bob!"]
```
