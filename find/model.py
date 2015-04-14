class FindModel(object):
    def __init__(self):
        self.cmd = 'find '
        self.exec_cmd = ''
        self.path = ''

    def reset_cmd(self):
        self.cmd = self.__generate_cmd()

    def update_actions(self, new_actions):
        self.exec_cmd = new_actions
        self.reset_cmd()

    def update_command(self, new_command):
        self.cmd = new_command

    def update_path(self, new_path):
        self.path = new_path
        self.reset_cmd()

    def __generate_cmd(self):
        """generate final command from stored data"""
        if self.exec_cmd != '':
            # Use '{} ;' instead of '{} \;' or '{} +'.
            # The backslant in '{} \;' is for shell's escape(we use Popen, not real shell),
            # and '{} +' is used less frequently.
            return u"find %s -exec %s {} ;" % (self.path, self.exec_cmd)
        return u"find %s" % (self.path)
