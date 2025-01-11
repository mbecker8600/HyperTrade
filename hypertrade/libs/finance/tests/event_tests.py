import unittest
from datetime import datetime
from unittest.mock import patch
from loguru import logger
import pytz

import pandas as pd

from hypertrade.libs.finance.event import EVENT, EventManager
from hypertrade.libs.logging.setup import initialize_logging


# import hypertrade.libs.debugging  # donotcommit


class MockStrategyHandler:

    def handle_event(self, time: datetime, event: EVENT) -> None:
        pass


class MockOrderHandler:

    def handle_event(self, time: datetime, event: EVENT) -> None:
        pass


class MockPortfolioHandler:

    def handle_event(self, time: datetime, event: EVENT) -> None:
        pass


class TestEventManager(unittest.TestCase):

    def test_basic_simulation_market_events(self) -> None:
        """Test market events are properly published with no over events scheduled"""
        nytz = pytz.timezone("America/New_York")
        start_time = pd.Timestamp("2020-01-01", tz=nytz)

        # Since no time is provide, the timestamp defaults to 00:00:00, meaning this day will not be
        # included in the simulation.
        end_time = pd.Timestamp("2020-01-10", tz=nytz)
        event_manager = EventManager(start_time=start_time, end_time=end_time)

        strategy = MockStrategyHandler()
        with patch.object(
            MockStrategyHandler, "handle_event", wraps=strategy.handle_event
        ) as mock:
            event_manager.subscribe(EVENT.MARKET_OPEN, strategy)
            event_manager.subscribe(EVENT.MARKET_CLOSE, strategy)

            for time, event in event_manager:
                logger.info(f"Event: {event} at {time}")

            # There are 6 trading sessions between 2020-01-01 and 2020-01-10 (midnight)
            # therefore we should get 6 market open and 6 market close events.
            # There is a holiday on the 1st and a weekend on the 6th and 7th.
            self.assertEquals(mock.call_count, 12)


if __name__ == "__main__":
    initialize_logging(level="DEBUG")
    unittest.main()
