## Millet

**Millet** - библиотека для создания диалоговых агентов.

### Вам может быть полезна библиотека, если 

- Вы пишите асинхронных текстовых ботов, со сложной ветвистой логикой (например виртуального ассистента для поиска дешевых авиабилетов).

Millet позволит описывать логику таких ботов очень просто, как если бы это был синхронный диалог с пользователем на input-print.

Только сравните скилл на input-print:

```python
def meeting_skill(message: str):
    name = input("What is your name?")
    print(f"Nice to meet you {name}!")
```

и этот же скилл в Millet:

```python
from millet import BaseSkill

class MeetingSkill(BaseSkill):
    def execute(self, initial_message: str):
        name = self.ask(question='What is your name?')
        self.say(f'Nice to meet you {name}!')
```

если бы вы описывали даже такой простой диалог для асинхронного бота своими силами, то вам бы пришлось использовать state-машину
где-то хранить текущее состояние ожидания имени пользователя. С увеличением сложности диалога количество состояний будет только расти, как и головная боль в их поддержке.

- вы пишите бота, который работает с различными каналами связи (telegram, viber, vk, почта и тд.)

Концептуально логика формирования ответа пользователю не должна зависеть от инфраструктурных каналов передачи сообщений. 
Millet позволяет разделить эти слои и предоставляет готовые и понятные абстракции для описания ваших агентов.

Продал? Тогда погнали.

### Установка

```bash
pip install Millet
```

### Сходу простой пример

Возможно вы гений и поймете концепцию, просто посмотрев на пример.

Опишем агента, который умеет знакомиться:
```python
from typing import Dict, List
from millet import Agent, BaseSkill, BaseSkillClassifier


class MeetingSkill(BaseSkill):
    def execute(self, initial_message: str):
        name = self.ask(question='What is your name?')
        self.say(f'Nice to meet you {name}!')


class SkillClassifier(BaseSkillClassifier):
    @property
    def skills_map(self) -> Dict[str, BaseSkill]:
        return {
            'meeting': MeetingSkill(),
        }

    def classify(self, message: str) -> List[str]:
        return ['meeting']


skill_classifier = SkillClassifier()
agent = Agent(skill_classifier=skill_classifier)
conversation = agent.conversation_with_user('100500')
```

использование:
```shell
>>> conversation.query('Hello')
['What is your name?']
>>> conversation.query('Bob')
['Nice to meet you Bob!']
```

всем остальным рекомендуется продолжить чтение документации.

### Для начала познакомимся с основными понятиями:

**Агент** - это ваш виртуальный ассистент, в который пользователи могут слать запросы, а он будет формировать ответы.

**Скилл** - это умение вашего агента. Хотите научить его играть в города? Просто опишите скилл игры в города и подключите его к вашему агенту. Вот так вот просто.

**Пользователь** - какой-то человек, желающий воспользоваться скиллом вашего агента.

**Диалог** - это процесс использования пользователем скилла агента. Диалог подразумевает, что какой-то пользователь находится в каком-то состоянии использования скилла агента.

**Классификатор скиллов** - механизм определения каким скиллом хочет воспользоваться пользователь на основании его запроса. Библиотека дает возможность описать свой классификатор - это может быть сложная ML-модель либо старые добрые if-else.

**Релевантность** - иногда пользователь не хочет доводить до цели текущий скилл. Он может захотеть воспользоваться другим скиллом или просто закончить текущий. Релевантность определяет уместно ли текущее сообщение пользователя к текущему скиллу. Возможно это сообщение не очень уместно и стоит переключить скилл классификатором.


### Описание скиллов
Для создания своего скилла необходимо реализовать класс BaseSkill.

```python
from millet import BaseSkill

class MeetingSkill(BaseSkill):
    def execute(self, initial_message: str):
        name = self.ask(question='What is your name?')
        self.say(f'Nice to meet you {name}!')
```

По умолчанию точкой входа является состояние initial_state_name='execute', но вы можете задать любое.

```python
from millet import BaseSkill

class MeetingSkill(BaseSkill):
    
    initial_state_name = 'meet'
    
    def meet(self, initial_message: str):
        name = self.ask(question='What is your name?')
        self.say(f'Nice to meet you {name}!')
```

В рамках скилла доступна ссылка на `user_id`.

Для того чтобы запросить какие-то уточнения от клиента в ходе выполнения скилла имеется ряд методов:

`say` - просто вывести ответ пользователю, управление пользователю не передается

---
`ask` - что-то спросить у пользователя, управление перейдет пользователю, когда от него будет получен ответ - скрипт продолжит свое выполнение с этого же места, метод вернет ответ пользователя

---
`specify` - то же самое что и ask, но произойдет вызов классификатора (необходимо применять этот метод когда вы не уверены, что ответ релевантен для текущего скилла и есть шанс что это запрос на начала другого скилла)


### direct_to
Иногда сложно уместить весь диалог в одно состояние или важно чтобы логика скрипта выполнялась ровно один раз (покупка чего-либо)
В таких случаях в методах с передачей управления пользователю предусмотрен параметр direct_to, в который нужно передать следующее состояние диалога
Состояние диалога - метод скила (по аналогии с методом execute). Можно передать сам метод или его название.

```python
from millet import BaseSkill


class AgeSkillWithDirectTo(BaseSkill):
    def execute(self, message: str):
        age = self.ask('How old are you?')
        self.wait_age(age)

    def wait_age(self, age: str):
        try:
            age = int(age)
        except ValueError:
            self.specify(question='Send a number pls', direct_to='wait_age')

        self.say(f'You are {age} years old')
```


### Контекст скилла 
Представляет собой горстку параметров в виде dict, которая доступна в рамках выполнения текущего скилла.
Необходима для передачи некоторых параметров в соседнее состояние скилла.

```python
from millet import BaseSkill


class SkillWithContext(BaseSkill):
    def execute(self, message: str):
        name = self.ask(question='What is your name?')
        self.context['name'] = name
        self.say(f'Nice to meet you {name}!')
        age = self.ask(f'{name}, how old are you?')
        self.wait_age(age)

    def wait_age(self, age: str):
        name = self.context['name']
        try:
            age = int(age)
        except ValueError:
            self.specify(question=f'{name}, send a number pls', direct_to='wait_age')

        self.say(f'You are {age} years old')
```


### Контекст агента

Сохранение контекста необходимо для хранения текущего состояния диалога с пользователем.
Из коробки поставляются следующие менеджеры контексты:

- RAMContextManager - хранение диалога в оперативной памяти, очищается при удалении экземпляра менеджера из памяти
- RedisContextManager - персистентное хранение диалога в Redis, не сбрасывается между передеплоями

Вы можете определить свой механизм хранения контекста реализовав абстрактный класс BaseContextManager. Например если вам нужно хранить контекст в postgres.


### Продвинутое использование
Для написания скилов полностью в синхронном стиле можно использовать определение side-функций.
Библиотека сделает всю магию за вас.

```python
from millet import BaseSkill
import random


class NumberSkill(BaseSkill):

    side_functions = [
        'random.randint',
    ]

    def execute(self, message: str):
        number_expected = random.randint(0, 100)  # side function
        number_actual = int(self.ask('Whats number?'))
        if number_actual == number_expected:
            self.say('ok')
        else:
            self.say('wrong')
```

В данном примере randint - side-функция, которая может вернуть разные значения при одинаковых входных данных.
Для описания side-методов можно использовать side_methods. 

```python
from millet import BaseSkill
import random


class Rand:
    def rand(self):
        return random.randint(0, 100)

class NumberSkill(BaseSkill):

    side_methods = [
        (Rand, 'rand'),
    ]

    def execute(self, message: str):
        number_expected = Rand().rand()  # side method
        number_actual = int(self.ask('Whats number?'))
        if number_actual == number_expected:
            self.say('ok')
        else:
            self.say('wrong')
```

Если метод текущего скила, то просто напишите его имя.

```python
from millet import BaseSkill
import random


class NumberSkill(BaseSkill):

    side_methods = [
        ('NumberSkill', 'rand'),
    ]

    def execute(self, message: str):
        number_expected = self.rand()  # side self-method
        number_actual = int(self.ask('Whats number?'))
        if number_actual == number_expected:
            self.say('ok')
        else:
            self.say('wrong')

    def rand(self):
        return random.randint(0, 100)
```

Рекомендация: при сохранении в контекст, передаче сообщений и использовании side_functions/side_methods используйте простые структуры данных (str, int, bool, dict, ...). Это облегчит мигрирование кода скилов без возникновения проблем у активных диалогов. Также альтернативой может быть подход написания новых скилов, а не изменение существующих.


### Примеры использования
https://github.com/odryfox/galangal - бот для изучения иностранных слов
https://github.com/radostkali/arena-battle-tg-bot - бот Сидорович

Другие примеры использования вы можете найти в здесь
https://github.com/odryfox/millet/tree/master/examples
