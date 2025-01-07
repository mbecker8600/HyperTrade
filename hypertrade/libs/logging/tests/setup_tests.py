
import unittest

from hypertrade.libs.logging.setup import initialize_logging
from loguru import logger


class TestPythonLoggingSetup(unittest.TestCase):

    def test_initalization(self) -> None:
        initialize_logging()
        logger.info("Logging setup complete")
        print("test")
