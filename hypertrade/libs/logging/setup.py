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
        format="<green>{time:YYYY-MM-DD HH:mm:ss} | <b>{extra[simulation_time]}</></> | <level> {level:7s} </> | {name}:{line} | <cyan> {message}</>",
        level=level,
        colorize=colorize,
    )
    logger.configure(extra={"simulation_time": None})
    logger.level("TRACE", color="<light-blue>")
    logger.level("DEBUG", color="<blue>")
    logger.level("INFO", color="<white>", icon="✏️")
    logger.level("SUCCESS", color="<green>")
    logger.level("WARNING", color="<yellow>")
    logger.level("ERROR", color="<light-red>")
    logger.level("CRITICAL", color="<RED><bold>")
    logger.info("Logging setup complete")
