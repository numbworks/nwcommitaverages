# GLOBAL MODULES
import unittest
from argparse import ArgumentParser, Namespace
from parameterized import parameterized
from subprocess import CompletedProcess
from typing import Optional
from unittest.mock import Mock, patch

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwcommitaverages import CommitAverageCalculator
from nwcommitaveragescli import APFactory, APAdapter, CLIManager, CLISTRING, TerminalWindowManager

# SUPPORT METHODS
# TEST CLASSES
class TerminalWindowManagerTestCase(unittest.TestCase):

    def test_defaultshutilwidthfunction_shouldreturncolumns_whenshutilissuccessful(self) -> None:

        # Arrange
        expected : int = 80

        with patch("shutil.get_terminal_size") as get_terminal_size:

            get_terminal_size.return_value = os.terminal_size((expected, 24))

            # Act
            actual : Optional[int] = TerminalWindowManager.default_shutil_width_function()

            # Assert
            self.assertEqual(actual, expected)
    def test_defaultshutilwidthfunction_shouldreturnnone_whenexceptionisraised(self) -> None:

        # Arrange
        with patch("nwcommitaveragescli.get_terminal_size", side_effect = Exception("Error")):

            # Act
            actual : Optional[int] = TerminalWindowManager.default_shutil_width_function()

            # Assert
            self.assertIsNone(actual)
    
    def test_defaultsttywidthfunction_shouldreturnwidth_whensttyissuccessful(self) -> None:

        # Arrange
        expected : int = 100

        process : Mock = Mock(spec = CompletedProcess)
        process.stdout = f"  {expected}  \n"
        
        with patch("subprocess.run", return_value = process) as mock_run:

            # Act
            actual : Optional[int] = TerminalWindowManager.default_stty_width_function()

            # Assert
            mock_run.assert_called_once_with(
                ["/bin/sh", "-c", "stty size | cut -d' ' -f2"],
                capture_output = True,
                text = True,
                check = False,
            )
            self.assertEqual(actual, expected)
    def test_defaultsttywidthfunction_shouldreturnnone_whensttyreturnsnegative(self) -> None:

        # Arrange
        process : Mock = Mock(spec = CompletedProcess)
        process.stdout = "-10\n"
        
        with patch("subprocess.run", return_value = process):

            # Act
            actual_width : Optional[int] = TerminalWindowManager.default_stty_width_function()

            # Assert
            self.assertIsNone(actual_width)
    def test_defaultsttywidthfunction_shouldreturnnone_whenexceptionisraised(self) -> None:

        # Arrange
        with patch("subprocess.run", side_effect = Exception("Error")):

            # Act
            actual_width : Optional[int] = TerminalWindowManager.default_stty_width_function()

            # Assert
            self.assertIsNone(actual_width)

    def test_init_shouldassignprovidedfunctions_wheninvokedwitharguments(self) -> None:

        # Arrange
        shutil_width_function : Mock = Mock()
        stty_width_function : Mock = Mock()

        # Act
        tw_manager : TerminalWindowManager = TerminalWindowManager(
            shutil_width_function = shutil_width_function,
            stty_width_function = stty_width_function
        )

        # Assert
        self.assertEqual(tw_manager._TerminalWindowManager__shutil_width_function, shutil_width_function)   # type: ignore
        self.assertEqual(tw_manager._TerminalWindowManager__stty_width_function, stty_width_function)       # type: ignore
    def test_init_shouldassigndefaultfunctions_wheninvokedwithoutarguments(self) -> None:

        # Arrange
        tw_manager : TerminalWindowManager = TerminalWindowManager()

        # Assert
        self.assertEqual(tw_manager._TerminalWindowManager__shutil_width_function, TerminalWindowManager.default_shutil_width_function) # type: ignore
        self.assertEqual(tw_manager._TerminalWindowManager__stty_width_function, TerminalWindowManager.default_stty_width_function)     # type: ignore

    def test_getorcutoff_shouldreturnshutilwidth_whenshutilissuccessful(self) -> None:

        # Arrange
        expected : int = 120
        shutil_width_function : Mock = Mock(return_value = expected)
        stty_width_function : Mock = Mock()
        
        tw_manager : TerminalWindowManager = TerminalWindowManager(
            shutil_width_function = shutil_width_function,
            stty_width_function = stty_width_function
        )

        # Act
        actual : int = tw_manager.get_or_cutoff()

        # Assert
        self.assertEqual(actual, expected)
        shutil_width_function.assert_called_once()
        stty_width_function.assert_not_called()
    def test_getorcutoff_shouldreturnsttywidth_whenshutilfailsandsttyissuccessful(self) -> None:

        # Arrange
        expected : int = 90
        shutil_width_function : Mock = Mock(return_value = None)
        stty_width_function : Mock = Mock(return_value = expected)
        
        tw_manager : TerminalWindowManager = TerminalWindowManager(
            shutil_width_function = shutil_width_function,
            stty_width_function = stty_width_function
        )

        # Act
        actual : int = tw_manager.get_or_cutoff()

        # Assert
        self.assertEqual(actual, expected)
        shutil_width_function.assert_called_once()
        stty_width_function.assert_called_once()
    def test_getorcutoff_shouldreturncutoffwidth_whenbothfunctionsfail(self) -> None:

        # Arrange
        shutil_width_function : Mock = Mock(return_value = None)
        stty_width_function : Mock = Mock(return_value = None)
        
        tw_manager : TerminalWindowManager = TerminalWindowManager(
            shutil_width_function = shutil_width_function,
            stty_width_function = stty_width_function
        )

        # Act
        actual : int = tw_manager.get_or_cutoff()

        # Assert
        self.assertEqual(actual, TerminalWindowManager.cutoff_width)
        shutil_width_function.assert_called_once()
        stty_width_function.assert_called_once()
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
        argument_parser.parse_args.return_value = Namespace(folder_path = folder_path)

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