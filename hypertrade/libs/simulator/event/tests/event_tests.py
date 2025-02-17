import unittest
from collections import Counter
from dataclasses import dataclass
from datetime import timedelta
from typing import Generic, TypeVar
from unittest.mock import patch

import pandas as pd
import pytz
from loguru import logger

from hypertrade.libs.logging.setup import initialize_logging
from hypertrade.libs.service.locator import ServiceLocator
from hypertrade.libs.simulator.event.service import EventManager
from hypertrade.libs.simulator.event.types import EVENT_TYPE, Event
from hypertrade.libs.tsfd.utils.time import cast_timestamp

# import hypertrade.libs.debugging  # donotcommit

T = TypeVar("T")


class MockNoEventPublishHandler(Generic[T]):

    def handle_event(self, event: Event[T]) -> None:
        pass


@dataclass
class OrderPlacedData:
    symbol: str
    amount: int


class MockStrategyHandler:

    def handle_event(self, event: Event[None]) -> None:
        service_locator = ServiceLocator[EventManager]()
        event_manager = service_locator.get(EventManager.SERVICE_NAME)
        event_manager.schedule_event(
            Event[OrderPlacedData](
                event_type=EVENT_TYPE.ORDER_PLACED,
                payload=OrderPlacedData("GOOGL", 10),
            )
        )


class MockOrderHandler:

    def handle_event(self, event: Event[OrderPlacedData]) -> None:
        service_locator = ServiceLocator[EventManager]()
        event_manager = service_locator.get(EventManager.SERVICE_NAME)
        event_manager.schedule_event(
            Event[None](event_type=EVENT_TYPE.ORDER_FULFILLED),
            delay=timedelta(seconds=3),
        )


class MockPortfolioHandler:

    def handle_event(self, event: Event[OrderPlacedData]) -> None:
        service_locator = ServiceLocator[EventManager]()
        event_manager = service_locator.get(EventManager.SERVICE_NAME)
        event_manager.schedule_event(
            Event[None](event_type=EVENT_TYPE.PORTFOLIO_UPDATE),
            delay=timedelta(seconds=1),
        )


class TestEventManager(unittest.TestCase):

    def test_basic_simulation_market_events(self) -> None:
        """Test market events are properly published with no over events scheduled"""
        nytz = pytz.timezone("America/New_York")
        start_time = cast_timestamp(pd.Timestamp("2020-01-01", tz=nytz))

        # Since no time is provide, the timestamp defaults to 00:00:00, meaning this day will not be
        # included in the simulation.
        end_time = cast_timestamp(pd.Timestamp("2020-01-10", tz=nytz))
        event_manager = EventManager(start_time=start_time, end_time=end_time)

        no_event_handler = MockNoEventPublishHandler[None]()
        with patch.object(
            MockNoEventPublishHandler,
            "handle_event",
            wraps=no_event_handler.handle_event,
        ) as mock:
            event_manager.subscribe(
                EVENT_TYPE.MARKET_OPEN, no_event_handler.handle_event
            )
            event_manager.subscribe(
                EVENT_TYPE.MARKET_CLOSE, no_event_handler.handle_event
            )

            for event in event_manager:
                logger.info(f"Event: {event.event_type} at {event.time}")

            # There are 6 trading sessions between 2020-01-01 and 2020-01-10 (midnight)
            # therefore we should get 6 market open and 6 market close events.
            # There is a holiday on the 1st and a weekend on the 6th and 7th.
            self.assertEqual(mock.call_count, 12)
            event_counter = Counter(
                args[0][0].event_type for args in mock.call_args_list
            )
            self.assertEqual(event_counter[EVENT_TYPE.MARKET_OPEN], 6)
            self.assertEqual(event_counter[EVENT_TYPE.MARKET_CLOSE], 6)

    def test_simulation_with_scheduled_events(self) -> None:
        """Test scheduled events are properly published"""
        nytz = pytz.timezone("America/New_York")
        start_time = cast_timestamp(pd.Timestamp("2020-01-02", tz=nytz))
        end_time = cast_timestamp(pd.Timestamp("2020-01-03", tz=nytz))

        event_manager = EventManager(start_time=start_time, end_time=end_time)
        strategy_handler = MockStrategyHandler()
        with patch.object(
            MockStrategyHandler,
            "handle_event",
            wraps=strategy_handler.handle_event,
        ) as mock:
            event_manager.subscribe(
                EVENT_TYPE.MARKET_OPEN, strategy_handler.handle_event
            )

            # First event is market open
            market_open_event = next(event_manager)
            self.assertEqual(market_open_event.event_type, EVENT_TYPE.MARKET_OPEN)
            self.assertEqual(
                market_open_event.time, pd.Timestamp("2020-01-02 09:30", tz=nytz)
            )

            # Second event is from the strategy handler, no delay so time is the same
            order_placed_event = next(event_manager)
            self.assertEqual(order_placed_event.event_type, EVENT_TYPE.ORDER_PLACED)
            self.assertEqual(
                order_placed_event.time, pd.Timestamp("2020-01-02 09:30", tz=nytz)
            )

            # Third event is market close
            market_close_event = next(event_manager)
            self.assertEqual(market_close_event.event_type, EVENT_TYPE.MARKET_CLOSE)
            self.assertEqual(
                market_close_event.time, pd.Timestamp("2020-01-02 16:00", tz=nytz)
            )

            mock.assert_called_once()

    def test_simulation_with_chained_events(self) -> None:
        """Test scheduled events are properly published"""
        nytz = pytz.timezone("America/New_York")
        start_time = cast_timestamp(pd.Timestamp("2020-01-02", tz=nytz))
        end_time = cast_timestamp(pd.Timestamp("2020-01-03", tz=nytz))

        event_manager = EventManager(start_time=start_time, end_time=end_time)
        strategy_handler = MockStrategyHandler()
        order_handler = MockOrderHandler()
        with patch.object(
            MockStrategyHandler,
            "handle_event",
            wraps=strategy_handler.handle_event,
        ) as mock_strategy_handler, patch.object(
            MockOrderHandler,
            "handle_event",
            wraps=order_handler.handle_event,
        ) as mock_order_handler:
            event_manager.subscribe(
                EVENT_TYPE.MARKET_OPEN, strategy_handler.handle_event
            )
            event_manager.subscribe(EVENT_TYPE.ORDER_PLACED, order_handler.handle_event)

            # First event is market open
            market_open_event = next(event_manager)
            self.assertEqual(market_open_event.event_type, EVENT_TYPE.MARKET_OPEN)
            self.assertEqual(
                market_open_event.time, pd.Timestamp("2020-01-02 09:30", tz=nytz)
            )

            # Second event is from the strategy handler, no delay so time is the same
            order_placed_event = next(event_manager)
            self.assertEqual(order_placed_event.event_type, EVENT_TYPE.ORDER_PLACED)
            self.assertEqual(
                order_placed_event.time, pd.Timestamp("2020-01-02 09:30", tz=nytz)
            )

            # Third event is from the strategy handler, no delay so time is the same
            order_placed_event = next(event_manager)
            self.assertEqual(order_placed_event.event_type, EVENT_TYPE.ORDER_FULFILLED)
            self.assertEqual(
                order_placed_event.time, pd.Timestamp("2020-01-02 09:30:03", tz=nytz)
            )

            # Fourth event is market close
            market_close_event = next(event_manager)
            self.assertEqual(market_close_event.event_type, EVENT_TYPE.MARKET_CLOSE)
            self.assertEqual(
                market_close_event.time, pd.Timestamp("2020-01-02 16:00", tz=nytz)
            )

            mock_strategy_handler.assert_called_once()
            mock_order_handler.assert_called_once()

    def test_simulation_with_unordered_publishing(self) -> None:
        """Test scheduled events with longer delay are not scheduled before shorter delay"""
        nytz = pytz.timezone("America/New_York")
        start_time = cast_timestamp(pd.Timestamp("2020-01-02", tz=nytz))
        end_time = cast_timestamp(pd.Timestamp("2020-01-03", tz=nytz))

        event_manager = EventManager(start_time=start_time, end_time=end_time)
        strategy_handler = MockStrategyHandler()
        order_handler = MockOrderHandler()
        portfolio_handler = MockPortfolioHandler()
        with patch.object(
            MockStrategyHandler,
            "handle_event",
            wraps=strategy_handler.handle_event,
        ) as mock_strategy_handler, patch.object(
            MockOrderHandler,
            "handle_event",
            wraps=order_handler.handle_event,
        ) as mock_order_handler, patch.object(
            MockPortfolioHandler,
            "handle_event",
            wraps=portfolio_handler.handle_event,
        ) as mock_portfolio_handler:
            event_manager.subscribe(
                EVENT_TYPE.MARKET_OPEN, strategy_handler.handle_event
            )

            # Since the order handler is subscribed first, but delays for multiple seconds
            # this should ensure that the proper event processing based on timestamps
            # is happening
            event_manager.subscribe(EVENT_TYPE.ORDER_PLACED, order_handler.handle_event)
            event_manager.subscribe(
                EVENT_TYPE.ORDER_PLACED, portfolio_handler.handle_event
            )

            # First event is market open
            market_open_event = next(event_manager)
            self.assertEqual(market_open_event.event_type, EVENT_TYPE.MARKET_OPEN)
            self.assertEqual(
                market_open_event.time, pd.Timestamp("2020-01-02 09:30", tz=nytz)
            )

            # Second event is from the strategy handler, no delay so time is the same
            order_placed_event = next(event_manager)
            self.assertEqual(order_placed_event.event_type, EVENT_TYPE.ORDER_PLACED)
            self.assertEqual(
                order_placed_event.time, pd.Timestamp("2020-01-02 09:30", tz=nytz)
            )

            # Third event is from the portfolio handler, since it only has a delay of 1
            port_update_event = next(event_manager)
            self.assertEqual(port_update_event.event_type, EVENT_TYPE.PORTFOLIO_UPDATE)
            self.assertEqual(
                port_update_event.time, pd.Timestamp("2020-01-02 09:30:01", tz=nytz)
            )

            # Fourth event is from the order handler, since it has a delay of 3
            order_placed_event = next(event_manager)
            self.assertEqual(order_placed_event.event_type, EVENT_TYPE.ORDER_FULFILLED)
            self.assertEqual(
                order_placed_event.time, pd.Timestamp("2020-01-02 09:30:03", tz=nytz)
            )

            # Last event is market close
            market_close_event = next(event_manager)
            self.assertEqual(market_close_event.event_type, EVENT_TYPE.MARKET_CLOSE)
            self.assertEqual(
                market_close_event.time, pd.Timestamp("2020-01-02 16:00", tz=nytz)
            )

            mock_strategy_handler.assert_called_once()
            mock_order_handler.assert_called_once()
            mock_portfolio_handler.assert_called_once()

    def test_simulation_bad_subscriber_fn(self) -> None:
        """Test failure occurs when someone subscribes a function to a publish event with mismatching data object"""
        nytz = pytz.timezone("America/New_York")
        start_time = cast_timestamp(pd.Timestamp("2020-01-02", tz=nytz))
        end_time = cast_timestamp(pd.Timestamp("2020-01-03", tz=nytz))

        event_manager = EventManager(start_time=start_time, end_time=end_time)
        order_handler = MockOrderHandler()

        with patch.object(
            MockOrderHandler,
            "handle_event",
            wraps=order_handler.handle_event,
        ):
            # the OrderHandler.handle_event expects an OrderPlacedData object to be passed, but
            # the EVENT_TYPE.MARKET_OPEN doesn't pass any data
            event_manager.subscribe(EVENT_TYPE.MARKET_OPEN, order_handler.handle_event)

            # First event is market open
            market_open_event = next(event_manager)
            self.assertEqual(market_open_event.event_type, EVENT_TYPE.MARKET_OPEN)
            self.assertEqual(
                market_open_event.time, pd.Timestamp("2020-01-02 09:30", tz=nytz)
            )

    # TODO: Add tests for improper start/end dates

    # TODO: Add test for various timezones


if __name__ == "__main__":
    initialize_logging(level="DEBUG")
    unittest.main()
