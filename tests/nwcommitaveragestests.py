# GLOBAL MODULES
import unittest
from argparse import ArgumentParser, Namespace
from datetime import datetime, timezone
from parameterized import parameterized
from subprocess import CompletedProcess
from tabulate import tabulate
from typing import Callable, Literal, Optional, Tuple
from unittest.mock import Mock, patch

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwcommitaverages import LOGTYPE, _MessageCollection, APFactory, APAdapter, AsciiBannerManager, CLIManager, CommitAverageCalculator, CommitItem, MonthlyStatus, Summary
from nwcommitaverages import DailyStatus

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
class CommitAverageCalculatorTestCase(unittest.TestCase):

    def test_createtimestampdt_shouldreturnexpecteddatetimetz_wheninvoked(self) -> None:

        # Arrange
        timestamp_int : int = 1700000000
        expected : datetime = datetime.fromtimestamp(timestamp_int, tz = timezone.utc)

        # Act
        actual : datetime = CommitAverageCalculator()._CommitAverageCalculator__create_timestamp_dt(timestamp_int = timestamp_int)  # type: ignore

        # Assert
        self.assertEqual(expected, actual)
    def test_createcommititem_shouldreturnexpectedcommititem_wheninvoked(self) -> None:

        # Arrange
        triplet : list[str] = ["2023-12-01", "1700000000", "origin/feature-a,origin/dev"]
        expected : CommitItem = CommitItem(
            date_str = "2023-12-01",
            timestamp_int = 1700000000,
            timestamp_dt = datetime.fromtimestamp(1700000000, tz = timezone.utc),
            ref_names = ["origin/feature-a", "origin/dev"]
        )

        # Act
        actual : CommitItem = CommitAverageCalculator()._CommitAverageCalculator__create_commit_item(triplet_lst = triplet)  # type: ignore

        # Assert
        self.assertEqual(expected.date_str, actual.date_str)
        self.assertEqual(expected.timestamp_int, actual.timestamp_int)
        self.assertEqual(expected.timestamp_dt, actual.timestamp_dt)
        self.assertEqual(expected.ref_names, actual.ref_names)
    def test_updaterefnames_shouldreturnupdatedcommititem_wheninvoked(self) -> None:

        # Arrange
        commit_item : CommitItem = CommitItem(
            date_str = "2023-12-01",
            timestamp_int = 1700000000,
            timestamp_dt = datetime.fromtimestamp(1700000000, tz = timezone.utc),
            ref_names = ["main"]
        )
        ref_names : list[str] = ["develop", "release"]
        expected : CommitItem = CommitItem(
            date_str = "2023-12-01",
            timestamp_int = 1700000000,
            timestamp_dt = datetime.fromtimestamp(1700000000, tz = timezone.utc),
            ref_names = ["develop", "release"]
        )

        # Act
        actual : CommitItem = CommitAverageCalculator()._CommitAverageCalculator__update_ref_names(commit_item = commit_item, ref_names = ref_names)  # type: ignore

        # Assert
        self.assertEqual(expected.ref_names, actual.ref_names)
        self.assertEqual(expected.date_str, actual.date_str)
        self.assertEqual(expected.timestamp_int, actual.timestamp_int)
        self.assertEqual(expected.timestamp_dt, actual.timestamp_dt)
    def test_cleanrefnames_shouldreturncleanedlist_whenrefnamescontainssomeremovableitems(self) -> None:

        # Arrange
        ref_names : list[str] = [
            " origin/feature-x ",
            "origin/HEAD",
            "tag:v1.0",
            "origin/master",
            "HEAD->master",
            "origin/bugfix"
        ]
        expected : list[str] = ["bugfix", "feature-x"]

        # Act
        actual : list[str] = CommitAverageCalculator()._CommitAverageCalculator__clean_ref_names(ref_names = ref_names)  # type: ignore

        # Assert
        self.assertEqual(expected, actual)
    def test_cleanrefnames_shouldreturnemptylist_whenrefnamescontainsonlyremovableitems(self) -> None:

        # Arrange
        ref_names : list[str] = ["origin/HEAD", "origin/master", "tag:v1.0", "HEAD->master"]
        expected : list[str] = []

        # Act
        actual : list[str] = CommitAverageCalculator()._CommitAverageCalculator__clean_ref_names(ref_names = ref_names)  # type: ignore

        # Assert
        self.assertEqual(expected, actual)
    def test_createyearmonth_shouldreturnyearmonthstring_whenvaliddatestring(self) -> None:

        # Arrange
        date_str : str = "2023-11-17"
        expected : str = "2023-11"

        # Act
        actual : str = CommitAverageCalculator()._CommitAverageCalculator__create_year_month(date_str = date_str)  # type: ignore

        # Assert
        self.assertEqual(expected, actual)
    def test_countdaysinmonth_shouldreturnexpectedcount_wheninvoked(self) -> None:

        # Arrange
        daily_statuses : list[DailyStatus] = [
            DailyStatus(date_str = "2023-10-01", timestamps = [], avg_minutes = 15.0, ref_names = []),
            DailyStatus(date_str = "2023-10-01", timestamps = [], avg_minutes = 20.0, ref_names = []),
            DailyStatus(date_str = "2023-10-02", timestamps = [], avg_minutes = 10.0, ref_names = []),
        ]
        expected : int = 2

        # Act
        actual : int = CommitAverageCalculator()._CommitAverageCalculator__count_days_in_month(daily_statuses = daily_statuses)  # type: ignore

        # Assert
        self.assertEqual(expected, actual)
    def test_extractavgminutes_shouldreturnexpectedfloats_wheninvoked(self) -> None:

        # Arrange
        daily_statuses : list[DailyStatus] = [
            DailyStatus(date_str = "2023-10-01", timestamps = [], avg_minutes = 30.0, ref_names = []),
            DailyStatus(date_str = "2023-10-02", timestamps = [], avg_minutes = 45.5, ref_names = []),
        ]
        expected : list[float] = [30.0, 45.5]

        # Act
        actual : list[float] = CommitAverageCalculator()._CommitAverageCalculator__extract_avg_minutes(daily_statuses = daily_statuses)  # type: ignore

        # Assert
        self.assertEqual(expected, actual)
    def test_getcommititems_shouldreturnexpectedcommititems_whenstdoutisvalid(self) -> None:

        # Arrange
        stdout : str = (
            "2023-08-16;1692207406;\n"
            "2023-08-21;1692636918;origin/v4.6.0\n"
            "2023-08-21;1692637081;HEAD -> master, origin/master, origin/HEAD"
        )
        completed_process : CompletedProcess = CompletedProcess(args = [], returncode = 0, stdout = stdout)
        expected : list[CommitItem] = [
            CommitItem(date_str = "2023-08-16", timestamp_int = 1692207406, timestamp_dt = datetime.fromtimestamp(1692207406, tz = timezone.utc), ref_names = []),
            CommitItem(date_str = "2023-08-21", timestamp_int = 1692636918, timestamp_dt = datetime.fromtimestamp(1692636918, tz = timezone.utc), ref_names = ["origin/v4.6.0"]),
            CommitItem(date_str = "2023-08-21", timestamp_int = 1692637081, timestamp_dt = datetime.fromtimestamp(1692637081, tz = timezone.utc), ref_names = ["HEAD -> master", " origin/master", " origin/HEAD"])
        ]

        # Act
        with patch("subprocess.run") as mocked_run:
            mocked_run.return_value = completed_process
            actual : list[CommitItem] = CommitAverageCalculator()._CommitAverageCalculator__get_commit_items(file_path = None)  # type: ignore

        # Assert
        self.assertEqual(len(actual), 3)
        for i in range(0,3):
            self.assertEqual(expected[i].date_str, actual[i].date_str)
            self.assertEqual(expected[i].timestamp_int, actual[i].timestamp_int)
            self.assertEqual(expected[i].timestamp_dt, actual[i].timestamp_dt)
            self.assertEqual(expected[i].ref_names, actual[i].ref_names)
    def test_cleancommititems_shouldreturncommititemswithcleanrefs_whenrefsdirty(self) -> None:

        # Arrange
        commit_item : CommitItem = CommitItem(
            date_str = "2023-10-01",
            timestamp_int = 1700000000,
            timestamp_dt = datetime.fromtimestamp(1700000000, tz = timezone.utc),
            ref_names = [
                "origin/dev", 
                "origin/HEAD", 
                "tag:v1.0", 
                "origin/main", 
                "HEAD -> master", 
                "origin/dev"
            ]
        )
        expected : list[CommitItem] = [
            CommitItem(date_str = "2023-10-01", timestamp_int = 1700000000, timestamp_dt = datetime.fromtimestamp(1700000000, tz = timezone.utc), ref_names = ["dev", "main"])
        ]

        # Act
        actual : list[CommitItem] = CommitAverageCalculator()._CommitAverageCalculator__clean_commit_items(commit_items = [commit_item])  # type: ignore

        # Assert
        self.assertEqual(len(actual), 1)
        self.assertEqual(expected[0].date_str, actual[0].date_str)
        self.assertEqual(expected[0].timestamp_int, actual[0].timestamp_int)
        self.assertEqual(expected[0].timestamp_dt, actual[0].timestamp_dt)
        self.assertEqual(expected[0].ref_names, actual[0].ref_names)
    def test_createdailystatuses_shouldgroupandcomputeavg_wheninvoked(self) -> None:

        # Arrange
        commit_items : list[CommitItem] = [
            CommitItem(date_str = "2023-11-17", timestamp_int = 1700239075, timestamp_dt = datetime.fromtimestamp(1700239075), ref_names = ["ref1"]),
            CommitItem(date_str = "2023-11-17", timestamp_int = 1700239305, timestamp_dt = datetime.fromtimestamp(1700239305), ref_names = ["ref2"]),
            CommitItem(date_str = "2023-11-17", timestamp_int = 1700240579, timestamp_dt = datetime.fromtimestamp(1700240579), ref_names = []),
            CommitItem(date_str = "2023-11-17", timestamp_int = 1700246557, timestamp_dt = datetime.fromtimestamp(1700246557), ref_names = []),
            CommitItem(date_str = "2023-11-20", timestamp_int = 1700508271, timestamp_dt = datetime.fromtimestamp(1700508271), ref_names = ["ref3"]),
            CommitItem(date_str = "2023-11-20", timestamp_int = 1700508711, timestamp_dt = datetime.fromtimestamp(1700508711), ref_names = ["ref4"])
        ]
        expected : list[DailyStatus] = [
            DailyStatus(
                date_str = "2023-11-17",
                timestamps = [1700239075, 1700239305, 1700240579, 1700246557],
                avg_minutes = 41.57,
                ref_names = ["ref1", "ref2"]
            ),
            DailyStatus(
                date_str = "2023-11-20",
                timestamps = [1700508271, 1700508711],
                avg_minutes = 7.33,
                ref_names = ["ref3", "ref4"]
            )
        ]

        # Act
        actual : list[DailyStatus] = CommitAverageCalculator()._CommitAverageCalculator__create_daily_statuses(commit_items = commit_items)  # type: ignore

        # Assert
        self.assertEqual(len(actual), 2)

        for i in range(0,2):
            self.assertEqual(expected[i].date_str, actual[i].date_str)
            self.assertEqual(expected[i].timestamps, actual[i].timestamps)
            self.assertAlmostEqual(expected[i].avg_minutes, actual[i].avg_minutes, places = 2)
            self.assertCountEqual(expected[i].ref_names, actual[i].ref_names)
    def test_createmonthlystatuses_shouldgroupandcomputeavg_wheninvoked(self) -> None:

        # Arrange
        daily_statuses : list[DailyStatus] = [
            DailyStatus(
                date_str = "2023-11-17",
                timestamps = [1700239075, 1700239305, 1700240579, 1700246557],
                avg_minutes = 41.57,
                ref_names = ["ref1", "ref2"]
            ),
            DailyStatus(
                date_str = "2023-11-20",
                timestamps = [1700508271, 1700508711],
                avg_minutes = 7.33,
                ref_names = ["ref3", "ref4"]
            )
        ]
        expected : list[MonthlyStatus] = [
            MonthlyStatus(
                year_month = "2023-11",
                dates = 2,
                timestamps = [1700239075, 1700239305, 1700240579, 1700246557, 1700508271, 1700508711],
                avg_minutes = 24.45,
                ref_names = ["ref1", "ref2", "ref3", "ref4"]
            )
        ]
        calculator : CommitAverageCalculator = CommitAverageCalculator()

        # Act
        actual : list[MonthlyStatus] = calculator._CommitAverageCalculator__create_monthly_statuses(daily_statuses = daily_statuses)  # type: ignore

        # Assert
        self.assertEqual(len(expected), len(actual))

        self.assertEqual(expected[0].year_month, actual[0].year_month)
        self.assertEqual(expected[0].dates, actual[0].dates)
        self.assertEqual(expected[0].timestamps, actual[0].timestamps)
        self.assertAlmostEqual(expected[0].avg_minutes, actual[0].avg_minutes, places = 2)
        self.assertCountEqual(expected[0].ref_names, actual[0].ref_names)
    def test_logtable_shouldtabulatemonthlystatusesandlogtable_wheninvoked(self) -> None:

        # Arrange
        logs : list[str] = []
        logging_function : Callable[[str], None] = lambda msg : logs.append(msg)

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
            "| 2023-09     |      1 |         1 |   Not enough data | v3.4.0     |\n"
            "+-------------+--------+-----------+---------------+----------------+"
        )

        # Act, Assert
        with patch("nwcommitaverages.tabulate", return_value = expected) as mocked_tabulate:
            
            ca_calculator : CommitAverageCalculator = CommitAverageCalculator(logging_function = logging_function)
            ca_calculator._CommitAverageCalculator__log_table(monthly_statuses = monthly_statuses)  # type: ignore

            mocked_tabulate.assert_called_once()
            self.assertEqual(logs[0], expected)
    def test_logitems_shouldlogallitems_wheninvoked(self) -> None:

        # Arrange
        actual : list[str] = []
        logging_function : Callable[[str], None] = lambda msg : actual.append(msg)

        items : list[object] = [
            DailyStatus(date_str = "2025-05-19", timestamps = [1, 2, 3], avg_minutes = 6.72, ref_names = []),
            MonthlyStatus(year_month = "2025-05", dates = 1, timestamps = [1, 2, 3], avg_minutes = 6.72, ref_names = [])
        ]

        expected : list[str] = [
            "DailyStatus(date_str='2025-05-19', timestamps=[1, 2, 3], avg_minutes=6.72, ref_names=[])",
            "MonthlyStatus(year_month='2025-05', dates=1, timestamps=[1, 2, 3], avg_minutes=6.72, ref_names=[])"
        ]

        # Act
        calculator : CommitAverageCalculator = CommitAverageCalculator(logging_function = logging_function)
        calculator._CommitAverageCalculator__log_items(items = items)  # type: ignore

        # Assert
        self.assertEqual(expected[0], str(actual[0]))
        self.assertEqual(expected[1], str(actual[1]))
    def test_orchestratelogging_shouldcallexpectedloggingfunction_whenlogtypeisvalid(self) -> None:

        # Arrange
        table_logging_function : Mock = Mock()
        daily_logging_function : Mock = Mock()
        monthly_logging_function : Mock = Mock()

        summary : Summary = Summary(
            commit_items = [],
            daily_statuses = [],
            monthly_statuses = [],
            daily_logging_function = daily_logging_function,
            monthly_logging_function = monthly_logging_function,
            table_logging_function = table_logging_function
        )

        calculator : CommitAverageCalculator = CommitAverageCalculator()

        # Act
        calculator._CommitAverageCalculator__orchestrate_logging(summary = summary, log_type = LOGTYPE.TABLE)  # type: ignore
        calculator._CommitAverageCalculator__orchestrate_logging(summary = summary, log_type = LOGTYPE.DAILY)  # type: ignore
        calculator._CommitAverageCalculator__orchestrate_logging(summary = summary, log_type = LOGTYPE.MONTHLY)  # type: ignore

        # Assert
        table_logging_function.assert_called_once()
        daily_logging_function.assert_called_once()
        monthly_logging_function.assert_called_once()
    def test_orchestratelogging_shouldraiseexception_wheninvalidlogtype(self) -> None:

        # Arrange
        summary : Summary = Mock(spec = Summary)
        log_type : str = "INVALID"
        expected : str = "The provided 'log_type' is not supported ('INVALID')."

        # Act, Assert
        with self.assertRaises(Exception) as context:
            CommitAverageCalculator()._CommitAverageCalculator__orchestrate_logging(summary = summary, log_type = log_type)  # type: ignore

        self.assertEqual(expected, str(context.exception))

    def test_run_shouldcallexpectedprivatemethodsandreturnasummary_wheninvoked(self) -> None:

        # Arrange
        ca_calculator : CommitAverageCalculator = CommitAverageCalculator()
        file_path : Optional[str] = "/workspaces/nwsomething"

        with patch.object(ca_calculator, "_CommitAverageCalculator__get_commit_items", return_value=[]) as mocked_get_commit_items, \
             patch.object(ca_calculator, "_CommitAverageCalculator__clean_commit_items", return_value=[]) as mocked_clean_commit_items, \
             patch.object(ca_calculator, "_CommitAverageCalculator__create_daily_statuses", return_value=[]) as mocked_create_daily_statuses, \
             patch.object(ca_calculator, "_CommitAverageCalculator__create_monthly_statuses", return_value=[]) as mocked_create_monthly_statuses:

            # Act
            summary : Summary = ca_calculator.run(file_path = file_path)

            # Assert
            mocked_get_commit_items.assert_called_once_with(file_path)
            mocked_clean_commit_items.assert_called_once_with(commit_items = [])
            mocked_create_daily_statuses.assert_called_once_with(commit_items = [])
            mocked_create_monthly_statuses.assert_called_once_with(daily_statuses = [])

            self.assertIsInstance(summary, Summary)
    def test_runandlog_shouldcallrunandorchestralogging_wheninvoked(self) -> None:

        # Arrange
        ca_calculator : CommitAverageCalculator = CommitAverageCalculator()
        file_path : Optional[str] = "/workspaces/nwsomething"
        log_type : Optional[LOGTYPE] = LOGTYPE.TABLE

        with patch.object(ca_calculator, "run", return_value=Mock()) as mocked_run, \
             patch.object(ca_calculator, "_CommitAverageCalculator__orchestrate_logging") as mocked_orchestrate_logging:

            # Act
            ca_calculator.run_and_log(file_path = file_path, log_type = log_type)

            # Assert
            mocked_run.assert_called_once_with(file_path = file_path)
            mocked_orchestrate_logging.assert_called_once()
    def test_runandlog_shouldlogexceptionmessage_whenorchestrateloggingraisesexception(self) -> None:

        # Arrange
        actual : list[str] = []
        logging_function : Callable[[str], None] = lambda msg : actual.append(msg)

        ca_calculator : CommitAverageCalculator = CommitAverageCalculator(logging_function = logging_function)

        file_path : Optional[str] = "/workspaces/nwsomething"
        log_type : Optional[LOGTYPE] = LOGTYPE.TABLE
        summary : Mock = Mock(spec = Summary)
        
        expected : list[str] = [
            "The provided 'log_type' is not supported ('...')."
        ]

        with patch.object(ca_calculator, "run", return_value = summary) as mocked_run, \
             patch.object(ca_calculator, "_CommitAverageCalculator__orchestrate_logging", side_effect = Exception(expected[0])) as mocked_orchestrate_logging:

            # Act
            ca_calculator.run_and_log(file_path = file_path, log_type = log_type)

            # Assert
            mocked_orchestrate_logging.assert_called_once_with(summary = summary, log_type = log_type)
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
    def test_create_shouldcallexpectedprivatemethodsandreturnbanner_wheninvoked(self) -> None:

        # Arrange
        ascii_banner_manager : AsciiBannerManager = AsciiBannerManager()
        version : str = "1.0.5"
        max_lenght : int = 65
        
        figlet_tpl : tuple = ("ascii_art", max_lenght)
        frame_tpl : tuple = ("top_border", "bottom_border")

        with patch.object(ascii_banner_manager, "_AsciiBannerManager__validate") as validate, \
                patch.object(ascii_banner_manager, "_AsciiBannerManager__create_figlet", return_value = figlet_tpl) as create_figlet, \
                patch.object(ascii_banner_manager, "_AsciiBannerManager__create_frame", return_value = frame_tpl) as create_frame:

            # Act
            actual : str = ascii_banner_manager.create(version = version)

            # Assert
            validate.assert_called_once_with(version)
            create_figlet.assert_called_once()
            create_frame.assert_called_once_with(version, max_lenght)

            self.assertIn("top_border", actual)
            self.assertIn("ascii_art", actual)
            self.assertIn("bottom_border", actual)
class CLIManagerTestCase(unittest.TestCase):

    @parameterized.expand([
        ("/workspaces/nwsomething", LOGTYPE.TABLE),
        (None, None)
    ])
    def test_runandlog_shouldcallcalculatorwithargs_wheninvoked(self, file_path : Optional[str], log_type : Optional[LOGTYPE]) -> None:

        # Arrange
        ap_adapter : APAdapter = Mock()
        ap_adapter.parse_args.return_value = (file_path, log_type)

        ca_calculator : CommitAverageCalculator = Mock()

        cli_manager : CLIManager = CLIManager(
            ap_adapter = ap_adapter,
            ca_calculator = ca_calculator
        )

        # Act
        cli_manager.run_and_log()

        # Assert
        ca_calculator.run_and_log.assert_called_once_with(file_path = file_path, log_type = log_type)

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)