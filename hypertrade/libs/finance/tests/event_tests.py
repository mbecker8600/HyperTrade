import unittest
from datetime import datetime
from hypertrade.libs.finance.event import EVENT, EventManager
from hypertrade.libs.logging.setup import initialize_logging
from dateutil import tz

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

    def test_basic_simulation(self) -> None:
        """Basic initialization of the Portfolio object"""
        nyc_tz = tz.gettz("America/New_York")
        event_manager = EventManager()

        strategy = MockStrategyHandler()
        event_manager.subscribe(EVENT.MARKET_OPEN, strategy)

        # Simulate two days of trading
        market_events = [
            (datetime(2025, 1, 10, 9, 30, tzinfo=nyc_tz), EVENT.MARKET_OPEN),
            (datetime(2025, 1, 10, 16, tzinfo=nyc_tz), EVENT.MARKET_CLOSE),
            (datetime(2025, 1, 13, 9, 30, tzinfo=nyc_tz), EVENT.MARKET_OPEN),
            (datetime(2025, 1, 13, 16, tzinfo=nyc_tz), EVENT.MARKET_CLOSE),
        ]

        for time, event in market_events:
            event_manager.publish(time, event)


if __name__ == "__main__":
    initialize_logging(level="DEBUG")
    unittest.main()
