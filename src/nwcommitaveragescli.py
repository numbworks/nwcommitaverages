'''
A CLI application built around nwcommitaverages.

Alias: nwcavg
'''

# GLOBAL MODULES
from argparse import ArgumentParser, Namespace
from typing import Literal, Optional, Tuple

# LOCAL/NW MODULES
from nwcommitaverages import CommitAverageCalculator, LOGTYPE

# GENERIC CLASSES
# CONSTANTS
# STATIC CLASSES
class _MessageCollectionAPFactory():

    '''Collects all the messages used for logging and for the exceptions.'''

    @staticmethod
    def parser_description() -> str:
        return "Calculates the average commit value and logs the result."
    @staticmethod
    def parser_file_path() -> str:
        return "The file path to the Git repository for which the average commit value is calculated."
    @staticmethod
    def parser_logtype() -> str:
        return f"The type of log ('{LOGTYPE.TABLE}' for a tabular overview, '{LOGTYPE.DAILY}' and '{LOGTYPE.MONTHLY}' for a list of statuses). The default is '{LOGTYPE.TABLE}'."
class _MessageCollection(
    _MessageCollectionAPFactory):

    '''Collects all the messages used for logging and for the exceptions.'''

    pass    

# CLASSES
class APFactory():

    '''Encapsulates all the logic related to the creation of a custom instance of argparse.ArgumentParser.'''

    def create(self) -> ArgumentParser:

        '''Creates a custom instance of argparse.ArgumentParser.'''

        argument_parser : ArgumentParser = ArgumentParser(description = _MessageCollection.parser_description())
        argument_parser.add_argument("--file_path", "-fp", required = False, help = _MessageCollection.parser_file_path())
        argument_parser.add_argument("--logtype", "-lt", required = False, choices = [f"{LOGTYPE.TABLE}", f"{LOGTYPE.DAILY}", f"{LOGTYPE.MONTHLY}"], help = _MessageCollection.parser_logtype())

        return argument_parser
class APAdapter():

    '''Customizes argparse.ArgumentParser for this use case.'''

    __ap_factory : APFactory

    def __init__(self, ap_factory : APFactory = APFactory()) -> None:
        self.__ap_factory = ap_factory

    def parse_args(self) -> Tuple[Optional[str], Optional[Literal[LOGTYPE.TABLE, LOGTYPE.DAILY, LOGTYPE.MONTHLY]]]:

        '''Parses provided arguments.'''

        parser : ArgumentParser = self.__ap_factory.create()
        args : Namespace = parser.parse_args()

        return (args.file_path, args.logtype)
class CLIManager():

    '''Collects all the logic related to the CLI management.'''

    __ap_adapter : APAdapter
    __ca_calculator : CommitAverageCalculator

    def __init__(
        self, 
        ap_adapter : APAdapter = APAdapter(), 
        ca_calculator : CommitAverageCalculator = CommitAverageCalculator()) -> None:
        
        self.__ap_adapter = ap_adapter
        self.__ca_calculator = ca_calculator

    def run_and_log(self) -> None:

        '''Calculates the average commit value and logs the result.'''

        file_path, log_type = self.__ap_adapter.parse_args()
        self.__ca_calculator.run_and_log(file_path = file_path, log_type = log_type)

# MAIN
if __name__ == "__main__":
    CLIManager().run_and_log()