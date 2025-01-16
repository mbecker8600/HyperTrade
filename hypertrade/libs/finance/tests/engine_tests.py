import unittest

import pandas as pd
from loguru import logger
import pytz


from hypertrade.libs.finance.engine import TradingEngine
from hypertrade.libs.logging.setup import initialize_logging


class TestTradingEngine(unittest.TestCase):

    def test_engine(self) -> None:
        nytz = pytz.timezone("America/New_York")
        start_time = pd.Timestamp("2020-01-01", tz=nytz)

        # Since no time is provide, the timestamp defaults to 00:00:00, meaning this day will not be
        # included in the simulation.
        end_time = pd.Timestamp("2020-01-10", tz=nytz)
        engine = TradingEngine(
            start_time=start_time, end_time=end_time, capital_base=1000
        )
        engine.run()


if __name__ == "__main__":
    initialize_logging(level="DEBUG")
    unittest.main()
