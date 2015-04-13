#!/usr/bin/env python
# coding: utf-8

import subprocess
import sys

from view import setup_tui

def print_find_result(args):
    p = subprocess.Popen(args, stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    while True:
        line = p.stdout.readline()
        if line != '':
            print line.rstrip()
        else:
            break


if __name__ == '__main__':
    if len(sys.argv) == 1:
        cmd = setup_tui()
        if cmd != '':
            print_find_result(cmd.split())
    else:
        print_find_result(['find'] + sys.argv[1:])
