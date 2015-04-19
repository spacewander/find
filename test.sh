#!/bin/sh

# quickly run all the tests
# support python 2(2.7+) and 3

python -m test_command
python3 -m test_command
python -m unittest discover find.tests 'test_*.py'
python3 -m unittest discover find.tests 'test_*.py'
