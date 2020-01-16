from dialogus.skill import SkillResult, Skill


def test_eq():
    class EmptySkill(Skill):
        def start(self, initial_message: str):
            pass

    skill1 = EmptySkill()
    skill2 = EmptySkill()

    assert skill1 == skill2


def test_skill_result_repr():
    skill_result = SkillResult(answers=["Hi"], relevant=True)
    assert repr(skill_result) == "SkillResult(answers=['Hi'], relevant=True)"


def test_say():
    class EchoSkill(Skill):
        def start(self, initial_message: str):
            self.say(initial_message)

    skill = EchoSkill()
    assert skill.send("Hi") == SkillResult(answers=["Hi"], relevant=True) and skill.finished


def test_duplicate_message_say():
    class DuplicateEchoSkill(Skill):
        def start(self, initial_message: str):
            self.say(initial_message * 2)

    skill = DuplicateEchoSkill()
    assert skill.send("Hi") == SkillResult(answers=["HiHi"], relevant=True) and skill.finished


def test_multi_answers():
    class GreetingSkill(Skill):
        def start(self, initial_message: str):
            self.say("Hello")
            self.say("How are you?")

    skill = GreetingSkill()
    assert skill.send("Hi") == SkillResult(answers=["Hello", "How are you?"], relevant=True) and skill.finished


def test_stop_exception():
    class EchoSkill(Skill):
        def start(self, initial_message: str):
            self.say(initial_message)

    skill = EchoSkill()
    skill.send("Hi")
    try:
        skill.send("Hi")
        assert False, f"Expected {StopIteration.__name__}"
    except StopIteration:
        assert True


def test_ask():
    class AgeSkill(Skill):
        def start(self, initial_message: str):
            age = self.ask("How old are you?")
            self.say(f"You are {age} years old!")

    skill = AgeSkill()
    assert skill.send("Hi") == SkillResult(answers=["How old are you?"], relevant=True) and not skill.finished
    assert skill.send("42") == SkillResult(answers=["You are 42 years old!"], relevant=True) and skill.finished


def test_ask_with_direct_to():
    class AgeSkill(Skill):
        def start(self, initial_message: str):
            self.ask("How old are you?", direct_to=self.wait_age)

        def wait_age(self, age: str):
            self.say(f"You are {age} years old!")

    skill = AgeSkill()
    assert skill.send("Hi") == SkillResult(answers=["How old are you?"], relevant=True) and not skill.finished
    assert skill.send("42") == SkillResult(answers=["You are 42 years old!"], relevant=True) and skill.finished


def test_specify():
    class AgeSkill(Skill):
        def start(self, initial_message: str):
            age = self.ask("How old are you?")
            try:
                age = int(age)
            except:
                age = self.specify("Incorrect age. Repeat pls.")
            self.say(f"You are {age} years old!")

    skill = AgeSkill()
    assert skill.send("Hi") == SkillResult(answers=["How old are you?"], relevant=True) and not skill.finished
    assert skill.send("I don't know!") == SkillResult(answers=["Incorrect age. Repeat pls."], relevant=False) and not skill.finished
    assert skill.send("42") == SkillResult(answers=["You are 42 years old!"], relevant=True) and skill.finished


def test_specify_with_direct_to():
    class AgeSkill(Skill):
        def start(self, initial_message: str):
            self.ask("How old are you?", direct_to=self.waiting_age)

        def waiting_age(self, age: str):
            try:
                age = int(age)
            except:
                age = self.specify("Incorrect age. Repeat pls.")
            self.say(f"You are {age} years old!")

    skill = AgeSkill()
    assert skill.send("Hi") == SkillResult(answers=["How old are you?"], relevant=True) and not skill.finished
    assert skill.send("I don't know!") == SkillResult(answers=["Incorrect age. Repeat pls."], relevant=False) and not skill.finished
    assert skill.send("42") == SkillResult(answers=["You are 42 years old!"], relevant=True) and skill.finished
