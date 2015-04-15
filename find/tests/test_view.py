import unittest

from urwid import ExitMainLoop

from find.model import FindModel
from find.view import FindView, exit_on_keys

ExitMainLoopException = ExitMainLoop().__class__

class ViewTest(unittest.TestCase):
    def setUp(self):
        self.model = FindModel()
        self.view = FindView(self.model)

    def test_exit_on_keys(self):
        with self.assertRaises(ExitMainLoopException):
            exit_on_keys('q')
        from find.view import EXIT_WITH_SUCCESS
        self.assertFalse(EXIT_WITH_SUCCESS)
        with self.assertRaises(ExitMainLoopException):
            exit_on_keys('ctrl d')

    # unable to test clicking menu yet
    def test_click_ok_button(self):
        with self.assertRaises(ExitMainLoopException):
            self.view.ok_button.keypress((1,1), 'enter')
        from find.view import EXIT_WITH_SUCCESS
        self.assertTrue(EXIT_WITH_SUCCESS)

    def test_click_reset_button(self):
        self.model.path = "path"
        self.model.exec_cmd = "du -h"
        self.view.reset_button.keypress((1,1), 'enter')
        self.assertEqual(u"find path -exec du -h {} ;",
                         self.view.command_input.edit_text)

    def test_change_path_input(self):
        self.view.path_input.set_edit_text(u"path")
        cmd = u"find path"
        self.assertEqual(cmd, self.model.cmd)
        self.assertEqual(cmd, self.view.command_input.edit_text)

    def test_change_actions_input(self):
        self.view.actions_input.set_edit_text(u"du -h")
        cmd = u"find  -exec du -h {} ;"
        self.assertEqual(cmd, self.model.cmd)
        self.assertEqual(cmd, self.view.command_input.edit_text)

    def test_change_command_input(self):
        self.view.command_input.set_edit_text(u"find this")
        self.assertEqual(self.model.cmd, u"find this")
