import sys
import colorama
from enum import Enum


class Logger:
    """
    General purpose logging class.
    """

    class Level(Enum):
        SUCCESS = 0
        INFO = 1
        WARNING = 2
        ERROR = 3
        FATAL = 4

    def colorp(self, level: Level, message: str, end: str = '\n'):
        """
        # Prints color logs to the console.

        ## Parameters
        ---
        - level: int
            - The level of the log.
        - message: str
            - The message to be printed.
        - end: str
            - The end character to be used when printing the message.
        
        ## Returns
        ---
        - None

        ## Raises
        ---
        - ValueError
            - If the level is not between 0-4.
        
        ## Example
        ---
        ```py
        from utils.logging import Logger

        logger = Logger()

        logger.colorp(Logger.Level.SUCCESS, "This is a success message.")
        ```
        """

        colorama.init()

        levels = {
            Logger.Level.SUCCESS: colorama.Fore.GREEN,
            Logger.Level.INFO: colorama.Fore.BLUE,
            Logger.Level.WARNING: colorama.Fore.YELLOW,
            Logger.Level.ERROR: colorama.Fore.RED,
            Logger.Level.FATAL: colorama.Fore.RED + colorama.Style.BRIGHT
        }

        if level not in levels:
            raise ValueError("The level must be between 0-4.")

        print(f"[{levels[level]}{level.name.upper()}{colorama.Style.RESET_ALL}]{' ' * (10 - len(level.name))}{message}{colorama.Style.RESET_ALL}", end=end)

        if level == Logger.Level.FATAL:
            sys.exit(1)