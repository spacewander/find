# Test the command line interface of find

import subprocess
import unittest

def run_cmd(args):
    """Run command in shell, and return output as a list"""
    try:
        return subprocess.check_output(args, shell=True).decode('utf8').split('\n')
    except subprocess.CalledProcessError:
        return []

class FindTest(unittest.TestCase):
    def test_find_with_args(self):
        find_py_res = run_cmd('./find.py ./find')
        find_res = run_cmd('find ./find')
        self.assertEqual(find_py_res, find_res)

    def test_find_with_shell_feature(self):
        find_py_res = run_cmd('./find.py ./find -type f | xargs wc -l')
        find_res = run_cmd('find ./find -type f | xargs wc -l')
        self.assertEqual(find_py_res, find_res)

suite = unittest.TestLoader().loadTestsFromTestCase(FindTest)
unittest.TextTestRunner(verbosity=2).run(suite)
