from __future__ import print_function

import subprocess
import sys

from findtui.view import setup_tui

def print_find_result(args):
    """
    Run find(1) and print the result to stdout.
    Notice: To make it almost the same as find(1) in shell,
    we run the command with shell=True, so, don't play with fire!
    """
    try:
        # WARN: Require python 2.7+
        print(subprocess.check_output(args, shell=True).decode('utf8'), end="")
    except subprocess.CalledProcessError:
        pass

def main():
    if len(sys.argv) == 1:
        cmd = setup_tui()
        if cmd != '':
            print_find_result(cmd)
    else:
        print_find_result(" ".join(['find'] + sys.argv[1:]))


