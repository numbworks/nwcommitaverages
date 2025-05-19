# GLOBAL MODULES
import unittest
from unittest.mock import Mock, mock_open, patch
from argparse import ArgumentParser, Namespace
from parameterized import parameterized
from typing import Callable, Optional, Tuple

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwcommitaverages import _MessageCollection, APFactory, APAdapter

# SUPPORT METHODS
# TEST CLASSES
class APFactoryTestCase(unittest.TestCase):

    def test_create_shouldreturnexpectedargumentparser_wheninvoked(self) -> None:

        # Arrange
        # Act
        argument_parser : ArgumentParser = APFactory().create()

        # Assert
        self.assertIsInstance(argument_parser, ArgumentParser)

        arguments : list[str] = []
        for action in argument_parser._actions:
            arguments.extend(action.option_strings)

        self.assertIn("--file_path", arguments)
        self.assertIn("-fp", arguments)
        self.assertIn("--logtype", arguments)
        self.assertIn("-lt", arguments)

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)