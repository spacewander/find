# Test the command line interface of find

import subprocess
import unittest

def run_cmd(args):
    """Run command in shell, and return output as a list"""
    try:
        return subprocess.check_output(args, shell=True,
                stderr=subprocess.STDOUT).decode('utf8').splitlines()
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf8').splitlines()

class FindTest(unittest.TestCase):
    def test_find_with_args(self):
        find_py_res = run_cmd('./main.py ./findtui')
        find_res = run_cmd('find ./findtui')
        self.assertEqual(find_py_res, find_res)

    def test_find_with_shell_feature(self):
        find_py_res = run_cmd('./main.py ./findtui -type f | xargs wc -l')
        find_res = run_cmd('find ./findtui -type f | xargs wc -l')
        self.assertEqual(find_py_res, find_res)

    def test_find_forward_stderr(self):
        find_py_res = run_cmd('./main.py -exec ls')
        find_res = run_cmd('find -exec ls')
        self.assertEqual(find_py_res, find_res)

suite = unittest.TestLoader().loadTestsFromTestCase(FindTest)
unittest.TextTestRunner(verbosity=2).run(suite)

