import unittest

from loguru import logger

from hypertrade.libs.logging.setup import initialize_logging


class TestPythonLoggingSetup(unittest.TestCase):

    def test_initalization(self) -> None:
        initialize_logging()
        logger.info("Logging setup complete")
        print("test")
