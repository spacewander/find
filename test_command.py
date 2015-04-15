# Test the command line interface of find

import subprocess
import unittest

def run_cmd(args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    out = []
    while True:
        line = p.stdout.readline()
        if line != '':
            out.append(line.rstrip())
        else:
            break
    return out

class FindTest(unittest.TestCase):
    def test_find_with_args(self):
        find_res = run_cmd(['find', './find'])
        find_py_res = run_cmd(['./find.py', './find'])
        self.assertEqual(find_py_res, find_res)

suite = unittest.TestLoader().loadTestsFromTestCase(FindTest)
unittest.TextTestRunner(verbosity=2).run(suite)
