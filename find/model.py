import os
from functools import reduce

from .options import  OPTION_NAMES

class FindModel(object):
    def __init__(self):
        self.cmd = 'find '
        self.exec_cmd = ''
        self.path = ''
        self.option_data = {}
        self.options_str = ""

    def reset_cmd(self, option_changed=False):
        if option_changed:
            opt_str = ["-%s %s" % (opt, self.option_data[opt]) for opt in self.option_data]
            self.options_str =  " ".join(opt_str)
        self.cmd = self.__generate_cmd()

    def update_actions(self, new_actions):
        self.exec_cmd = new_actions
        self.reset_cmd()

    def update_command(self, new_command):
        self.cmd = new_command

    def update_options(self, opt, text='', remove=False):
        if remove:
            self.option_data.pop(opt, None)
        else:
            self.option_data[opt] = text
        self.reset_cmd(option_changed=True)

    def update_path(self, new_path):
        self.path = new_path
        self.reset_cmd()

    def __generate_cmd(self):
        """generate final command from stored data"""
        if self.exec_cmd != '':
            # Use '{} ;' instead of '{} \;' or '{} +'.
            # The backslant in '{} \;' is for shell's escape(we use Popen, not real shell),
            # and '{} +' is used less frequently.
            return "find %s %s -exec %s {} ;" % (self.path, self.options_str,
                                                 self.exec_cmd)
        return "find %s %s" % (self.path, self.options_str)

    def complete_any(self, input):
        """
        If given input starts with '-', complete with options, else with path.
        """
        if input.startswith('-'):
            return self.complete_options(input)
        else:
            return self.complete_path(input)

    def complete_path(self, input):
        dirname = os.path.dirname(input)
        if dirname == '':
            dirname = '.'
        input = os.path.basename(input)
        source = os.listdir(dirname)
        return self.complete(input, source)

    def complete_options(self, input):
        source = OPTION_NAMES
        return self.complete(input, source, is_options=True)

    def complete(self, input, source, is_options=False):
        candidates = [candidate for candidate in source if candidate.startswith(input)]
        prefix = self.find_common_prefix(candidates)
        if is_options:
            candidates = [(candidate, candidate) \
                          for candidate in source if candidate.startswith(input)]
        else:
            candidates = [(candidate, candidate) \
                          for candidate in source if candidate.startswith(input)]
        return candidates, prefix

    def find_common_prefix(self, candidates):
        def common_prefix(prefix, string):
            i = 0
            for ch in zip(prefix, string):
                if ch[0] == ch[1]:
                    i += 1
            return prefix[:i]

        if len(candidates) is 0:
            return ''
        return reduce(common_prefix, candidates)

