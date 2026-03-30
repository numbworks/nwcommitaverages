# GLOBAL MODULES
import unittest
from argparse import ArgumentParser, Namespace
from parameterized import parameterized
from typing import Optional, Tuple
from unittest.mock import Mock, patch

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwcommitaverages import LOGTYPE, CommitAverageCalculator
from nwcommitaveragescli import APFactory, APAdapter, CLIManager, CLISTRING

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

        self.assertIn(CLISTRING.OPTION_FOLDERPATH_FLAGS[0], arguments)
class APAdapterTestCase(unittest.TestCase):

    @parameterized.expand([
        ("/workspaces/nwsomething", "/workspaces/nwsomething"),
        (None, None)
    ])
    def test_parseargs_shouldreturnexpectedstring_wheninvoked(self, folder_path : Optional[str], expected : Optional[str]) -> None:

        # Arrange
        argument_parser : Mock = Mock(spec = ArgumentParser)
        argument_parser.parse_args.return_value = Namespace(file_path = folder_path)

        ap_factory : Mock = Mock()
        ap_factory.create.return_value = argument_parser

        # Act
        ap_adapter : APAdapter = APAdapter(ap_factory = ap_factory)
        actual : Optional[str] = ap_adapter.parse_args()

        # Assert
        self.assertEqual(expected, actual)
class CLIManagerTestCase(unittest.TestCase):

    @parameterized.expand([
        "/workspaces/nwsomething",
        None
    ])
    def test_runandlog_shouldcallcalculatorwithargs_wheninvoked(self, folder_path : Optional[str]) -> None:

        # Arrange
        ap_adapter : APAdapter = Mock()
        ap_adapter.parse_args.return_value = (folder_path)

        ca_calculator : CommitAverageCalculator = Mock()

        cli_manager : CLIManager = CLIManager(
            ap_adapter = ap_adapter,
            ca_calculator = ca_calculator
        )

        # Act
        cli_manager.run_and_log()

        # Assert
        ca_calculator.run_and_log.assert_called_once_with(folder_path = folder_path)

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)