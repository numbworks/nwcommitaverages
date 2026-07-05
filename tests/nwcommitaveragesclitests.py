# GLOBAL MODULES
import unittest
from argparse import ArgumentParser, Namespace
from parameterized import parameterized
from subprocess import CompletedProcess
from typing import Callable, Optional
from unittest.mock import Mock, patch

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwcommitaverages import MonthlyStatus, Summary
from nwcommitaveragescli import _MessageCollection, APFactory, APAdapter, AsciiBannerManager, CLIManager, CLISTRING, TerminalWindowManager

# SUPPORT METHODS
# TEST CLASSES
class MessageCollectionCLIManagerTestCase(unittest.TestCase):

    def test_notenoughdata_shouldreturnexpectedmessage_wheninvoked(self):

        # Arrange
        expected : str = "Not enough data"

        # Act
        actual : str = _MessageCollection.not_enough_data()

        # Assert
        self.assertEqual(expected, actual)
class AsciiBannerManagerTestCase(unittest.TestCase):

    def test_validate_shouldraisevalueerror_whenversionisnone(self) -> None:

        # Arrange
        # Act, Assert
        with self.assertRaises(ValueError) as context:
            AsciiBannerManager()._AsciiBannerManager__validate(version = None) # type: ignore

        self.assertEqual(_MessageCollection.provided_version_empty_whitespace(), str(context.exception))
    def test_validate_shouldraisevalueerror_whenversioniswhitespace(self) -> None:

        # Arrange
        version : str = " "

        # Act, Assert
        with self.assertRaises(ValueError) as context:
            AsciiBannerManager()._AsciiBannerManager__validate(version = version) # type: ignore

        self.assertEqual(_MessageCollection.provided_version_empty_whitespace(), str(context.exception))
    def test_createfiglet_shouldreturnexpectedmaxlength_wheninvoked(self) -> None:

        # Arrange
        expected : int = 65

        # Act
        _, max_length = AsciiBannerManager()._AsciiBannerManager__create_figlet() # type: ignore

        # Assert
        self.assertEqual(expected, max_length)
    def test_createframe_shouldreturnexpectedtuple_wheninvoked(self) -> None:

        # Arrange
        version : str = "1.0.5"
        max_length : int = 65
        
        expected_top_line : str = "*" * 65
        expected_bottom_line : str = "*" * 46 + "Version: 1.0.5" + "*" * 5

        # Act
        top_line, bottom_line = AsciiBannerManager()._AsciiBannerManager__create_frame(version = version, max_length = max_length) # type: ignore

        # Assert
        self.assertEqual(expected_top_line, top_line)
        self.assertEqual(expected_bottom_line, bottom_line)
    def test_createstandard_shouldcallexpectedprivatemethodsandreturnbanner_wheninvoked(self) -> None:

        # Arrange
        ascii_banner_manager : AsciiBannerManager = AsciiBannerManager()
        version : str = "1.0.1"
        max_lenght : int = 65
        
        figlet_tpl : tuple = ("ascii_art", max_lenght)
        frame_tpl : tuple = ("top_border", "bottom_border")

        with patch.object(ascii_banner_manager, "_AsciiBannerManager__validate") as validate, \
                patch.object(ascii_banner_manager, "_AsciiBannerManager__create_figlet", return_value = figlet_tpl) as create_figlet, \
                patch.object(ascii_banner_manager, "_AsciiBannerManager__create_frame", return_value = frame_tpl) as create_frame:

            # Act
            actual : str = ascii_banner_manager.create_standard(version = version)

            # Assert
            validate.assert_called_once_with(version)
            create_figlet.assert_called_once()
            create_frame.assert_called_once_with(version, max_lenght)

            self.assertIn("top_border", actual)
            self.assertIn("ascii_art", actual)
            self.assertIn("bottom_border", actual)
    def test_createmini_shouldcallexpectedprivatemethodsandreturnminibanner_wheninvoked(self) -> None:

        # Arrange
        ascii_banner_manager : AsciiBannerManager = AsciiBannerManager()
        version : str = "1.0.1"
        expected : str = os.linesep.join([
            "*****************",
            "* NWCAVG v1.0.1 *",
            "*****************",
            ""
        ])

        with patch.object(ascii_banner_manager, "_AsciiBannerManager__validate") as validate:

            # Act
            actual : str = ascii_banner_manager.create_mini(version = version)

            # Assert
            validate.assert_called_once_with(version)
            self.assertEqual(expected, actual)
    def test_create_shouldreturnstandardbanner_whenterminalwidthisgreaterthanorequaltomaxlength(self) -> None:

        # Arrange
        ascii_banner_manager : AsciiBannerManager = AsciiBannerManager()
        version : str = "1.0.1"
        terminal_width : int = 80
        max_length : int = 54
        figlet_tpl : tuple = ("ascii_art", max_length)
        expected_banner : str = "standard_banner"

        with patch.object(ascii_banner_manager, "_AsciiBannerManager__create_figlet", return_value = figlet_tpl) as create_figlet, \
                patch.object(ascii_banner_manager, "create_standard", return_value = expected_banner) as create_standard:

            # Act
            actual : str = ascii_banner_manager.create(version = version, terminal_width = terminal_width)

            # Assert
            create_figlet.assert_called_once()
            create_standard.assert_called_once_with(version)
            self.assertEqual(expected_banner, actual)
    def test_create_shouldreturnminibanner_whenterminalwidthislessthanmaxlength(self) -> None:

        # Arrange
        ascii_banner_manager : AsciiBannerManager = AsciiBannerManager()
        version : str = "1.0.1"
        terminal_width : int = 40
        max_length : int = 54
        figlet_tpl : tuple = ("ascii_art", max_length)
        expected_banner : str = "mini_banner"

        with patch.object(ascii_banner_manager, "_AsciiBannerManager__create_figlet", return_value = figlet_tpl) as create_figlet, \
                patch.object(ascii_banner_manager, "create_mini", return_value = expected_banner) as create_mini:

            # Act
            actual : str = ascii_banner_manager.create(version = version, terminal_width = terminal_width)

            # Assert
            create_figlet.assert_called_once()
            create_mini.assert_called_once_with(version)
            self.assertEqual(expected_banner, actual)
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

    def test_converttotable_shouldreturntabulatedmonthlystatusesstring_wheninvoked(self) -> None:

        # Arrange
        monthly_statuses : list[MonthlyStatus] = [
            MonthlyStatus(
                year_month = "2023-08",
                dates = 2,
                timestamps = [1700239075, 1700239305, 1700240579, 1700246557, 1700508271, 1700508711],
                avg_minutes = 721.28,
                ref_names = ["v3.2.0", "v3.3.0"]
            ),
            MonthlyStatus(
                year_month = "2023-09",
                dates = 1,
                timestamps = [1700600000],
                avg_minutes = 0.00,
                ref_names = ["v3.4.0"]
            )
        ]

        expected : str = (
            "+-------------+--------+-----------+---------------+----------------+\n"
            "| YearMonth   |   Days |   Commits |   DailyAvgMin | RefNames       |\n"
            "+=============+========+===========+===============+================+\n"
            "| 2023-08     |      2 |         6 |        721.28 | v3.2.0, v3.3.0 |\n"
            "+-------------+--------+-----------+---------------+----------------+\n"
            "| 2023-09     |      1 |         1 | Not enough data | v3.4.0         |\n"
            "+-------------+--------+-----------+---------------+----------------+"
        )

        # Act & Assert
        with patch("nwcommitaveragescli.tabulate", return_value = expected) as tabulate:
            
            cli_manager : CLIManager = CLIManager()
            actual : str = cli_manager._CLIManager__convert_to_table(monthly_statuses = monthly_statuses) # type: ignore

            tabulate.assert_called_once()
            self.assertEqual(actual, expected)

    @parameterized.expand([
        "/workspaces/nwsomething",
        None
    ])
    def test_parse_shouldcallexpectedprivatemethods_wheninvoked(self, folder_path: Optional[str]) -> None:

        # Arrange
        ap_adapter: Mock = Mock()
        ap_adapter.parse_args.return_value = folder_path

        summary: Mock = Mock(spec = Summary)
        summary.monthly_statuses = []
        
        ca_calculator: Mock = Mock()
        ca_calculator.run.return_value = summary

        cli_manager = CLIManager(
            ap_adapter = ap_adapter,
            ca_calculator = ca_calculator
        )

        # Act, Assert
        with patch('nwcommitaveragescli.CLIManager._CLIManager__log_ascii_banner') as log_ascii_banner, \
             patch('nwcommitaveragescli.CLIManager._CLIManager__log_folder_path') as log_folder_path, \
             patch('nwcommitaveragescli.CLIManager._CLIManager__log_monthly_statuses') as log_monthly_statuses:
            
            cli_manager.parse()

            log_ascii_banner.assert_called_once()
            log_folder_path.assert_called_once_with(folder_path = folder_path)

            ap_adapter.parse_args.assert_called_once()
            ca_calculator.run.assert_called_once_with(folder_path = folder_path)

            log_monthly_statuses.assert_called_once_with(monthly_statuses = summary.monthly_statuses)

    def test_parse_shouldlogexception_wheninvalidargument(self) -> None:

        # Arrange
        expected : str = "Something went wrong during parsing or calculation."
        
        ap_adapter : Mock = Mock()
        ap_adapter.parse_args.side_effect = Exception(expected)
        
        logs : list[str] = []
        logging_function : Callable[[str], None] = lambda msg : logs.append(msg)

        cli_manager = CLIManager(
            ap_adapter = ap_adapter,
            logging_function = logging_function
        )

        # Act,          
        cli_manager.parse()

        # Assert
        self.assertEqual(logs[2], expected)

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)