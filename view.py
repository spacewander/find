import urwid as uw

from constants import MENUS, OPTIONS
from model import FindModel

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
    def __init__(self):
        help = uw.Text(
            u"Click menu and edit options.\n"
            u"Fill 'Execute Command' with the command you want to execute.\n"
            u"Fill 'Path' with the path you want to run with.\n"
            u"Press q or Q or Ctrl+d to quit.\n"
            u"Press reset to reset command with options/exec/path\n"
            u"Press Enter in input box or click OK to run the command\n\n"
        )

        self.menu = uw.Padding(self.create_menubar(MENUS))

        self.options_panel = uw.Padding(self.create_options(MENUS[0]))

        self.actions_input = uw.Edit(u"Execute Command:")
        self.path_input = uw.Edit(u"Path:")
        uw.connect_signal(self.actions_input, 'change', self.actions_changed)
        uw.connect_signal(self.path_input, 'change', self.path_changed)

        self.command_input = uw.Edit(u"Final Command: ")
        self.command_input.set_edit_text('find')
        uw.connect_signal(self.command_input, 'change', self.command_changed)
        # click it to run the command
        ok_button = uw.Button(u"OK")
        uw.connect_signal(ok_button, 'click', self.ok_clicked)
        ok_button = uw.AttrMap(ok_button,
                                          None, focus_map='reversed')
        # click it to reset output command
        reset_button = uw.Button(u"Rebuild")
        uw.connect_signal(reset_button, 'click', self.reset_clicked)
        reset_button = uw.AttrMap(reset_button,
                                          None, focus_map='reversed')

        self.frame = uw.Frame(header=help,
                              body=uw.Pile(
                                    [self.menu,
                                     self.options_panel,
                                     ('pack', self.actions_input),
                                     ('pack', self.path_input)]),
                              footer=uw.Columns([
                                  self.command_input,
                                  ('weight', 0.1, ok_button),
                                  ('weight', 0.1, reset_button)]))

    def bind_model(self, model):
        """Bind a model bidirectionally to store and deal with data."""
        self.model = model

    def run(self):
        uw.MainLoop(self.frame, palette=[('reversed', 'standout', '')],
                    unhandled_input=exit_on_keys).run()

    def create_menubar(self, options):
        body = []
        for opt in options:
            button = uw.Button(opt)
            uw.connect_signal(button, 'click', self.menu_chosen)
            body.append(uw.AttrMap(button, None, focus_map='reversed'))
        # put all menus vertically, male clicking on them easier
        return uw.ListBox(uw.SimpleFocusListWalker(body))

    def create_options(self, choice):
        body = []
        for opt in OPTIONS[choice]:
            button = uw.Button(opt)
            body.append(uw.AttrMap(button, None, focus_map='reversed'))
        return uw.ListBox(uw.SimpleFocusListWalker(body))

    # Action handler
    def actions_changed(self, input, text):
        self.model.update_actions(text)

    def command_changed(self, input, text):
        self.model.update_command(text)

    def menu_chosen(self, button):
        self.options_panel.original_widget = self.create_options(button.label)

    def ok_clicked(self, button):
        exit_loop(success=True)

    def path_changed(self, input, text):
        """Update path once the input changed"""
        self.model.update_path(text)

    def reset_clicked(self, button):
        """
        The command input allows you to edit the command directly.
        Once you aren't satisfied with the edited command,
        you can click the reset button and reset the output command with
        selected options, actions input and path input.
        """
        self.model.reset_cmd()

    #  UI change interface
    def set_cmd(self, cmd):
        """Set the display text in command input"""
        self.command_input.set_edit_text(cmd)


def setup_tui():
    view = FindView()
    model = FindModel(view)
    view.run()
    if EXIT_WITH_SUCCESS:
        return model.cmd
    else:
        return ''
