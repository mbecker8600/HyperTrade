"""setup.py: Setup the logger for the project.

This module will setup the logger for the project. It will use the loguru library to setup the logger.
It should be called at the beginning of the project to setup the logger within the main function.

"""

from loguru import logger
import sys


def setup_logging(level: str = "INFO", colorize: bool = True) -> None:
    logger.add(
        sys.stderr, format="{time} {level} {message}", filter="my_module", level=level, colorize=colorize)
