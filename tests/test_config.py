import unittest
from chaser import config


class TestConfig(unittest.TestCase):

    def test_smoke_default_config(self):
        r = config.get('BuildDir')
        self.assertEquals("~/ccr", r)
