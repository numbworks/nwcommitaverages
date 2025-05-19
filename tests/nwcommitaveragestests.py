# GLOBAL MODULES
import unittest
from unittest.mock import Mock, mock_open, patch
from argparse import ArgumentParser, Namespace
from parameterized import parameterized
from typing import Callable, Optional, Tuple, cast

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwcommitaverages import LOGTYPE, _MessageCollection, APFactory, APAdapter

# SUPPORT METHODS
# TEST CLASSES
class MessageCollectionTestCase(unittest.TestCase):

    def test_notenoughdata_shouldreturnexpectedmessage_wheninvoked(self):

        # Arrange
        expected : str = "Not enough data"

        # Act
        actual : str = _MessageCollection.not_enough_data()

        # Assert
        self.assertEqual(expected, actual)
    def test_providedlogtypenotsupported_shouldreturnexpectedmessage_wheninvalidlogtypegiven(self):

        # Arrange
        log_type : LOGTYPE = LOGTYPE.DAILY                                      # We fake this is not supported.
        expected : str = "The provided 'log_type' is not supported ('daily')."

        # Act
        actual : str = _MessageCollection.provided_log_type_not_supported(log_type)

        # Assert
        self.assertEqual(expected, actual)
    def test_parserdescription_shouldreturnexpectedmessage_wheninvoked(self):

        # Arrange
        expected : str = "Calculates the average commit value and logs the result."

        # Act
        actual : str = _MessageCollection.parser_description()

        # Assert
        self.assertEqual(expected, actual)
    def test_parserfilepath_shouldreturnexpectedmessage_wheninvoked(self):

        # Arrange
        expected : str = "The file path to the Git repository for which the average commit value is calculated."

        # Act
        actual : str = _MessageCollection.parser_file_path()

        # Assert
        self.assertEqual(expected, actual)
    def test_parserlogtype_shouldreturnexpectedmessage_wheninvoked(self):

        # Arrange
        expected : str = "The type of log ('table' for a tabular overview, 'daily' and 'monthly' for a list of statuses). The default is 'table'."

        # Act
        actual : str = _MessageCollection.parser_logtype()

        # Assert
        self.assertEqual(expected, actual)
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
class APAdapterTestCase(unittest.TestCase):

    @parameterized.expand([
        ("/workspaces/nwsomething", LOGTYPE.DAILY, ("/workspaces/nwsomething", LOGTYPE.DAILY)),
        ("/workspaces/nwsomething", None, ("/workspaces/nwsomething", None)),
        (None, None, (None, None))
    ])
    def test_parseargs_shouldreturnexpectedtuple_wheninvoked(
        self,
        file_path : Optional[str],
        logtype : Optional[LOGTYPE],
        expected : Tuple[Optional[str], Optional[LOGTYPE]]
    ) -> None:

        # Arrange
        argument_parser : Mock = Mock(spec = ArgumentParser)
        argument_parser.parse_args.return_value = Namespace(file_path = file_path, logtype = logtype)

        ap_factory : Mock = Mock()
        ap_factory.create.return_value = argument_parser

        # Act
        ap_adapter : APAdapter = APAdapter(ap_factory = ap_factory)
        actual : Tuple[Optional[str], Optional[LOGTYPE]] = ap_adapter.parse_args()

        # Assert
        self.assertEqual(expected, actual)

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)