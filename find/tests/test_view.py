import unittest

import urwid as uw
from urwid import ExitMainLoop

from find.model import FindModel
from find.options import MENUS, OPTIONS
from find.view import (FindView, exit_on_keys, CLR_RADIO_CHOOSE,
                       JUMP_TO_MENUS, JUMP_TO_COMMAND, JUMP_TO_OPTIONS)

ExitMainLoopException = ExitMainLoop().__class__

class ViewTest(unittest.TestCase):
    # helpers
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

    def test_run_on_keys(self):
        with self.assertRaises(ExitMainLoopException):
            exit_on_keys('ctrl r')
        from find.view import EXIT_WITH_SUCCESS
        self.assertTrue(EXIT_WITH_SUCCESS)

    # Unable to test specified EXIT_KEY and RUN_KEY.
    # They have been initialized once view.py is imported

    # Fake user input
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

    def test_jump_to_menus(self):
        self.view.filter_short_keys([JUMP_TO_MENUS], [])
        # .contents => ((widget, options), ...)
        self.assertEqual(self.view.frame.body.focus.contents[0][0],
                         self.view.menus)
        self.assertEqual(self.view.menus.focus_position,
                         self.view.current_selected_menu_idx)

    def test_jump_to_options_panel(self):
        self.view.filter_short_keys([JUMP_TO_OPTIONS], [])
        self.assertEqual(self.view.frame.body.focus,
                         self.view.options_panel)

    def test_jump_to_command_input(self):
        self.view.filter_short_keys([JUMP_TO_COMMAND], [])
        self.assertEqual(self.view.frame.body.focus.contents[0][0],
                         self.view.command_input)

    # ACTIONS
    def test_menu_chosen(self):
        self.view.menu_chosen(1, uw.Button(MENUS[1]))
        self.assertEqual(self.view.current_selected_menu_idx, 1)
        options = self.view.options_panel.original_widget.body
        self.assertEqual(len(options), len(OPTIONS[MENUS[1]]))

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
        clear = uw.RadioButton(bgroup, CLR_RADIO_CHOOSE, 'first True')
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

        clear = uw.RadioButton(bgroup1, CLR_RADIO_CHOOSE, 'first True')
        self.view.opt_radio_button_changed(clear, True, {'option_name': 'opt'})
        self.assertEqual(self.model.options_str, "-name some")

    def test_opt_checkbox_changed(self):
        cb = uw.CheckBox('')
        self.view.opt_checkbox_changed(cb, True, {'option_name': 'opt'})
        self.assertEqual(self.model.options_str, "-opt ")
        self.assertEqual(self.cmd(), "find  -opt ")

        self.view.opt_checkbox_changed(cb, False, {'option_name': 'opt'})
        self.assertEqual(self.model.options_str, "")
        self.assertEqual(self.cmd().rstrip(), "find")

    def test_opt_path_input_changed(self):
        pi = uw.Edit()
        self.view.opt_path_input_changed('opt', pi, "fi")
        self.assertEqual(self.model.options_str, "-opt fi")
        self.assertEqual(self.cmd(), "find  -opt fi")
        self.view.opt_path_input_changed('opt', pi, "Re")
        self.assertEqual(self.model.options_str, "-opt Re")

        self.view.opt_path_input_changed('opt', pi, "")
        self.assertEqual(self.model.options_str, "")

    def test_opt_text_input_changed(self):
        ti = uw.Edit()
        self.view.opt_path_input_changed('opt', ti, "some")
        self.assertEqual(self.model.options_str, "-opt some")
        self.assertEqual(self.cmd(), "find  -opt some")
        self.view.opt_path_input_changed('opt', ti, "else")
        self.assertEqual(self.model.options_str, "-opt else")

        self.view.opt_path_input_changed('opt', ti, "")
        self.assertEqual(self.model.options_str, "")

    def test_opt_int_input_changed(self):
        pi = uw.Edit()
        self.view.opt_path_input_changed('opt', pi, 3)
        self.assertEqual(self.model.options_str, "-opt 3")
        self.assertEqual(self.cmd(), "find  -opt 3")
        self.view.opt_path_input_changed('opt', pi, 4)
        self.assertEqual(self.model.options_str, "-opt 4")

        self.view.opt_path_input_changed('opt', pi, "")
        self.assertEqual(self.model.options_str, "")

