'''
A CLI application built around nwcommitaverages.

Alias: nwcavg
'''

# GLOBAL MODULES
import subprocess
from argparse import ArgumentParser, Namespace
from shutil import get_terminal_size
from subprocess import CompletedProcess
from typing import Callable, Final, Optional, Tuple

# LOCAL/NW MODULES
from nwcommitaverages import CommitAverageCalculator
from setupinfo import CLI_NAME, CLI_DESCRIPTION

# GENERIC CLASSES
# CONSTANTS
# STATIC CLASSES
class CLISTRING:

    '''Collects all the CLI-related strings.'''

    OPTION_FOLDERPATH_FLAGS : Final[list[str]] = ["--folder_path"]
    OPTION_FOLDERPATH_REQUIRED : Final[bool] = False
    OPTION_FOLDERPATH_HELP : Final[str] = "The path to the Git repository folder for which the average commit value is calculated."
class _MessageCollection():

    '''Collects all the messages used for logging and for the exceptions.'''

    pass    

# CLASSES
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
    __tw_manager : TerminalWindowManager

    def __init__(
        self, 
        ap_adapter : APAdapter = APAdapter(), 
        ca_calculator : CommitAverageCalculator = CommitAverageCalculator(),
        tw_manager : TerminalWindowManager = TerminalWindowManager()) -> None:
        
        self.__ap_adapter = ap_adapter
        self.__ca_calculator = ca_calculator
        self.__tw_manager = tw_manager

    def run_and_log(self) -> None:

        '''Calculates the average commit value and logs the result.'''

        folder_path : Optional[str] = self.__ap_adapter.parse_args()
        self.__ca_calculator.run_and_log(folder_path = folder_path)

# MAIN
def main(): CLIManager().run_and_log()

if __name__ == "__main__":
    main()