import urwid as uw

from constants import MENUS, OPTIONS

def exit_on_keys(key):
    if key in ('q', 'Q', 'ctrl d'):
        raise uw.ExitMainLoop()


class FindView():
    def __init__(self):
        help = uw.Text(
            u"Click menu and edit options.\n"
            u"Fill 'Execute Command' with the command you want to execute.\n"
            u"Fill 'Path' with the path you want to run with.\n"
            u"Press q or Q or Ctrl+d to quit.\n\n"
        )

        self.menu = uw.Padding(self.create_menubar(MENUS))

        self.options_panel = uw.Padding(self.create_options(MENUS[0]))

        self.actions_input = uw.Edit("Execute Command:")
        self.path_input = uw.Edit("Path:")
        self.command_input = uw.Edit("Final Command: find ")

        self.frame = uw.Frame(header=help,
                              body=uw.Pile(
                                    [self.menu,
                                     self.options_panel,
                                     ('pack', self.actions_input),
                                     ('pack', self.path_input)]),
                              footer=self.command_input)

    def run(self):
        uw.MainLoop(self.frame, palette=[('reversed', 'standout', '')],
                    unhandled_input=exit_on_keys).run()

    def create_menubar(self, options):
        body = []
        for opt in options:
            button = uw.Button(opt)
            uw.connect_signal(button, 'click', self.menu_chosen, opt)
            body.append(uw.AttrMap(button, None, focus_map='reversed'))
        # put all menus vertically, male clicking on them easier
        return uw.ListBox(uw.SimpleFocusListWalker(body))

    def create_options(self, choice):
        body = []
        for opt in OPTIONS[choice]:
            button = uw.Button(opt)
            body.append(uw.AttrMap(button, None, focus_map='reversed'))
        return uw.ListBox(uw.SimpleFocusListWalker(body))

    def menu_chosen(self, button, choice):
        self.options_panel.original_widget = self.create_options(choice)


def setup_tui():
    view = FindView()
    view.run()
