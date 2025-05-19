# GLOBAL MODULES
import unittest
from unittest.mock import Mock, mock_open, patch
from argparse import ArgumentParser, Namespace
from parameterized import parameterized
from typing import Callable, Optional, Tuple

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))

# SUPPORT METHODS
# TEST CLASSES

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)