# Test the command line interface of find

import subprocess
import unittest

def run_cmd(args):
    try:
        return subprocess.check_output(args).decode('utf8').split('\n')
    except subprocess.CalledProcessError:
        return []

class FindTest(unittest.TestCase):
    def test_find_with_args(self):
        find_py_res = run_cmd(['./find.py', './find'])
        find_res = run_cmd(['find', './find'])
        self.assertEqual(find_py_res, find_res)

suite = unittest.TestLoader().loadTestsFromTestCase(FindTest)
unittest.TextTestRunner(verbosity=2).run(suite)
