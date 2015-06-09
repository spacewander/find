import os
import unittest

from findtui.model import FindModel, ACTION_CHANGE, OPTION_CHANGE
from findtui.options import ACTION_OPTIONS

class ModelTest(unittest.TestCase):
    def get_completion_data(self, candidates):
        """refine data part from given candidates"""
        return sorted([candidate[1] for candidate in candidates])

    def cmd(self):
        return self.model.cmd.toCmd()

    def setUp(self):
        self.model = FindModel()

    def test_reset_cmd(self):
        self.model.exec_cmd = '-exec du -h {} ;'
        self.model.path = 'path'
        self.model.reset_cmd()
        self.assertEqual(self.cmd(), "find path  -exec du -h {} ;")
        self.model.exec_cmd = ''
        self.model.reset_cmd()
        self.assertEqual(self.cmd(), "find path")

    def test_reset_cmd_option_changed(self):
        self.model.option_data['some'] = 'true'
        self.model.reset_cmd(option_changed=OPTION_CHANGE)
        self.assertEqual(self.cmd(), "find  -some true")
        self.model.option_data['some'] = 'false'
        self.model.reset_cmd()
        self.assertEqual(self.cmd(), "find  -some true")

    def test_reset_cmd_multi_options(self):
        self.model.option_data['some'] = 'true'
        self.model.option_data['any'] = 'false'
        self.model.reset_cmd(option_changed=OPTION_CHANGE)
        # the generated options_str is unordered
        if self.model.options_str != "-any false -some true":
            self.assertEqual(self.model.options_str, "-some true -any false")
        else:
            self.assertTrue(True)

    def test_reset_cmd_actions_changed(self):
        action1 = ACTION_OPTIONS.pop()
        action2 = ACTION_OPTIONS.pop()
        self.model.action_data[action1] = 'true'
        self.model.reset_cmd(option_changed=ACTION_CHANGE)
        self.assertEqual(self.cmd(), "find   -%s true" % action1)
        self.model.action_data[action2] = 'true'
        self.model.reset_cmd(option_changed=ACTION_CHANGE)
        if self.model.actions_str != "-%s true -%s true" % (action2, action1):
            self.assertEqual(self.model.actions_str, "-%s true -%s true" %
                    (action1, action2))
        else:
            self.assertTrue(True)

    def test_reset_cmd_action_and_option_changed(self):
        action = ACTION_OPTIONS.pop()
        option = "some"
        self.model.option_data[option] = 'true'
        self.model.reset_cmd(option_changed=OPTION_CHANGE)
        self.model.action_data[action] = 'do sth'
        self.model.reset_cmd(option_changed=ACTION_CHANGE)
        self.assertEqual(self.cmd(), "find  -some true -%s do sth" % action)

    def test_action_cover_exec_cmd(self):
        action = ACTION_OPTIONS.pop()
        self.model.action_data[action] = 'do sth'
        self.model.reset_cmd(option_changed=ACTION_CHANGE)
        self.model.exec_cmd = '-exec du -s {} ;'
        self.assertEqual(self.cmd(), "find   -%s do sth" % action)
        self.model.action_data.pop(action)
        self.model.reset_cmd(option_changed=ACTION_CHANGE)
        self.assertEqual(self.cmd(), "find   -exec du -s {} ;")

    def test_update_actions(self):
        self.model.update_actions('du -h')
        self.assertEqual(self.cmd(), "find   -exec du -h {} ;")

    def test_update_path(self):
        self.model.update_path('path')
        self.assertEqual(self.cmd(), "find path")

    def test_update_command(self):
        cmd = 'some cmd'
        self.model.update_command(cmd)
        self.assertEqual(self.cmd(), "find")

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
                         self.model.complete_options('-a'))
        self.assertEqual(self.model.complete_any('.'),
                         self.model.complete_path('.'))

    def test_complete_path(self):
        candidates, prefix = self.model.complete_path('.g')
        data = self.get_completion_data(candidates)
        self.assertEqual(data, ['.git/', '.gitignore'])
        self.assertEqual(prefix, '.git')

    def test_complete_path_with_dir(self):
        dir = 'findtui/tests'
        if os.path.exists(dir):
            files = os.listdir(dir)
            files = [os.path.join(dir, f) for f in files if f.startswith('t')]
            candidates, prefix = self.model.complete_path(os.path.join(dir, 't'))
            data = self.get_completion_data(candidates)
            self.assertEqual(data, sorted(files))
            self.assertEqual(prefix, 'findtui/tests/test_')

    def test_complete_path_with_nonexisted_dir(self):
        dir = '.git/HEAD/'
        if os.path.exists(dir):
            candidates, prefix = self.model.complete_path(os.path.join(dir))
            self.assertEqual(candidates, [])
            self.assertEqual(prefix, '')

    def test_complete_options(self):
        candidates, prefix = self.model.complete_options('-t')
        data = self.get_completion_data(candidates)
        self.assertEqual(data, ['-true', '-type'])
        self.assertEqual(prefix, '-t')

