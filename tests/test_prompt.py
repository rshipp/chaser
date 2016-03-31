import unittest
from chaser import prompt


class TestPrompt(unittest.TestCase):

    def test_yes_yes_case(self):
        prompt.user_input = lambda x: prompt.YES
        r = prompt.prompt("test")
        self.assertEquals(prompt.YES, r)

    def test_yes_no_case(self):
        prompt.user_input = lambda x: prompt.NO
        r = prompt.prompt("test")
        self.assertEquals(prompt.NO, r)

    def test_no_yes_case(self):
        prompt.user_input = lambda x: prompt.YES
        r = prompt.prompt("test", prompt.NO)
        self.assertEquals(prompt.YES, r)

    def test_no_no_case(self):
        prompt.user_input = lambda x: prompt.NO
        r = prompt.prompt("test", prompt.NO)
        self.assertEquals(prompt.NO, r)

    def test_correct_lower_upper(self):
        def user_input1(x):
            self.assertEquals(prompt.YES.upper(), x[6])
            self.assertEquals(prompt.NO.lower(), x[8])
            return prompt.YES
        prompt.user_input = user_input1
        r = prompt.prompt("")

        def user_input2(x):
            self.assertEquals(prompt.YES.lower(), x[6])
            self.assertEquals(prompt.NO.upper(), x[8])
            return prompt.YES
        prompt.user_input = user_input2
        r = prompt.prompt("", prompt.NO)
