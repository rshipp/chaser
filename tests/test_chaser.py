import unittest
import subprocess
import os
import tempfile

from chaser import chaser, pacman, prompt
import ccr

class TestChaser(unittest.TestCase):

    def test_get_source_files(self):
        with tempfile.TemporaryDirectory() as d:
            chaser.get_source_files('aur2ccr', d)
            self.assertTrue(os.path.isfile(os.path.join(d, 'aur2ccr', 'PKGBUILD')))

    """
    # Old broken test
    def test_recurse_depends(self):
        old = (chaser.BUILD_DIR, pacman.is_installed, pacman.exists)
        with tempfile.TemporaryDirectory() as d:
            chaser.BUILD_DIR = d
            pacman.is_installed = lambda x: False
            pacman.exists = lambda x: False if x in ["abs", "aur2ccr"] else True
            expected = {
                'abs': set(['bash', 'rsync']),
                'aur2ccr': set([
                    'abs',
                    'bash',
                    'ccr',
                    'curl',
                    'gawk',
                    'jshon',
                    'pacman',
                    'python2',
                    'sed'
                ]),
                'bash': set(),
                'ccr': set(),
                'curl': set(),
                'gawk': set(),
                'jshon': set(),
                'pacman': set(),
                'python2': set(),
                'rsync': set(),
                'sed': set()
            }
            self.assertEquals(expected, chaser.recurse_depends('aur2ccr'))
            pacman.is_installed = lambda x: True
            self.assertEquals({'aur2ccr': set()}, chaser.recurse_depends('aur2ccr'))
        chaser.BUILD_DIR, pacman.is_installed, pacman.exists = old
    """

    def test_dependency_chain(self):
        old = chaser.recurse_depends
        graph = {
            'a': set(['b']),
            'b': set(['c']),
            'c': set(),
            'd': set(['a', 'b']),
        }
        chaser.recurse_depends = lambda x, y: graph
        self.assertEquals(['c', 'b', 'a', 'd'], chaser.dependency_chain('d'))
        chaser.recurse_depends = old

    def test_smoke_install(self):
        old = (chaser.dependency_chain, chaser.get_source_files,
                prompt.prompt, subprocess.call, os.chdir, os.path.isfile)
        chaser.dependency_chain = lambda x, y: [x]
        chaser.get_source_files = lambda x, y: None
        prompt.prompt = lambda x: prompt.YES
        subprocess.call = lambda x: None
        os.chdir = lambda x: None
        os.path.isfile = lambda x: True

        chaser.install("test")

        chaser.dependency_chain, chaser.get_source_files, prompt.prompt, subprocess.call, os.chdir, os.path.isfile = old

    def test_check_updates(self):
        old = (pacman.list_unofficial, ccr.info)
        pacman.list_unofficial = lambda: [('test', '1-1')]
        # Lower ver, lower rel
        ccr.info = lambda x: {'Name': 'test', 'Version': '0-0'}
        self.assertEquals([], chaser.check_updates(None))
        # Lower ver, same rel
        ccr.info = lambda x: {'Name': 'test', 'Version': '0-1'}
        self.assertEquals([], chaser.check_updates(None))
        # Lower ver, higher rel
        ccr.info = lambda x: {'Name': 'test', 'Version': '0-2'}
        self.assertEquals([], chaser.check_updates(None))
        # Same ver, lower rel
        ccr.info = lambda x: {'Name': 'test', 'Version': '1-0'}
        self.assertEquals([], chaser.check_updates(None))
        # Same ver, same rel
        ccr.info = lambda x: {'Name': 'test', 'Version': '1-1'}
        self.assertEquals([], chaser.check_updates(None))
        # Same ver, higher rel: update
        ccr.info = lambda x: {'Name': 'test', 'Version': '1-2'}
        self.assertEquals([('test', '1-2')], chaser.check_updates(None))
        # Higher ver, lower rel: update
        ccr.info = lambda x: {'Name': 'test', 'Version': '2-0'}
        self.assertEquals([('test', '2-0')], chaser.check_updates(None))
        # Higher ver, same rel: update
        ccr.info = lambda x: {'Name': 'test', 'Version': '2-1'}
        self.assertEquals([('test', '2-1')], chaser.check_updates(None))
        # Higher ver, higher rel: update
        ccr.info = lambda x: {'Name': 'test', 'Version': '2-2'}
        self.assertEquals([('test', '2-2')], chaser.check_updates(None))

        # Decimal ver
        ccr.info = lambda x: {'Name': 'test', 'Version': '0.9-1'}
        self.assertEquals([], chaser.check_updates(None))
        ccr.info = lambda x: {'Name': 'test', 'Version': '1.0-1'}
        self.assertEquals([], chaser.check_updates(None))
        ccr.info = lambda x: {'Name': 'test', 'Version': '1.1-1'}
        self.assertEquals([('test', '1.1-1')], chaser.check_updates(None))

        # Ver with letters
        pacman.list_unofficial = lambda: [('test', '1a1-1')]
        ccr.info = lambda x: {'Name': 'test', 'Version': '1a0-1'}
        self.assertEquals([], chaser.check_updates(None))
        ccr.info = lambda x: {'Name': 'test', 'Version': '1a2-1'}
        self.assertEquals([('test', '1a2-1')], chaser.check_updates(None))

        pacman.list_unofficial, ccr.info = old

    def test_smoke_list_updates(self):
        old = chaser.check_updates
        chaser.check_updates = lambda: [('test', '0-0')]
        chaser.list_updates(None)
        chaser.check_updates = old

    def test_update(self):
        old = (chaser.check_updates, prompt.user_input, chaser.install)
        chaser.check_updates = lambda: [('test', '0-0')]
        prompt.user_input = lambda x: prompt.YES
        chaser.install = lambda x: self.assertEquals('test', x)
        chaser.update(None)

        prompt.user_input = lambda x: prompt.NO
        chaser.install = lambda x: self.assertTrue(False)
        chaser.update(None)

        chaser.check_updates = lambda: []
        prompt.user_input = lambda x: prompt.YES
        chaser.update(None)
        chaser.check_updates, prompt.user_input, chaser.install = old

    def test_smoke_search(self):
        chaser.search("test")

    def test_info_exists(self):
        self.assertNotEquals(1, chaser.info("aur2ccr"))

    def test_info_doesnt_exist(self):
        self.assertEquals(1, chaser.info("doesntexist"))
