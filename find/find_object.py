class FindObject:
    """An object represented a find(1) command"""
    def __init__(self, cmd):
        self.exec_cmd = ''
        self.path = ''
        self.opts = ''
        if cmd.startswith('find'):
            # find ./find -type f -exec rm -rf {} ;
            # 012345      012     0123456
            #
            # 8 possibilities:
            # find
            # find -exec rm -rf {} ;
            # find -type f
            # find -type f -exec rm -rf {} ;
            # find ./bla
            # find ./bla -exec rm -rf {} ;
            # find ./bla -type f
            # find ./bla -type f -exec rm -rf {} ;
            exec_from = cmd.find('-exec ')
            if exec_from is not -1:
                exec_to = cmd.rfind('{}')
                self.exec_cmd = cmd[exec_from+6:exec_to].rstrip()
                cmd = cmd[:exec_from]
            path_end = cmd.find(' -')
            if path_end is not -1:
                self.path = cmd[5:path_end].rstrip()
                self.opts = cmd[path_end:].strip()
            else:
                self.path = cmd[5:].rstrip()

    @classmethod
    def build_with(cls, path, opts, exec_cmd):
        cmd = cls('')
        cmd.path = path
        cmd.opts = opts
        cmd.exec_cmd = exec_cmd
        return cmd

    def toCmd(self):
        if self.exec_cmd != '':
            # Use '{} ;' instead of '{} \;' or '{} +'.
            # The backslant in '{} \;' is for shell's escape(we use Popen, not real shell),
            # and '{} +' is used less frequently.
            cmd = "find %s %s -exec %s {} ;" % (self.path, self.opts,
                                                 self.exec_cmd)
        else:
            cmd = "find %s %s" % (self.path, self.opts)
        return cmd.rstrip()
