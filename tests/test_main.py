import unittest
import sys
from chaser import main


class TestMain(unittest.TestCase):

    def test_smoke_main(self):
        sys.argv = ["chaser"]
        main()
