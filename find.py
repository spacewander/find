#!/usr/bin/env python
# coding: utf-8

import subprocess
import sys

from view import setup_tui

if __name__ == '__main__':
    if len(sys.argv) == 1:
        setup_tui()
    else:
        p = subprocess.Popen(['find'] + sys.argv[1:], stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        while True:
            line = p.stdout.readline()
            if line != '':
                print line.rstrip()
            else:
                break
