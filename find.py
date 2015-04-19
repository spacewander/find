#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

import subprocess
import sys

from find.view import setup_tui

def print_find_result(args):
    try:
        # WARN: Require python 2.7+
        print(subprocess.check_output(args).decode('utf8'), end="")
    except subprocess.CalledProcessError:
        pass


if __name__ == '__main__':
    if len(sys.argv) == 1:
        cmd = setup_tui()
        if cmd != '':
            print_find_result(cmd.split())
    else:
        print_find_result(['find'] + sys.argv[1:])
