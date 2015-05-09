import os
import platform
import struct
from functools import reduce

import urwid as uw

from .model import FindModel
from .options import (MENUS, OPTIONS, CHECKBOX_OPTION, RADIO_BUTTON_OPTION,
                      PATH_INPUT_OPTION, TEXT_INPUT_OPTION, INT_INPUT_OPTION)
from .find_object import FindObject

LEN_OF_MENUS = len(MENUS)

CLR_RADIO_CHOOSE = 'clr'
# Global status variable, changed by `exit_on_keys` or `FindView`
EXIT_WITH_SUCCESS = False

def bind_key(name, key):
    """
    Bind key to specific key name, without checking key conflict.
    :param name is the name of bined key, like 'EXIT_KEY'
    :param key is a string of key, like 'ctrl n'
    """
    return os.getenv(name, key)

# short keys
JUMP_TO_MENUS = bind_key('JUMP_TO_MENUS', 'ctrl n')# want to use ctrl+m, but it is equal to enter in terminal
JUMP_TO_OPTIONS = bind_key('JUMP_TO_OPTIONS', 'ctrl o')
JUMP_TO_COMMAND = bind_key('JUMP_TO_COMMAND', 'ctrl e')
TRIGGER_COMPLETITION = bind_key('TRIGGER_COMPLETITION', 'tab')

def bind_keys(name, keys):
    """
    Bind keys to specific key name, without checking key conflict.
    :param name is the name of bined key, like 'EXIT_KEY'
    :param keys is a tuple of keys, like ('q', 'Q', 'ctrl d')
    """
    type = os.getenv(name, keys)
    if isinstance(type, str):
        type = (type, )
    return type


EXIT_KEY = bind_keys('EXIT_KEY', ('q', 'Q', 'ctrl d'))
RUN_KEY = bind_keys('RUN_KEY', ('ctrl r', 'enter'))

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

def get_terminal_size():
    """get width and height of console"""
    current_os = platform.system()
    tuple_xy = None
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        def ioctl_GWINSZ(fd):
            try:
                import fcntl
                import termios
                cr = struct.unpack('hh',
                                fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
                return cr
            except:
                pass
        cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2) # try 1
        if not cr:
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY) # try 2
                cr = ioctl_GWINSZ(fd)
                os.close(fd)
            except:
                pass
        if not cr:
            try:
                cr = (os.environ['LINES'], os.environ['COLUMNS']) # try 3
            except:
                pass
        if not cr:
            tuple_xy = None # accept it
        else:
            tuple_xy = (int(cr[1]), int(cr[0]))

    if tuple_xy is None:
        tuple_xy = (80, 25)      # default value
    return tuple_xy


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
                ('weight', 0.6, self.menus_area),
                ('weight', 1, self.options_panel),
                ('weight', 0.7, self.notice_board),
                ('pack', self.actions_input),
                ('pack', self.path_input),
                ('pack', self.command_area)
            ])
        )

        # Non-GUI part
        self.bind_model(model)
        self.component_waited_completed = None

    def bind_model(self, model):
        """Bind a model bidirectionally to store and deal with data."""
        self.model = model

    def filter_short_keys(self, keys, raw_keys):
        """
        This method will be used as input_filter in MainLoop.
        We will define short keys here, to catch them before widgets.
        Return keys so that the widgets can receive the input.
        """
        def handle_up(keys, k, i):
            if  self.__is_on_options_panel() and self.__is_on_option_n(0):
                self.focus_menus()
                del keys[i] # no need to up again
            elif self.__is_on_menus():
                idx = self.menus.focus_position - 1
                if idx >= 0:
                    self.current_selected_menu_idx = idx
                    self.options_panel.original_widget = self.create_options(
                        MENUS[idx]
                    )

        def handle_down(keys, k, i):
            if self.__is_on_menus():
                idx = self.menus.focus_position + 1
                if idx < LEN_OF_MENUS:
                    self.current_selected_menu_idx = idx
                    self.options_panel.original_widget = self.create_options(
                        MENUS[idx]
                    )

        def handle_trigger_completition_action(keys, k, i):
            if self.__is_on_options_panel():
                opt = self.options_panel.original_widget.focus.original_widget.contents[1][0]
                pos = self.options_panel.original_widget.focus_position
                name = MENUS[self.current_selected_menu_idx]
                if OPTIONS[name][pos].type == PATH_INPUT_OPTION:
                    self.complete(opt, self.model.complete_path)
            elif self.__is_on_command_input():
                self.complete(self.command_input, self.model.complete_any)
            elif self.__is_on_path_input():
                self.complete(self.path_input, self.model.complete_path)
            del keys[i]

        def handle_jump_to_command(keys, k, i):
            self.focus_inputs()
            del keys[i]

        def handle_jump_to_menus(keys, k, i):
            self.focus_menus()
            del keys[i]

        def handle_jump_to_options(keys, k, i):
            self.focus_options()
            del keys[i]

        def handle_remain_keys(*args): # lambda : pass is not allowed in python
            pass

        keys_handler_dict = {
            JUMP_TO_COMMAND: handle_jump_to_command,
            JUMP_TO_MENUS: handle_jump_to_menus,
            JUMP_TO_OPTIONS: handle_jump_to_options,
            'up': handle_up,
            'down': handle_down,
            TRIGGER_COMPLETITION: handle_trigger_completition_action
        }
        for i, k in enumerate(keys):
            keys_handler_dict.get(k, handle_remain_keys)(keys, k, i)

        return keys

    def run(self):
        uw.MainLoop(self.frame, palette=[('reversed', 'standout', '')],
                    input_filter=self.filter_short_keys,
                    unhandled_input=exit_on_keys).run()

    def create_menubar(self, menus):
        body = []
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
            options = OPTIONS[choice]
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

    def create_notice_board(self, contents=[]):
        # contents: [(text, data), ...]
        if len(contents) is 0:
            return uw.ListBox(uw.SimpleListWalker([]))

        board = []
        line_num = 10

        uw.Button.button_left = uw.Text('')
        uw.Button.button_right = uw.Text('')

        if contents[0][0] != contents[0][1]: # options
            for content in contents[:line_num]:
                text = content[0][len(content[1]):]
                btn = uw.Button(content[1], on_press=self.complete_btn_clicked,
                                user_data=content[1])
                description = uw.Text(text)
                board.append(uw.AttrMap(uw.Columns([btn,
                                                    ('weight', 1.5, description)]),
                                        None, focus_map='reversed'))

        else: # path or others
            width, _ = get_terminal_size()
            # len(text) + padding
            max_length = reduce(lambda x, y: max(x, len(y[0])), contents, 0) + 10
            # the result should be 1/2/4 according to terminal width
            content_per_row = width // max_length
            if content_per_row <= 1:
                content_per_row = 1
            elif content_per_row <= 3:
                content_per_row = 2
            else:
                content_per_row = 4

            # unlike zsh, we prefer to put contents vertically
            if line_num >= len(contents):
                for content in contents:
                    btn = uw.Button(content[0], on_press=self.complete_btn_clicked,
                                    user_data=content[1])
                    board.append(uw.AttrMap(uw.Columns([btn]), None, focus_map='reversed'))
            else:
                rows = min(len(contents) // content_per_row, line_num)
                for i in range(rows):
                    row = []
                    for j in range(content_per_row):
                        content = contents[i*content_per_row+j]
                        btn = uw.Button(content[0], on_press=self.complete_btn_clicked,
                                        user_data=content[1])
                        row.append(uw.AttrMap(btn, None, focus_map='reversed'))
                    board.append(uw.Columns(row, dividechars=5))

        # Should I reset the button_left/right after create the new notice_board?
        return uw.ListBox(uw.SimpleFocusListWalker(board))

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

    def complete(self, component_waited_completed, completer):
        """
        Implement auto completition.
        This method is relatived with notice_board displayed results,
        a component_waited_completed sending text and received completed text,
        and some methods of FindModel.
        This method will be triggered by short key, currently is TAB.

        User case:
            1. user press TAB(completion trigger)
            2. figure out common prefix and candidates
            3. use candidates to fill the notice_board
                3.1 fill it with Button(not pretty, but useful)
                3.2 one or two or four items each row,
                    according to the max length of candidates and the width of terminal
            4. complete component with prefix, and move the cursor to end

        :param
            component_waited_completed is a component has 'edit_text' and 'set_edit_text' attributes
        :param
            completer is a function accepted text, return candidate list and common prefix
        """
        text_pieces = component_waited_completed.edit_text.split(' ')
        input = text_pieces[-1]
        if self.component_waited_completed is component_waited_completed:
            self.trigger_counter += 1
        else:
            self.component_waited_completed = component_waited_completed
            self.trigger_counter = 1

        # candidates: [(text, data), ...]
        # prefix: string
        candidates, prefix = completer(input)
        self.notice_board.original_widget = self.create_notice_board(candidates)
        if prefix == '' or prefix == input:
            return
        if prefix.endswith(os.path.sep):
            candidates, prefix = completer(prefix)
            self.notice_board.original_widget = self.create_notice_board(candidates)

        text_pieces[-1] = prefix
        result = " ".join(text_pieces)
        self.component_waited_completed.set_edit_text(result)
        self.component_waited_completed.set_edit_pos(len(result))

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

    def __is_on_command_input(self):
        """If focus is on the command_input"""
        return self.frame.body.focus == self.command_area and \
                self.command_area.focus == self.command_input

    def __is_on_path_input(self):
        """If focus is on the path_input"""
        return self.frame.body.focus == self.path_input

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
        """Click OK button and exit the terminal UI, then run the find(1)"""
        exit_loop(success=True)

    def complete_btn_clicked(self, button, text):
        # make sure component_waited_completed is existed
        old_text = self.component_waited_completed.edit_text
        last_piece_start = old_text.rfind(' ') + 1
        if last_piece_start != 0:
            new_text = old_text[:last_piece_start] + text
        else:
            new_text = text
        new_text += ' '
        self.component_waited_completed.set_edit_text(new_text)
        self.component_waited_completed.set_edit_pos(len(new_text))
        # FIXME how can we jump back to component_waited_completed?

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
        """Set the display text in command input, with given FindObject"""
        pre = FindObject(self.command_input.edit_text)
        for attr in ['path', 'exec_cmd']: # no opts
            if getattr(cmd, attr) == "":
                pre_value = getattr(pre, attr)
                setattr(cmd, attr, pre_value)

        self.command_input.set_edit_text(cmd.toCmd())


def setup_tui():
    model = FindModel()
    view = FindView(model)
    view.run()
    if EXIT_WITH_SUCCESS:
        return view.command_input.edit_text
    else:
        return ''

