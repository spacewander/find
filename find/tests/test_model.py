import unittest

from find.model import FindModel

class ModelTest(unittest.TestCase):
    def setUp(self):
        self.model = FindModel()

    def test_reset_cmd(self):
        self.model.exec_cmd = 'du -h'
        self.model.path = 'path'
        self.model.reset_cmd()
        self.assertEqual(self.model.cmd, "find path -exec du -h {} ;")
        self.model.exec_cmd = ''
        self.model.reset_cmd()
        self.assertEqual(self.model.cmd, "find path")

    def test_update_actions(self):
        self.model.update_actions('du -h')
        self.assertEqual(self.model.cmd, "find  -exec du -h {} ;")

    def test_update_path(self):
        self.model.update_path('path')
        self.assertEqual(self.model.cmd, "find path")

    def test_update_command(self):
        cmd = 'some cmd'
        self.model.update_command(cmd)
        self.assertEqual(self.model.cmd, cmd)
