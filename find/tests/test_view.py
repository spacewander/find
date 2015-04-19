import unittest

import urwid as uw
from urwid import ExitMainLoop

from find.model import FindModel
from find.view import FindView, exit_on_keys

ExitMainLoopException = ExitMainLoop().__class__

class ViewTest(unittest.TestCase):
    def cmd(self):
        return self.view.command_input.edit_text

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
        self.assertEqual("find path  -exec du -h {} ;",
                         self.cmd())

    def test_change_path_input(self):
        self.view.path_input.set_edit_text("path")
        cmd = "find path "
        self.assertEqual(cmd, self.model.cmd)
        self.assertEqual(cmd, self.cmd())

    def test_change_actions_input(self):
        self.view.actions_input.set_edit_text("du -h")
        cmd = "find   -exec du -h {} ;"
        self.assertEqual(cmd, self.model.cmd)
        self.assertEqual(cmd, self.cmd())

    def test_change_command_input(self):
        self.view.command_input.set_edit_text("find this")
        self.assertEqual(self.model.cmd, "find this")

    # ACTIONS
    def test_opt_radio_button_changed(self):
        bgroup = []
        rb = uw.RadioButton(bgroup, 'some', 'first True')
        self.view.opt_radio_button_changed(rb, False, {'option_name': 'opt'})
        self.assertEqual(self.model.options_str, "")
        self.view.opt_radio_button_changed(rb, True, {'option_name': 'opt'})
        self.assertEqual(self.model.options_str, "-opt some")
        self.assertEqual(self.cmd(), "find  -opt some")

    def test_opt_radio_button_changed_clear(self):
        bgroup = []
        rb = uw.RadioButton(bgroup, 'some', 'first True')
        self.view.opt_radio_button_changed(rb, True, {'option_name': 'opt'})
        clear = uw.RadioButton(bgroup, 'clear', 'first True')
        self.view.opt_radio_button_changed(clear, True, {'option_name': 'opt'})
        self.assertEqual(self.model.options_str, "")
        self.assertEqual(self.cmd().rstrip(), "find")

        self.view.opt_radio_button_changed(rb, True, {'option_name': 'opt'})
        self.assertEqual(self.model.options_str, "-opt some")

    def test_opt_radio_button_changed_clear2(self):
        bgroup1 = []
        bgroup2 = []
        rb1 = uw.RadioButton(bgroup1, 'some', 'first True')
        self.view.opt_radio_button_changed(rb1, True, {'option_name': 'opt'})
        rb2 = uw.RadioButton(bgroup2, 'some', 'first True')
        self.view.opt_radio_button_changed(rb2, True, {'option_name': 'name'})

        clear = uw.RadioButton(bgroup1, 'clear', 'first True')
        self.view.opt_radio_button_changed(clear, True, {'option_name': 'opt'})
        self.assertEqual(self.model.options_str, "-name some")

