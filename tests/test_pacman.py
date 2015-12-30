import unittest
from unittest import mock
import subprocess
from chaser import pacman


class TestPacman(unittest.TestCase):

    def test_exists_true(self):
        subprocess.check_output = lambda x, **_: "test"
        self.assertEquals("test", pacman.exists("test"))

    def test_exists_false(self):
        subprocess.check_output = mock.Mock(
                side_effect=subprocess.CalledProcessError(1, None))
        self.assertEquals(False, pacman.exists("test"))

    def test_is_installed(self):
        subprocess.call = lambda x, **_: 0
        self.assertEquals(True, pacman.is_installed("test"))

    def test_not_installed(self):
        subprocess.call = lambda x, **_: 1
        self.assertEquals(False, pacman.is_installed("test"))
        subprocess.call = lambda x, **_: 0

        pacman.exists = lambda x: False
        self.assertEquals(False, pacman.is_installed("test"))
