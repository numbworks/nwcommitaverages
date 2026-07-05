'''
A CLI application built around nwcommitaverages.

Alias: nwcavg
'''

# GLOBAL MODULES
import os
from pathlib import Path
import subprocess
from argparse import ArgumentParser, Namespace
from enum import StrEnum, auto
from shutil import get_terminal_size
from subprocess import CompletedProcess
from tabulate import tabulate
from typing import Callable, Final, Literal, Optional

# NW/LOCAL MODULES
from nwcommitaverages import CommitAverageCalculator, MonthlyStatus, Summary
from setupinfo import CLI_NAME, CLI_DESCRIPTION, PROJECT_VERSION

# GENERIC CLASSES
# CONSTANTS
class CLISTRING:

    '''Collects all the CLI-related strings.'''

    OPTION_FOLDERPATH_FLAGS : Final[list[str]] = ["--folder_path"]
    OPTION_FOLDERPATH_REQUIRED : Final[bool] = False
    OPTION_FOLDERPATH_HELP : Final[str] = "The path to the Git repository folder for which the average commit value is calculated."
class LOGTYPE(StrEnum):

    '''Represents a collection of log types.'''

    TABLE = auto()
    DAILY = auto()
    MONTHLY = auto()
class HEADER(StrEnum):

    '''Represents a collection of headers.'''

    YEARMONTH = "YearMonth"
    DAYS = "Days"
    COMMITS = "Commits"
    DAILYAVGMIN = "DailyAvgMin"
    REFNAMES = "RefNames"

# STATIC CLASSES
class _MessageCollectionCommitAverageCalculator():

    '''Collects all the messages used for logging and for the exceptions used by CommitAverageCalculator.'''

    @staticmethod
    def not_enough_data() -> str:
        return "Not enough data"
    @staticmethod
    def provided_log_type_not_supported(log_type : LOGTYPE) -> str:
        return f"The provided 'log_type' is not supported ('{log_type}')."
    @staticmethod
    def field_equals_to(name: str, value: str) -> str:
        return f"{name}:'{value}'"
class _MessageCollectionAsciiBannerManager():

    '''Collects all the messages used for logging and for the exceptions.'''

    @staticmethod
    def provided_version_empty_whitespace() -> str:
        return "The provided 'version' is empty or whitespace."
class _MessageCollection(
    _MessageCollectionAsciiBannerManager,
    _MessageCollectionCommitAverageCalculator):

    '''Collects all the messages used for logging and for the exceptions.'''

    pass

# CLASSES
class AsciiBannerManager:

    """
        Creates the ASCII banner for the provided library's version.

        The figlet can be generated using 
            - 'http://www.network-science.de/ascii/' (font: "banner3-D", width: 120)
            - 'https://www.askapache.com/online-tools/figlet-ascii/'.
    """

    def __validate(self, version: str) -> None:
        
        """Validates the provided 'version'."""

        if not version or not version.strip():
            raise ValueError(_MessageCollection.provided_version_empty_whitespace())
    def __create_figlet(self) -> tuple:
        
        """Returns a tuple containing the figlet and its width."""
        
        lines : list[str] = [
            "'##::: ##:'##:::::'##::'######:::::'###::::'##::::'##::'######:::",
            " ###:: ##: ##:'##: ##:'##... ##:::'## ##::: ##:::: ##:'##... ##::",
            " ####: ##: ##: ##: ##: ##:::..:::'##:. ##:: ##:::: ##: ##:::..:::",
            " ## ## ##: ##: ##: ##: ##:::::::'##:::. ##: ##:::: ##: ##::'####:",
            " ##. ####: ##: ##: ##: ##::::::: #########:. ##:: ##:: ##::: ##::",
            " ##:. ###: ##: ##: ##: ##::: ##: ##.... ##::. ## ##::: ##::: ##::",
            " ##::. ##:. ###. ###::. ######:: ##:::: ##:::. ###::::. ######:::",
            "..::::..:::...::...::::......:::..:::::..:::::...::::::......::::"
        ]

        return (os.linesep.join(lines), len(lines[0]))
    def __create_frame(self, version: str, max_length: int) -> tuple:
        
        """Returns a tuple containing the frame of the figlet."""
        
        version_token : str = f"Version: {version}"
        
        margin_length : int = 5
        total_length : int = max_length - len(version_token) - margin_length

        top_line : str = "*" * max_length
        bottom_line : str = f"{top_line[:total_length]}{version_token}{'*' * margin_length}"

        return (top_line, bottom_line)

    def create_standard(self, version : str) -> str:
        
        """Creates the standard ASCII banner."""
        
        self.__validate(version)

        figlet, max_length = self.__create_figlet()
        top_line, bottom_line = self.__create_frame(version, max_length)

        ascii_banner : str = os.linesep.join([
            top_line,
            figlet,
            bottom_line,
            ""
        ])

        return ascii_banner
    def create_mini(self, version : str) -> str:

        """
            Creates the mini ASCII banner:
            
                *****************
                * NWCAVG v1.0.0 *
                *****************
        """

        self.__validate(version)

        assembly_name : str = "NWCAVG"
        middle_line : str = f"* {assembly_name} v{version} *"
        
        top_line : str = "*" * len(middle_line)
        bottom_line : str = top_line

        ascii_banner : str = os.linesep.join([
            top_line,
            middle_line,
            bottom_line,
            ""
        ])

        return ascii_banner
    def create(self, version : str, terminal_width : int) -> str:

        """Creates either a standard or mini ASCII banner depending on the terminal width."""
        
        _, max_length = self.__create_figlet()

        if max_length <= terminal_width:
            return self.create_standard(version)
        else:
            return self.create_mini(version)
class TerminalWindowManager:

    '''Handles terminal window size.'''

    __shutil_width_function : Callable[[], Optional[int]]
    __stty_width_function : Callable[[], Optional[int]]

    cutoff_width : Final[int] = 70

    @staticmethod
    def default_shutil_width_function() -> Optional[int]:

        """Get terminal width using shutil (multi-platform)."""

        try:

            terminal_width : int = get_terminal_size().columns

            return terminal_width
        
        except:
            return None

    @staticmethod
    def default_stty_width_function() -> Optional[int]:

        """Get terminal width using stty command (Linux)."""

        try:

            process : CompletedProcess[str] = subprocess.run(
                ["/bin/sh", "-c", "stty size | cut -d' ' -f2"],
                capture_output = True,
                text = True,
                check = False,
            )

            stty_output : str = process.stdout.strip()
            terminal_width : int = int(stty_output)

            if terminal_width >= 0:
                return terminal_width

            return None
        except:
            return None

    def __init__(
        self,
        shutil_width_function : Optional[Callable[[], Optional[int]]] = None,
        stty_width_function : Optional[Callable[[], Optional[int]]] = None,
    ) -> None:
        
        if shutil_width_function is None:
            shutil_width_function = self.default_shutil_width_function
        
        if stty_width_function is None:
            stty_width_function = self.default_stty_width_function

        self.__shutil_width_function = shutil_width_function
        self.__stty_width_function = stty_width_function

    def get_or_cutoff(self) -> int:

        terminal_width : Optional[int] = self.__shutil_width_function()

        if terminal_width is None:
            terminal_width = self.__stty_width_function()

        if terminal_width is None:
            terminal_width = self.cutoff_width

        return terminal_width
class APFactory():

    '''Encapsulates all the logic related to the creation of a custom instance of argparse.ArgumentParser.'''

    def create(self) -> ArgumentParser:

        '''Creates a custom instance of argparse.ArgumentParser.'''

        argument_parser : ArgumentParser = ArgumentParser(prog = CLI_NAME, description = CLI_DESCRIPTION)

        argument_parser.add_argument(
            *CLISTRING.OPTION_FOLDERPATH_FLAGS, 
            required = CLISTRING.OPTION_FOLDERPATH_REQUIRED, 
            help = CLISTRING.OPTION_FOLDERPATH_HELP)

        return argument_parser
class APAdapter():

    '''Customizes argparse.ArgumentParser for this use case.'''

    __ap_factory : APFactory

    def __init__(self, ap_factory : APFactory = APFactory()) -> None:
        self.__ap_factory = ap_factory

    def parse_args(self) -> Optional[str]:

        '''Parses provided arguments.'''

        parser : ArgumentParser = self.__ap_factory.create()
        args : Namespace = parser.parse_args()

        return args.folder_path
class CLIManager():

    '''Collects all the logic related to the CLI management.'''

    __ap_adapter : APAdapter
    __ca_calculator : CommitAverageCalculator
    __ascii_banner_manager : AsciiBannerManager
    __tw_manager : TerminalWindowManager
    __logging_function : Callable[[str], None]

    def __init__(
        self, 
        ap_adapter : APAdapter = APAdapter(), 
        ca_calculator : CommitAverageCalculator = CommitAverageCalculator(),
        ascii_banner_manager : AsciiBannerManager = AsciiBannerManager(),
        tw_manager : TerminalWindowManager = TerminalWindowManager(),
        logging_function : Callable[[str], None] = lambda msg : print(msg)) -> None:
        
        self.__ap_adapter = ap_adapter
        self.__ca_calculator = ca_calculator
        self.__ascii_banner_manager = ascii_banner_manager
        self.__tw_manager = tw_manager
        self.__logging_function = logging_function

    def __log_ascii_banner(self):

        """Logs the ascii banner."""

        terminal_width : int = self.__tw_manager.get_or_cutoff()
        ascii_banner : str = self.__ascii_banner_manager.create(PROJECT_VERSION, terminal_width)

        self.__logging_function("")
        self.__logging_function(ascii_banner)
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
            row[3] = str(row[3]).replace("0.00", _MessageCollection.not_enough_data())
            rows.append(row)

        table : str = tabulate(
            rows, 
            headers = [HEADER.YEARMONTH, HEADER.DAYS, HEADER.COMMITS, HEADER.DAILYAVGMIN, HEADER.REFNAMES], 
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
    def __log_folder_path(self, folder_path : Optional[str]):

        """Logs the folder_path."""

        if (folder_path):
            self.__logging_function(_MessageCollection.field_equals_to("Folder", folder_path))
        else:
            self.__logging_function(_MessageCollection.field_equals_to("Folder", str(Path.cwd())))

        self.__logging_function("")    
    def __orchestrate_logging(self, summary : Summary, log_type : Optional[Literal[LOGTYPE.TABLE, LOGTYPE.DAILY, LOGTYPE.MONTHLY]]) -> None:

        '''Orchestrate summary logging according to log_type.'''

        if log_type is None or log_type== LOGTYPE.TABLE:
            self.__log_table(monthly_statuses = summary.monthly_statuses)

        elif log_type == LOGTYPE.DAILY:
            self.__log_items(items = summary.daily_statuses)
        
        elif log_type == LOGTYPE.MONTHLY:
            self.__log_items(items = summary.monthly_statuses)
        
        else:
            raise Exception(_MessageCollection.provided_log_type_not_supported(log_type = log_type))
    
    def parse(self) -> None:

        '''Calculates the average commit value and logs the result.'''

        try:

            self.__log_ascii_banner()

            folder_path : Optional[str] = self.__ap_adapter.parse_args()
            log_type : Optional[Literal[LOGTYPE.TABLE, LOGTYPE.DAILY, LOGTYPE.MONTHLY]] = LOGTYPE.TABLE

            self.__log_folder_path(folder_path = folder_path)

            summary : Summary = self.__ca_calculator.run(folder_path = folder_path)
            self.__orchestrate_logging(summary = summary, log_type = log_type)

        except Exception as e:

            self.__logging_function(str(e))

# MAIN
def main(): CLIManager().parse()

if __name__ == "__main__":
    main()