import unittest

import urwid as uw
from urwid import ExitMainLoop

from find.model import FindModel
from find.options import MENUS, OPTIONS
from find.view import (FindView, exit_on_keys, CLR_RADIO_CHOOSE,
                       JUMP_TO_MENUS, JUMP_TO_COMMAND, JUMP_TO_OPTIONS,
                       TRIGGER_COMPLETITION)

ExitMainLoopException = ExitMainLoop().__class__

class ViewTest(unittest.TestCase):
    # helpers
    def assert_notice_board_have_items(self, n):
        self.assertEqual(len(self.view.notice_board.original_widget.body), n)

    def get_option(self, n):
        """get the tool component of option n"""
        opts = self.view.options_panel.original_widget.contents()
        return opts[n][0].original_widget.contents[1][0]

    def choose_menu(self, n):
        """choose the Nth menu, start from zero"""
        self.view.menu_chosen(n, uw.Button(MENUS[n]))

    def press(self, key):
        """imitate a key is pressed"""
        self.view.filter_short_keys([key], [])
        return self

    def cmd(self):
        """return the text in command_input"""
        return self.view.command_input.edit_text

    def assert_options_is_from_menu(self, n):
        """assert the contents of options_panel comes from MENUS[n]"""
        options = self.view.options_panel.original_widget.body
        self.assertEqual(len(options), len(OPTIONS[MENUS[n]]),
                         "options' contents is incorrect")

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
        cmd = "find path"
        self.assertEqual(cmd, self.cmd())

    def test_change_actions_input(self):
        self.view.actions_input.set_edit_text("du -h")
        cmd = "find   -exec du -h {} ;"
        self.assertEqual(cmd, self.cmd())

    def test_change_command_input(self):
        self.view.command_input.set_edit_text("find this")
        self.assertEqual(self.model.cmd.path, "this")

    def test_jump_to_menus(self):
        self.press(JUMP_TO_MENUS)
        # .contents => ((widget, options), ...)
        self.assertEqual(self.view.frame.body.focus.contents[0][0],
                         self.view.menus)
        self.assertEqual(self.view.menus.focus_position,
                         self.view.current_selected_menu_idx)

    def test_jump_to_options_panel(self):
        self.press(JUMP_TO_OPTIONS)
        self.assertEqual(self.view.frame.body.focus,
                         self.view.options_panel)

    def test_jump_to_command_input(self):
        self.press(JUMP_TO_COMMAND)
        self.assertEqual(self.view.frame.body.focus.contents[0][0],
                         self.view.command_input)

    def test_focus_middle_menu_at_first(self):
        middle = len(MENUS) // 2 - 1
        self.assertEqual(self.view.menus.focus_position, middle)
        self.assertEqual(self.view.current_selected_menu_idx, middle)

    def test_press_up_on_first_option_jump_to_current_menu(self):
        # First, we need to focus on the first option of options_panel
        self.view.frame.body.focus_position = self.view.focus_order('options_panel')
        self.view.options_panel.original_widget.focus_position = 0

        self.press('up')
        self.assertEqual(self.view.frame.body.focus, self.view.menus_area)
        self.assertEqual(self.view.menus.focus_position,
                         self.view.current_selected_menu_idx)

    def test_press_up_on_menu_change_options(self):
        self.view.menus.focus_position = 1
        self.press('up')
        self.assertEqual(self.view.current_selected_menu_idx, 0)
        self.assert_options_is_from_menu(0)

        # should not change if there will be out of index
        self.press('up')
        self.assertEqual(self.view.current_selected_menu_idx, 0)

    def test_press_down_on_menu_change_options(self):
        the_last = len(MENUS) - 1
        self.view.menus.focus_position = the_last - 1
        self.press('down')
        self.assertEqual(self.view.current_selected_menu_idx, the_last)
        self.assert_options_is_from_menu(the_last)

        # should not change if there will be out of index
        self.press('down')
        self.assertEqual(self.view.current_selected_menu_idx, the_last)

    def test_press_completion_trigger_on_path_input(self):
        self.view.frame.body.focus_position = self.view.focus_order('path_input')
        self.view.path_input.set_edit_text('.g')
        self.press(TRIGGER_COMPLETITION)
        # .git, .gitignore
        self.assert_notice_board_have_items(2)

    def test_press_completion_trigger_on_command_input(self):
        self.view.frame.body.focus_position = self.view.focus_order('command_input')
        self.view.command_input.set_edit_text('find fa .g')
        self.press(TRIGGER_COMPLETITION)
        # .git, .gitignore
        self.assert_notice_board_have_items(2)

        self.view.command_input.set_edit_text('find afas -a')
        self.press(TRIGGER_COMPLETITION)
        # 'amin', 'anewer', 'atime'
        self.assert_notice_board_have_items(3)

    def test_press_completion_trigger_on_invalid_place(self):
        self.view.frame.body.focus_position = self.view.focus_order('options_panel')
        # Now the focus is on 'false'
        self.press(TRIGGER_COMPLETITION)
        # don't trigger completion on NON-PATH_INPUT_OPTION
        self.assert_notice_board_have_items(0)

    def test_press_completion_trigger_on_path_input_option(self):
        self.choose_menu(1) # Name
        self.view.frame.body.focus_position = self.view.focus_order('options_panel')
        # Now the focus is on 'ilname'
        focused = self.get_option(0)
        focused.set_edit_text('.g')
        self.press(TRIGGER_COMPLETITION)
        # .git, .gitignore
        self.assert_notice_board_have_items(2)

        cwc = self.view.component_waited_completed
        # change on path_input
        self.assertEqual(cwc, focused)
        self.assertEqual(cwc.edit_text, '.git')
        self.assertEqual(cwc.edit_pos, 4)

    # ACTIONS
    def test_complete_btn_clicked(self):
        ed = uw.Edit('')
        ed.set_edit_text('a b')
        ed2 = uw.Edit('')
        ed2.set_edit_text('b')
        btn = uw.Button('')
        self.view.component_waited_completed = ed
        self.view.complete_btn_clicked(btn, 'blind')
        self.assertEqual(ed.edit_text, 'a blind ')

        self.view.component_waited_completed = ed2
        self.view.complete_btn_clicked(btn, 'blind')
        self.assertEqual(ed2.edit_text, 'blind ')

    def test_menu_chosen(self):
        self.choose_menu(1)
        self.assertEqual(self.view.current_selected_menu_idx, 1)
        self.assert_options_is_from_menu(1)

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
        self.assertEqual(self.cmd(), "find  -opt")

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

