import unittest

from find.model import FindModel

class ModelTest(unittest.TestCase):
    def cmd(self):
        return self.model.cmd

    def setUp(self):
        self.model = FindModel()

    def test_reset_cmd(self):
        self.model.exec_cmd = 'du -h'
        self.model.path = 'path'
        self.model.reset_cmd()
        self.assertEqual(self.cmd(), "find path  -exec du -h {} ;")
        self.model.exec_cmd = ''
        self.model.reset_cmd()
        self.assertEqual(self.cmd(), "find path ")

    def test_reset_cmd_option_changed(self):
        self.model.option_data['some'] = 'true'
        self.model.reset_cmd(option_changed=True)
        self.assertEqual(self.cmd(), "find  -some true")
        self.model.option_data['some'] = 'false'
        self.model.reset_cmd()
        self.assertEqual(self.cmd(), "find  -some true")

    def test_reset_cmd_multi_options(self):
        self.model.option_data['some'] = 'true'
        self.model.option_data['any'] = 'false'
        self.model.reset_cmd(option_changed=True)
        # the generated options_str is unordered
        if self.model.options_str != "-any false -some true":
            self.assertEqual(self.model.options_str, "-some true -any false")
        else:
            self.assertTrue(True)

    def test_update_actions(self):
        self.model.update_actions('du -h')
        self.assertEqual(self.cmd(), "find   -exec du -h {} ;")

    def test_update_path(self):
        self.model.update_path('path')
        self.assertEqual(self.cmd(), "find path ")

    def test_update_command(self):
        cmd = 'some cmd'
        self.model.update_command(cmd)
        self.assertEqual(self.cmd(), cmd)

    def test_update_options(self):
        self.model.update_options('some', 'true')
        self.assertEqual(self.model.option_data['some'], 'true')
        self.model.update_options('some', remove=True)
        self.assertNotIn('some', self.model.option_data)

        self.model.update_options('any', 'true')
        self.assertEqual(self.model.option_data['any'], 'true')
        self.model.update_options('any', 'false')
        self.assertEqual(self.model.option_data['any'], 'false')

    def test_complete_any(self):
        self.assertEqual(self.model.complete_any('-a'),
                         self.model.complete_options('a'))
        self.assertEqual(self.model.complete_any('.'),
                         self.model.complete_path('.'))

    def test_complete_path(self):
        self.assertEqual(self.model.complete_path('.g'),
                         ['.git', '.gitignore'])
    def test_complete_options(self):
        self.assertEqual(self.model.complete_options('a'),
                         ['amin', 'anewer', 'atime'])

