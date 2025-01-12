"""setup.py: Setup the logger for the project.

This module will setup the logger for the project. It will use the loguru library to setup the logger.
It should be called at the beginning of the project to setup the logger within the main function.

"""

from loguru import logger
import sys

SIMULATION_TIME_KEY: str = "simulation_time"


def initialize_logging(level: str = "INFO", colorize: bool = True) -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level:7s} | {name}:{line} | {message}",
        level=level,
        colorize=colorize,
    )
    logger.info("Logging setup complete")
