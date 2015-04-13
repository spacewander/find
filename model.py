class FindModel(object):
    def __init__(self):
        self.cmd = ''
        self.exec_cmd = ''
        self.path = ''

    def bind_view(self, view):
        """Bind a view with this model. Called by FindView instance"""
        self.view = view

    def rebuild_cmd(self):
        self.cmd = self.__generate_cmd()
        self.view.set_cmd(self.cmd)

    def update_actions(self, new_actions):
        self.exec_cmd = new_actions
        self.rebuild_cmd()

    def update_command(self, new_command):
        self.cmd = new_command

    def update_path(self, new_path):
        self.path = new_path
        self.rebuild_cmd()

    def __generate_cmd(self):
        """generate final command from stored data"""
        if self.exec_cmd != '':
            return u"find %s -exec %s {} \;" % (self.path, self.exec_cmd)
        return u"find %s" % (self.path)
