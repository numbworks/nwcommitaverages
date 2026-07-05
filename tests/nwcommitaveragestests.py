# GLOBAL MODULES
import unittest
from datetime import datetime, timezone
from subprocess import CompletedProcess
from typing import Callable, Optional
from unittest.mock import Mock, patch

# LOCAL MODULES
import sys, os
sys.path.append(os.path.dirname(__file__).replace('tests', 'src'))
from nwcommitaverages import CommitAverageCalculator, DailyStatus, CommitItem, MonthlyStatus, Summary

# SUPPORT METHODS
# TEST CLASSES
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
            actual : list[CommitItem] = CommitAverageCalculator()._CommitAverageCalculator__get_commit_items(folder_path = None)  # type: ignore

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
    def test_run_shouldcallexpectedprivatemethodsandreturnasummary_wheninvoked(self) -> None:

        # Arrange
        ca_calculator : CommitAverageCalculator = CommitAverageCalculator()
        folder_path : Optional[str] = "/workspaces/nwsomething"

        with patch.object(ca_calculator, "_CommitAverageCalculator__get_commit_items", return_value=[]) as mocked_get_commit_items, \
             patch.object(ca_calculator, "_CommitAverageCalculator__clean_commit_items", return_value=[]) as mocked_clean_commit_items, \
             patch.object(ca_calculator, "_CommitAverageCalculator__create_daily_statuses", return_value=[]) as mocked_create_daily_statuses, \
             patch.object(ca_calculator, "_CommitAverageCalculator__create_monthly_statuses", return_value=[]) as mocked_create_monthly_statuses:

            # Act
            summary : Summary = ca_calculator.run(folder_path = folder_path)

            # Assert
            mocked_get_commit_items.assert_called_once_with(folder_path)
            mocked_clean_commit_items.assert_called_once_with(commit_items = [])
            mocked_create_daily_statuses.assert_called_once_with(commit_items = [])
            mocked_create_monthly_statuses.assert_called_once_with(daily_statuses = [])

            self.assertIsInstance(summary, Summary)

# MAIN
if __name__ == "__main__":
    result = unittest.main(argv=[''], verbosity=3, exit=False)