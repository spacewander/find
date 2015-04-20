import urwid as uw

from .model import FindModel
from .options import (MENUS, OPTIONS, CHECKBOX_OPTION, RADIO_BUTTON_OPTION,
                      PATH_INPUT_OPTION, TEXT_INPUT_OPTION, INT_INPUT_OPTION)

# Global status variable, changed by `exit_on_keys` or `FindView`
EXIT_WITH_SUCCESS = False

def exit_on_keys(key):
    if key in ('q', 'Q', 'ctrl d'):
        exit_loop(success=False)
    elif key is 'enter':
        exit_loop(success=True)

def exit_loop(success):
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
            "\nClick menu and edit options.\n"
            "Fill 'Execute Command' with the command you want to execute.\n"
            "Fill 'Path' with the path you want to run with.\n"
            "Press q or Q or Ctrl+d to quit.\n"
            "Press reset to reset command with options/exec/path\n"
            "Press Enter in input box or click OK to run the command\n\n"
        )

        self.menu = uw.Padding(self.create_menubar(MENUS))

        self.__options_panels = {}
        self.options_panel = uw.Padding(self.create_options(MENUS[0]))

        self.notice_board = uw.Padding(self.create_notice_board())

        self.actions_input = uw.Edit("Execute Command:")
        self.path_input = uw.Edit("Path:")
        uw.connect_signal(self.actions_input, 'change', self.actions_changed)
        uw.connect_signal(self.path_input, 'change', self.path_changed)

        self.command_input = uw.Edit("Final Command: ")
        self.command_input.set_edit_text('find')
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

        self.frame = uw.Frame(
            body=uw.Pile([
                ('weight', 0.6, uw.Columns([
                    self.menu, uw.Filler(help, valign='top')
                ], dividechars=20)),
                self.options_panel,
                self.notice_board,
                ('pack', self.actions_input),
                ('pack', self.path_input)]),
            footer=uw.Columns([
                self.command_input,
                ('weight', 0.1, self.ok_button),
                ('weight', 0.1, self.reset_button)]))
        self.bind_model(model)

    def bind_model(self, model):
        """Bind a model bidirectionally to store and deal with data."""
        self.model = model

    def run(self):
        uw.MainLoop(self.frame, palette=[('reversed', 'standout', '')],
                    unhandled_input=exit_on_keys).run()

    def create_menubar(self, menus):
        body = []
        for menu in menus:
            button = uw.Button(menu)
            uw.connect_signal(button, 'click', self.menu_chosen)
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
            for opt in OPTIONS[choice]:
                label = uw.Text(opt.name)
                description = uw.Text(opt.description)

                if opt.type is CHECKBOX_OPTION:
                    tool = uw.CheckBox('',
                                       on_state_change=self.opt_checkbox_changed,
                                       user_data={'option_name': opt.name})

                elif opt.type is RADIO_BUTTON_OPTION:
                    bgroup = []
                    # click clear means you don't need this option any more
                    uw.RadioButton(bgroup, 'clear', 'first True',
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
                    col = uw.Columns([
                        ('weight', 0.2, label),
                        ('weight', 0.3, placeholder), description
                    ])
                    pile = uw.Pile([col, tool])
                    body.append(uw.AttrMap(pile, None, focus_map='reversed'))
                else:
                    col = uw.Columns([
                        ('weight', 0.2, label),
                        ('weight', 0.3, tool), description
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

    # Action handler
    def actions_changed(self, input, text):
        self.model.update_actions(text)
        self.set_cmd(self.model.cmd)

    def command_changed(self, input, text):
        self.model.update_command(text)

    def menu_chosen(self, button):
        self.options_panel.original_widget = self.create_options(button.label)

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
            if rb.label is 'clear':
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

