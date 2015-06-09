import os
from functools import reduce

from .options import  OPTION_NAMES, OPTION_DATA, ACTION_OPTIONS
from .find_object import FindObject

# use enum if py3.4 is default
OPTION_CHANGE = 0
ACTION_CHANGE = 1

class FindModel(object):
    def __init__(self):
        self.cmd = FindObject('find ')
        self.exec_cmd = ''
        self.path = ''
        self.option_data = {}
        self.action_data = {}
        self.options_str = ""
        self.actions_str = ""

    def reset_cmd(self, option_changed=None):
        if option_changed == OPTION_CHANGE:
            opt_str = ["-%s %s" % (opt, self.option_data[opt]) for opt in self.option_data]
            self.options_str =  " ".join(opt_str)
        elif option_changed == ACTION_CHANGE:
            actions_str = ["-%s %s" % (opt, self.action_data[opt]) for opt in self.action_data]
            self.actions_str =  " ".join(actions_str)
        self.cmd = self.__generate_cmd()

    def update_actions(self, new_actions):
        # Use '{} ;' instead of '{} \;' or '{} +'.
        # The backslant in '{} \;' is for shell's escape(we use Popen, not real shell),
        # and '{} +' is used less frequently.
        self.exec_cmd = '-exec ' + new_actions + ' {} ;'
        self.reset_cmd()

    def update_command(self, new_command):
        """Update command with String"""
        self.cmd = FindObject(new_command)

    def update_options(self, opt, text='', remove=False):
        if opt in ACTION_OPTIONS:
            if remove:
                self.action_data.pop(opt, None)
            else:
                self.action_data[opt] = text
            self.reset_cmd(option_changed=ACTION_CHANGE)
        else:
            if remove:
                self.option_data.pop(opt, None)
            else:
                self.option_data[opt] = text
            self.reset_cmd(option_changed=OPTION_CHANGE)

    def update_path(self, new_path):
        self.path = new_path
        self.reset_cmd()

    def __generate_cmd(self):
        """generate final command object from stored data"""
        # if action options are given, ignore executed cmd
        if self.actions_str != '':
            return FindObject.build_with(self.path, self.options_str, self.actions_str)
        else:
            return FindObject.build_with(self.path, self.options_str, self.exec_cmd)

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
        # dirname is stupid, it just does some string work,
        # without checking if the dirname is existed
        try:
            if dirname == '':
                dirname = '.'
                source = [f for f in os.listdir(dirname)]
            else:
                source = [os.path.join(dirname, f) for f in os.listdir(dirname)]
            for i, f in enumerate(source):
                if os.path.isdir(f):
                    source[i] += '/'
        except OSError:
            source = []
        return self.complete(input, source)

    def complete_options(self, input):
        source = OPTION_NAMES
        return self.complete(input, source, is_options=True)

    def complete(self, input, source, is_options=False):
        candidates = [candidate for candidate in source if candidate.startswith(input)]
        prefix = self.find_common_prefix(candidates)
        if is_options:
            candidates = [(OPTION_DATA[candidate], candidate) \
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
                else:
                    break
            return prefix[:i]

        if len(candidates) is 0:
            return ''
        return reduce(common_prefix, candidates)

