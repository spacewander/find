import unittest

from find.find_object import FindObject

class FindObjectTest(unittest.TestCase):
    def is_same(self, cmd, components):
        cmd = FindObject(cmd)
        self.assertEqual((cmd.path, cmd.opts, cmd.exec_cmd), components)

    def test_find0(self):
        self.is_same("some", ('', '', ''))

    # test 8 possibilities of find(1)
    def test_find1(self):
        self.is_same("find", ('', '', ''))

    def test_find2(self):
        self.is_same("find -exec rm -rf {} ;", ('', '', 'rm -rf'))

    def test_find3(self):
        self.is_same("find -type f", ('', '-type f', ''))

    def test_find4(self):
        self.is_same("find -type f -exec rm -rf {} ;",
                     ('', '-type f', 'rm -rf'))

    def test_find5(self):
        self.is_same("find ./bla", ('./bla', '', ''))

    def test_find6(self):
        self.is_same("find ./bla -exec rm -rf {} ;",
                     ('./bla', '', 'rm -rf'))

    def test_find7(self):
        self.is_same("find ./bla -type f", ('./bla', '-type f', ''))

    def test_find8(self):
        self.is_same("find ./bla -type f -exec rm -rf {} ;",
                     ('./bla', '-type f', 'rm -rf'))

