import os

import urwid as uw

from .model import FindModel
from .options import (MENUS, OPTIONS, CHECKBOX_OPTION, RADIO_BUTTON_OPTION,
                      PATH_INPUT_OPTION, TEXT_INPUT_OPTION, INT_INPUT_OPTION)

LEN_OF_MENUS = len(MENUS)

CLR_RADIO_CHOOSE = 'clr'
# Global status variable, changed by `exit_on_keys` or `FindView`
EXIT_WITH_SUCCESS = False

# short keys
JUMP_TO_MENUS = 'ctrl n' # want to use ctrl+m, but it is equal to enter in terminal
JUMP_TO_OPTIONS = 'ctrl o'
JUMP_TO_COMMAND = 'ctrl e'

def bind_exit_key():
    EXIT_KEY = os.getenv('EXIT_KEY', ('q', 'Q', 'ctrl d'))
    if isinstance(EXIT_KEY, str):
        EXIT_KEY = (EXIT_KEY, )
    return EXIT_KEY

def bind_run_key():
    RUN_KEY = os.getenv('RUN_KEY', ('ctrl r', 'enter'))
    if isinstance(RUN_KEY, str):
        RUN_KEY = (RUN_KEY, )
    return RUN_KEY

EXIT_KEY = bind_exit_key()
RUN_KEY = bind_run_key()

def exit_on_keys(key):
    """
    Handle unhandled key input.

    If key given is q/Q/ctrl+d, exit UI simply;
    else if key given is ctrl+r, exit and prepare to run the command.

    Assuming you can connect with nearest extraterrestrial intelligent life by
    pressing ctrl+r in the terminal, You won't reserve it for trivival find(1) probably.
    Don't worry, You can set environment variables like RUN_KEY and EXIT_KEY to specify your key:

        RUN_KEY='ctrl d' find # will use ctrl+d to run the command
        EXIT_KEY='enter' find # will use enter to exit the UI(without running command)

    Some notices:
        1. to use ALT, you should type 'meta'
        2. to use SHIFT+OtherKey, you should type 'shift otherkey'
        3. no need to type '+' among each key

        So, to use 'ALT+R', you need to type 'shift meta r'
    """
    if key in EXIT_KEY:
        exit_loop(success=False)
    elif key in RUN_KEY:
        exit_loop(success=True)

def exit_loop(success):
    """exit UI loop and report success or not"""
    global EXIT_WITH_SUCCESS
    if success:
        EXIT_WITH_SUCCESS = True
    else:
        EXIT_WITH_SUCCESS = False
    raise uw.ExitMainLoop()

class FindView():
    def __init__(self, model):
        """
        The UI of FindView like this:

            menus-----------help---------
            options----------------------
            options----------------------
            notice_board-----------------
            exec_cmd_input---------------
            path_input-------------------
            cmd_input----------ok--reset-

        """
        help = uw.Text(
            "Click menu and edit options.\n"
            "Fill 'Execute Command' with the command you want to execute.\n"
            "Fill 'Path' with the path you want to run with.\n"
            "Press Ctrl+e to jump to command input\n"
            "Press Ctrl+n to jump to menus, and Ctrl+o to jump to Options\n"
            "Press q or Q or Ctrl+d to quit.\n"
            "Press reset to reset command with options/exec/path\n"
            "Press ctrl+r or click OK to run the command\n"
        )

        self.menus = self.create_menubar(MENUS)
        middle_of_menu = len(MENUS) // 2 - 1
        self.current_selected_menu_idx = middle_of_menu
        self.menus.focus_position = middle_of_menu

        self.__options_panels = {}
        self.options_panel = uw.Padding(self.create_options(MENUS[middle_of_menu]))

        self.notice_board = uw.Padding(self.create_notice_board())

        self.actions_input = uw.Edit("Execute Command:")
        self.path_input = uw.Edit("Path:")
        uw.connect_signal(self.actions_input, 'change', self.actions_changed)
        uw.connect_signal(self.path_input, 'change', self.path_changed)

        self.command_input = uw.Edit("Final Command: ")
        self.command_input.set_edit_text('find ')
        uw.connect_signal(self.command_input, 'change', self.command_changed)
        # click it to run the command
        ok_button = uw.Button("OK")
        uw.connect_signal(ok_button, 'click', self.ok_clicked)
        self.ok_button = uw.AttrMap(ok_button,
                                          None, focus_map='reversed')
        # click it to reset output command
        reset_button = uw.Button("Reset")
        uw.connect_signal(reset_button, 'click', self.reset_clicked)
        self.reset_button = uw.AttrMap(reset_button,
                                          None, focus_map='reversed')

        self.menus_area = uw.Columns([
                    ('weight', 0.5, self.menus),
                    ('weight', 0.2, uw.Filler(uw.Text(''))),
                    uw.Filler(help, valign='top')
        ])
        self.command_area = uw.Columns([
                    self.command_input,
                    ('weight', 0.1, self.ok_button),
                    ('weight', 0.1, self.reset_button)
        ])

        self.frame = uw.Frame(
            body=uw.Pile([
                ('weight', 0.7, self.menus_area),
                self.options_panel,
                self.notice_board,
                ('pack', self.actions_input),
                ('pack', self.path_input),
                ('pack', self.command_area)
            ])
        )

        self.bind_model(model)

    def bind_model(self, model):
        """Bind a model bidirectionally to store and deal with data."""
        self.model = model

    def filter_short_keys(self, keys, raw_keys):
        """
        This method will be used as input_filter in MainLoop.
        We will define short keys here, to catch them before widgets.
        Return keys so that the widgets can receive the input.
        """
        for i, k in enumerate(keys):
            if k == JUMP_TO_COMMAND:
                # the shortkey may be used as EXIT_KEY or RUN_KEY, so don't delete it from key
                self.focus_inputs()
            elif k == JUMP_TO_MENUS:
                self.focus_menus()
            elif k == JUMP_TO_OPTIONS:
                self.focus_options()
            elif k == 'up':
                if  self.__is_on_options_panel() and self.__is_on_option_n(0):
                    self.focus_menus()
                    del keys[i] # no need to up again
                elif self.__is_on_menus():
                    idx = self.menus.focus_position - 1
                    if idx >= 0:
                        self.current_selected_menu_idx = idx
                        self.options_panel.original_widget = self.create_options(MENUS[idx])
            elif k == 'down':
                if self.__is_on_menus():
                    idx = self.menus.focus_position + 1
                    if idx < LEN_OF_MENUS:
                        self.current_selected_menu_idx = idx
                        self.options_panel.original_widget = self.create_options(MENUS[idx])

        return keys

    def run(self):
        uw.MainLoop(self.frame, palette=[('reversed', 'standout', '')],
                    input_filter=self.filter_short_keys,
                    unhandled_input=exit_on_keys).run()

    def create_menubar(self, menus):
        body = []
        menus.sort()
        for i, menu in enumerate(menus):
            button = uw.Button(menu)
            uw.connect_signal(button, 'click', self.menu_chosen, user_args=[i])
            body.append(uw.AttrMap(button, None, focus_map='reversed'))
        # put all menus vertically, male clicking on them easier
        return uw.ListBox(uw.SimpleFocusListWalker(body))

    def create_options(self, choice):
        """
        Create options in 'choice' menu.
        There are five different options:
            1. CHECKBOX_OPTION: select this option or not, with checkbox
            2. RADIO_BUTTON_OPTION: select one of the value of an option, with radio buttons
            3. PATH_INPUT_OPTION: write value in an Edit. The value should be a path
            4. TEXT_INPUT_OPTION: write value in an Edit. No limit with the value
            5. INT_INPUT_OPTION: write positive value in an Edit.

        Each option displays with a label(option name), a tool according to its kind,
        and a description text.

        Except RADIO_BUTTON_OPTION, all options display like this:

            label   tool(Edit/CheckBox)     description

        RADIO_BUTTON_OPTION displays like this:

            label   placeholder...          description
            RadioButton group

        """
        if choice not in self.__options_panels:
            body = []
            options = sorted(OPTIONS[choice])
            for opt in options:
                label = uw.Text(opt.name)
                description = uw.Text("-- " + opt.description)

                if opt.type is CHECKBOX_OPTION:
                    tool = uw.CheckBox('',
                                       on_state_change=self.opt_checkbox_changed,
                                       user_data={'option_name': opt.name})

                elif opt.type is RADIO_BUTTON_OPTION:
                    bgroup = []
                    # click clear means you don't need this option any more
                    uw.RadioButton(bgroup, CLR_RADIO_CHOOSE, 'first True',
                            on_state_change=self.opt_radio_button_changed,
                            user_data={'option_name': opt.name})
                    for type in opt.data['type']:
                        uw.RadioButton(bgroup, type, 'first True',
                                on_state_change=self.opt_radio_button_changed,
                                user_data={'option_name': opt.name})

                    tool = uw.Columns(bgroup)

                elif opt.type is PATH_INPUT_OPTION:
                    tool = uw.Edit('> ')
                    uw.connect_signal(tool, 'change',
                                      self.opt_path_input_changed,
                                      user_args=[opt.name])

                elif opt.type is TEXT_INPUT_OPTION:
                    tool = uw.Edit('> ')
                    uw.connect_signal(tool, 'change',
                                      self.opt_text_input_changed,
                                      user_args=[opt.name])

                elif opt.type is INT_INPUT_OPTION:
                    tool = uw.IntEdit('> ')
                    uw.connect_signal(tool, 'change',
                                      self.opt_int_input_changed,
                                      user_args=[opt.name])
                else:
                    raise ValueError(
                        "Unknown options type got with name %s" % opt.name)

                if opt.type is RADIO_BUTTON_OPTION:
                    placeholder = uw.Text('')
                    col1 = uw.Columns([
                        ('weight', 0.3, label),
                        ('weight', 0.4, placeholder), description
                    ])
                    col2 = uw.Columns([
                        ('weight', 0.4, tool),
                        ('weight', 0.6, uw.Text(''))
                    ])
                    pile = uw.Pile([col1, col2])
                    body.append(uw.AttrMap(pile, None, focus_map='reversed'))
                else:
                    col = uw.Columns([
                        ('weight', 0.3, label),
                        ('weight', 0.4, tool), description
                    ])
                    body.append(uw.AttrMap(col, None, focus_map='reversed'))

            self.__options_panels[choice] = uw.ListBox(
                uw.SimpleFocusListWalker(body)
            )
        return self.__options_panels[choice]

    def create_notice_board(self, content=False):
        if not content:
            return uw.Filler(uw.Text(''))
        return None

    def focus_order(self, area_name):
        """
        Look up area name for its position in the view.
        Return 0 if area name given does not exist.
        """
        return {
            'menus'         : 0,
            'options_panel' : 1,
            'notice_board'  : 2,
            'actions_input' : 3,
            'path_input'    : 4,
            'command_input' : 5
        }.get(area_name, 0)

    def focus_menus(self):
        """Set focus to current selected menu"""
        menus_position = self.focus_order('menus')
        self.frame.body.focus_position = menus_position
        self.menus.focus_position = self.current_selected_menu_idx

    def focus_options(self):
        """Set focus to the first option of current selected menu"""
        self.frame.body.focus_position = self.focus_order('options_panel')

    def focus_inputs(self):
        """Set focus to command input"""
        self.frame.body.focus_position = self.focus_order('command_input')
        self.command_input.set_edit_pos(5) # set cursor behind 'find '

    # little helper
    def __is_on_menus(self):
        """If focus is on the menus"""
        return self.frame.body.focus == self.menus_area

    def __is_on_options_panel(self):
        """If focus is on the options_panel"""
        return self.frame.body.focus == self.options_panel

    def __is_on_option_n(self, n):
        """If focus is on nth option(n starts from 0)"""
        return self.options_panel.original_widget.focus_position == n

    # Action handler
    def actions_changed(self, input, text):
        self.model.update_actions(text)
        self.set_cmd(self.model.cmd)

    def command_changed(self, input, text):
        self.model.update_command(text)

    def menu_chosen(self, idx, button):
        self.current_selected_menu_idx = idx
        self.options_panel.original_widget = self.create_options(button.label)
        self.focus_options()

    def ok_clicked(self, button):
        exit_loop(success=True)

    def opt_checkbox_changed(self, cb, value, user_data):
        if value is True:
            self.model.update_options(user_data['option_name'], '')
        else:
            self.model.update_options(user_data['option_name'], remove=True)
        self.set_cmd(self.model.cmd)

    def opt_radio_button_changed(self, rb, value, user_data):
        # each click on a radio button will emit two changed event,
        # one for True -> False, the other for False -> True,
        # just need to handle the second one.
        if value is True:
            if rb.label is CLR_RADIO_CHOOSE:
                rb.set_state(False, do_callback=False)
                self.model.update_options(user_data['option_name'], remove=True)
            else:
                self.model.update_options(user_data['option_name'], rb.label)
            self.set_cmd(self.model.cmd)

    def opt_path_input_changed(self, option_name, pi, text):
        if text is "":
            self.model.update_options(option_name, remove=True)
        else:
            self.model.update_options(option_name, text)
        self.set_cmd(self.model.cmd)

    def opt_text_input_changed(self, option_name, ti, text):
        if text is "":
            self.model.update_options(option_name, remove=True)
        else:
            self.model.update_options(option_name, text)
        self.set_cmd(self.model.cmd)

    def opt_int_input_changed(self, option_name, ii, value):
        if value is "":
            self.model.update_options(option_name, remove=True)
        else:
            self.model.update_options(option_name, str(value))
        self.set_cmd(self.model.cmd)

    def path_changed(self, input, text):
        """Update path once the input changed"""
        self.model.update_path(text)
        self.set_cmd(self.model.cmd)

    def reset_clicked(self, button):
        """
        The command input allows you to edit the command directly.
        Once you aren't satisfied with the edited command,
        you can click the reset button and reset the output command with
        selected options, actions input and path input.
        """
        self.model.reset_cmd()
        self.set_cmd(self.model.cmd)

    #  UI change interface
    def set_cmd(self, cmd):
        """Set the display text in command input"""
        self.command_input.set_edit_text(cmd)


def setup_tui():
    model = FindModel()
    view = FindView(model)
    view.run()
    if EXIT_WITH_SUCCESS:
        return model.cmd
    else:
        return ''

