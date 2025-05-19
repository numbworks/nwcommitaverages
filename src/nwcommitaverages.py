'''
A CLI application designed to calculate the average time between git commits.

Alias: nwca
'''

# GLOBAL MODULES
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum, auto
from subprocess import CompletedProcess
from tabulate import tabulate
from typing import Callable, Literal, Optional

# LOCAL MODULES
# CONSTANTS
class LOGTYPE(StrEnum):

    '''Represents a collection of options.'''

    TABLE = auto()
    DAILY = auto()
    MONTHLY = auto()
    
# STATIC CLASSES
# CLASSES
@dataclass(frozen = True)
class CommitItem():

    '''Collects all the necessary information related to a commit timestamp.'''

    date_str : str
    timestamp_int : int
    timestamp_dt : datetime
    ref_names : list[str]
@dataclass(frozen = True)
class DailyStatus():

    '''Represents a daily status.'''

    date_str : str
    timestamps : list[int]
    avg_minutes : float
    ref_names : list[str]
@dataclass(frozen = True)
class MonthlyStatus():

    '''Represents a monthly status.'''

    year_month : str
    dates : int
    timestamps : list[int]
    avg_minutes : float
    ref_names : list[str]
@dataclass(frozen = True)
class Summary():

    '''Represents a summary.'''

    commit_items : list[CommitItem]
    daily_statuses : list[DailyStatus]
    monthly_statuses : list[MonthlyStatus]
    daily_logging_function : Callable[[], None]
    monthly_logging_function : Callable[[], None]    
    table_logging_function : Callable[[], None]
class CommitAverageCalculator():
    
    '''Calculates custom averages related to the current git repository.'''

    __logging_function : Callable[[str], None]

    def __init__(self, logging_function : Callable[[str], None] = lambda msg : print(msg)) -> None:

        self.__logging_function = logging_function

    def __create_timestamp_dt(self, timestamp_int : int) -> datetime:

        '''Converts an integer timestamp to datetime.'''

        dt : datetime = datetime.fromtimestamp(int(timestamp_int), tz = timezone.utc)

        return dt
    def __create_commit_item(self, triplet_lst : list[str]) -> CommitItem:

        '''Creates a CommitItem object out of the provided arguments.'''

        date_str : str = triplet_lst[0]
        timestamp_int : int = int(triplet_lst[1])
        timestamp_dt : datetime = self.__create_timestamp_dt(timestamp_int = timestamp_int) 

        ref_names : list[str] = []
        if triplet_lst[2]:
            ref_names =  triplet_lst[2].split(",")

        commit_item : CommitItem = CommitItem(
            date_str = date_str,
            timestamp_int = timestamp_int,
            timestamp_dt = timestamp_dt,
            ref_names = ref_names
        ) 

        return commit_item
    def __update_ref_names(self, commit_item : CommitItem, ref_names : list[str]) -> CommitItem:

        '''Update commit_item.ref_names with ref_names.'''

        updated : CommitItem = CommitItem(
            date_str = commit_item.date_str,
            timestamp_int = commit_item.timestamp_int,
            timestamp_dt = commit_item.timestamp_dt,
            ref_names = ref_names
        )

        return updated    
    def __clean_ref_names(self, ref_names : list[str]) -> list[str]:

        '''Clean branch names.'''
        
        if not ref_names:
            return ref_names

        cleaned : list[str] = []

        for ref_name in ref_names:

            ref_name = ref_name.replace(" ", "")

            if ref_name in ["origin/HEAD", "origin/master", "HEAD->master"]:
                continue
          
            if ref_name.startswith("tag:"):
                continue

            if ref_name.startswith("origin/"):
                ref_name = ref_name.replace("origin/", "")
                cleaned.append(ref_name)
                continue

        return sorted(set(cleaned))
    def __create_year_month(self, date_str : str) -> str:

        '''"2023-11-17" -> 2023-11'''

        year_month : str = date_str[:7]

        return year_month
    def __count_days_in_month(self, daily_statuses : list[DailyStatus]) -> int:

        '''Counts days in month.'''

        return len(set(daily_status.date_str for daily_status in daily_statuses))
    def __extract_avg_minutes(self, daily_statuses : list[DailyStatus]) -> list[float]:

        '''Extracts the avg_minutes from daily_statuses.'''
        
        return [status.avg_minutes for status in daily_statuses]
    def __get_commit_items(self, file_path: Optional[str]) -> list[CommitItem]:

        '''
            Retrieve a collection of CommitItem objects out of the git log.

            git log output:
                2023-08-16;1692207406;
                2023-08-21;1692636918;origin/v4.6.0
                2023-08-21;1692637081;HEAD -> master, origin/master, origin/HEAD
                ...

            If "file_path" is None, "git log" is run against the current folder.
            Otherwise, it's run against the provided folder ("git -C file_path log").
        '''

        git_command : list[str] = ["git", "log", "--pretty=format:%cs;%ct;%D", "--reverse"]

        if file_path:
            git_command = ["git", "-C", file_path, "log", "--pretty=format:%cs;%ct;%D", "--reverse"]

        output : CompletedProcess = subprocess.run(
            git_command,
            capture_output = True,
            text = True,
            check = True
        )

        triplets : list[str] = list(map(str, output.stdout.splitlines()))
        commit_items : list[CommitItem] = []

        for triplet in triplets:
            triplet_lst : list[str] = triplet.split(";")
            commit_item : CommitItem = self.__create_commit_item(triplet_lst = triplet_lst)
            commit_items.append(commit_item)

        return commit_items
    def __clean_commit_items(self, commit_items : list[CommitItem]) -> list[CommitItem]:

        '''Cleans every commit_item.ref_names in commit items.'''

        cleaned : list[CommitItem] = []

        for commit_item in commit_items:

            new_ref_names : list[str] = self.__clean_ref_names(ref_names = commit_item.ref_names)
            new_commit_item : CommitItem = self.__update_ref_names(commit_item = commit_item, ref_names = new_ref_names)

            cleaned.append(new_commit_item)

        return cleaned
    def __create_daily_statuses(self, commit_items : list[CommitItem]) -> list[DailyStatus]:
        
        '''
        Creates a collection of DailyStatus objects out of commit_items.

        Example:
        [
            (date_str = "2023-11-17", timestamps = [1700239075, 1700239305, 1700240579, 1700246557], avg_minutes = 41.57, ref_names = ["ref1", "ref2"]), 
            (date_str = "2023-11-20", timestamps = [1700508271, 1700508711], avg_minutes = 7.33, ref_names = ["ref3', "ref4']), 
            ...
        ]
        '''

        grouped_by_date : defaultdict = defaultdict(list)

        for item in commit_items:
            grouped_by_date[item.date_str].append(item)

        daily_statuses : list[DailyStatus] = []

        for date_str, items in grouped_by_date.items():

            timestamps : list[int] = [item.timestamp_int for item in items]
            timestamps.sort()

            ref_names : list[str] = list({ref for item in items for ref in item.ref_names})

            avg_minutes : float = 0.0
            if len(timestamps) > 1:
                differences : list[int] = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]
                avg_minutes = round((sum(differences) / len(differences) / 60), 2)

            daily_status : DailyStatus = DailyStatus(date_str = date_str, timestamps = timestamps, avg_minutes = avg_minutes, ref_names = ref_names)
            daily_statuses.append(daily_status)

        return daily_statuses
    def __create_monthly_statuses(self, daily_statuses : list[DailyStatus]) -> list[MonthlyStatus]:

        '''
        Creates a collection of MonthlyStatus objects out of daily_statuses.

        Example:
        [
            (year_month = "2023-11", timestamps = [1700239075, 1700239305, 1700240579, 1700246557, 1700508271, 1700508711], avg_minutes = 24.45, ref_names = ["ref1", "ref2", "ref3", "ref4"]),
            (year_month = "2023-12", timestamps = [...], avg_minutes = ...),
            ...
        ]
        '''

        grouped_by_ym : defaultdict = defaultdict(list)

        for daily_status in daily_statuses:
            year_month : str = self.__create_year_month(date_str = daily_status.date_str)
            grouped_by_ym[year_month].append(daily_status)

        monthly_statuses : list[MonthlyStatus] = []

        for year_month, daily_statuses in grouped_by_ym.items():

            dates : int = self.__count_days_in_month(daily_statuses = daily_statuses)

            timestamps : list[int] = []
            ref_names : list[str] = []

            for daily_status in daily_statuses:
                timestamps.extend(daily_status.timestamps)
                ref_names.extend(daily_status.ref_names)

            timestamps.sort()
            ref_names = sorted(list(set(ref_names)))

            daily_avg_minutes : list[float] = self.__extract_avg_minutes(daily_statuses = daily_statuses)

            monthly_avg_minutes : float = 0.0
            if len(timestamps) > 1:
                monthly_avg_minutes = round(sum(daily_avg_minutes) / len(daily_avg_minutes), 2)

            monthly_status : MonthlyStatus = MonthlyStatus(
                year_month = year_month, 
                dates = dates, 
                timestamps = timestamps, 
                avg_minutes = monthly_avg_minutes, 
                ref_names = ref_names
            )
            
            monthly_statuses.append(monthly_status)

        return monthly_statuses
    def __log_table(self, monthly_statuses : list[MonthlyStatus]) -> None:

        '''
            Displays the MonthlyStatus objects as a table using the tabulate package.
        
            Example:
                +-------------+--------+-----------+---------------+--------------------------------+
                | YearMonth   |   Days |   Commits |   DailyAvgMin | RefNames                       |
                +=============+========+===========+===============+================================+
                | 2023-08     |      2 |         6 |        721.28 |  v3.2.0, v3.3.0                |
                +-------------+--------+-----------+---------------+--------------------------------+
                ...
        '''

        rows : list[list[object]] = []

        for monthly_status in monthly_statuses:
            row : list[object] = [
                monthly_status.year_month,
                monthly_status.dates,
                len(monthly_status.timestamps),
                str(f"{monthly_status.avg_minutes:.2f}"),
                ", ".join(monthly_status.ref_names)
            ]
            row[3] = str(row[3]).replace("0.00", "Not enough data")
            rows.append(row)

        table : str = tabulate(
            rows, 
            headers = ["YearMonth", "Days", "Commits", "DailyAvgMin", "RefNames"], 
            tablefmt = "grid", 
            disable_numparse = True
        )

        self.__logging_function(table)
    def __log_items(self, items : list) -> None:

        '''
            Logs each item of the given list on its own line - i.e.:
        
                - DailyStatus(date_str='2025-05-19', timestamps=[1747679247, 1747679425, 1747679655, 1747680456], avg_minutes=6.72, ref_names=[])
                - MonthlyStatus(year_month='2025-05', dates=1, timestamps=[1747679247, 1747679425, 1747679655, 1747680456], avg_minutes=6.72, ref_names=[])
        '''

        for item in items :
            self.__logging_function(item)
    def __orchestrate_logging(self, summary : Summary, log_type : Literal[LOGTYPE.TABLE, LOGTYPE.DAILY, LOGTYPE.MONTHLY]) -> None:

        '''Orchestrate summary logging according to log_type.'''

        if log_type == LOGTYPE.TABLE:
            summary.table_logging_function()

        elif log_type == LOGTYPE.DAILY:
            summary.daily_logging_function()
        
        elif log_type == LOGTYPE.MONTHLY:
            summary.monthly_logging_function()
        
        else:
            raise Exception(f"The provided 'log_type' is not supported ('{log_type}').")

    def run(self, file_path: Optional[str]) -> Summary:

        '''Returns a Summary or raises an Exception.'''

        commit_items : list[CommitItem] = self.__get_commit_items(file_path)
        commit_items = self.__clean_commit_items(commit_items = commit_items)

        daily_statuses : list[DailyStatus] = self.__create_daily_statuses(commit_items = commit_items)
        monthly_statuses : list[MonthlyStatus] = self.__create_monthly_statuses(daily_statuses = daily_statuses)

        daily_logging_function : Callable[[], None] = lambda : self.__log_items(items = daily_statuses)
        monthly_logging_function : Callable[[], None] = lambda : self.__log_items(items = monthly_statuses)
        table_logging_function : Callable[[], None] = lambda : self.__log_table(monthly_statuses = monthly_statuses)  
        
        summary : Summary = Summary(
            commit_items = commit_items,
            daily_statuses = daily_statuses,
            monthly_statuses = monthly_statuses,
            daily_logging_function = daily_logging_function,
            monthly_logging_function = monthly_logging_function,
            table_logging_function = table_logging_function
        )

        return summary
    def run_and_log(
        self, 
        file_path: Optional[str] = None, 
        log_type : Literal[LOGTYPE.TABLE, LOGTYPE.DAILY, LOGTYPE.MONTHLY] = LOGTYPE.TABLE) -> None:

        '''Logs the outcome of the calculation or the Exception message.'''

        try:

            summary : Summary = self.run(file_path = file_path)
            self.__orchestrate_logging(summary = summary, log_type = log_type)

        except Exception as e:

            self.__logging_function(str(e))

# MAIN
if __name__ == "__main__":
    CommitAverageCalculator().run_and_log()