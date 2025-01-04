
import unittest

from hypertrade.libs.logging.setup import setup_logging
from loguru import logger


class TestPythonLoggingSetup(unittest.TestCase):

    def test_initalization(self) -> None:
        setup_logging()
        logger.info("Logging setup complete")
        print("test")
