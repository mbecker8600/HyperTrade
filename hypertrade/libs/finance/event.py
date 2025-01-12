from __future__ import annotations
import datetime
import heapq
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    runtime_checkable,
)
from pandas import Timestamp
import exchange_calendars as xcals

import enum
from loguru import logger
import pytz

from hypertrade.libs.service.locator import ServiceLocator

import os

if TYPE_CHECKING:
    from loguru import Record


class Frequency(enum.Enum):
    DAILY = 1


class EVENT(enum.Enum):
    MARKET_OPEN = 1
    MARKET_CLOSE = 2
    ORDER_PLACED = 3
    ORDER_FULFILLED = 4
    PORTFOLIO_UPDATE = 5


@runtime_checkable
class SupportsEventHandling(Protocol):
    def handle_event(self, time: datetime.datetime, event: EVENT) -> None: ...


EventHandlerFn = Callable[[datetime.datetime, EVENT], None]


class MarketEvents:
    """Handles market events and provides the next market event after a given time."""

    def __init__(
        self,
        exchange: str = "XNYS",
        frequency: Frequency = Frequency.DAILY,
        tz: str = "America/New_York",
    ) -> None:
        """
        Args:
            exchange (ExchangeCalendar string): The exchange to get the calendar for.
            frequency (Frequency): The frequency of the market events.
            tz (pytz.timezone string): The timezone to use for the market events.

        Raises:
            ValueError
                If `start` is earlier than the earliest supported start date.
                If `end` is later than the latest supported end date.
                If `start` parses to a later date than `end`.
            xcals.errors.InvalidCalendarName
                If name does not represent a registered calendar.
        """
        self.calendar: xcals.ExchangeCalendar = xcals.get_calendar(exchange)
        self.frequency = frequency
        self.tz = pytz.timezone(tz)

    def next_market_event(self, time: Timestamp) -> Tuple[Timestamp, EVENT]:
        """
        Returns the next market event after the given time.
        """
        if self.frequency == Frequency.DAILY:
            if time.time() < datetime.time(9, 30, tzinfo=self.tz):
                return (
                    self.calendar.next_open(time).tz_convert(self.tz),
                    EVENT.MARKET_OPEN,
                )
            elif time.time() < datetime.time(16, 0, tzinfo=self.tz):
                return (
                    self.calendar.next_close(time).tz_convert(self.tz),
                    EVENT.MARKET_CLOSE,
                )
            else:
                return (
                    self.calendar.next_open(time).tz_convert(self.tz),
                    EVENT.MARKET_OPEN,
                )


class EventManager:
    """Handles event creation, scheduling (with timestamps), and dispatching to subscribers"""

    SERVICE_NAME = "event_manager"

    def __init__(
        self,
        start_time: Timestamp,
        end_time: Timestamp,
        exchange: str = "XNYS",
        frequency: Frequency = Frequency.DAILY,
        tz: str = "America/New_York",
        event_log_dir: str = "/tmp/logs/hypertrade/events",
    ) -> None:
        """Initialize the event manager.

        Args:
            start_time (pd.Timestamp): The start time of the simulation.
            end_time (pd.Timestamp): The end time of the simulation.
                NOTE: If no time is provided, the timestamp defaults to 00:00:00, meaning this
                day will not be included in the simulation.
            frequency (Frequency): The frequency of the market events.

        Raises:
            ValueError
                If `start` is earlier than the earliest supported start date.
                If `end` is later than the latest supported end date.
                If `start` parses to a later date than `end`.
            xcals.errors.InvalidCalendarName
                If name does not represent a registered calendar.

        """
        # public attributes
        self.current_time = start_time
        self.end_time = end_time

        # private attributes
        self._subscribers: Dict[EVENT, List[EventHandlerFn]] = {
            EVENT.ORDER_FULFILLED: []
        }
        self._market_events = MarketEvents(
            exchange=exchange, frequency=frequency, tz=tz
        )
        self._event_queue: List[Tuple[datetime.datetime, EVENT]] = []

        # Register the event manager as a service
        self._service_locator = ServiceLocator[EventManager]()
        self._service_locator.register(EventManager.SERVICE_NAME, self)

        self._configure_event_logging(event_log_dir=event_log_dir)

    def _format_with_sim_time(self, record: Record) -> str:
        """
        Custom formatter function to add simulation time.
        """
        sim_time = self.current_time
        formatted_time = sim_time.strftime("%Y-%m-%d %H:%M:%S")
        return "{time} - SimTime: {sim_time} - {level:7s} - {message}\n".format(
            time=record["time"].strftime("%Y-%m-%d %H:%M:%S"),
            sim_time=formatted_time,
            level=record["level"].name,
            message=record["message"],
        )

    def _filter_event_logs(self, record: Record) -> bool:
        """
        Filter function to include only event logs.
        """
        return "event" in record["extra"]  # Check for "event" key in record["extra"]

    def _configure_event_logging(self, event_log_dir: str) -> None:
        """
        Configures a separate handler for the event logging in a separate location.
        """

        # Configure Loguru
        logger.add(
            os.path.join(event_log_dir, "events.log"),
            format=self._format_with_sim_time,
            filter=self._filter_event_logs,  # Add the filter
        )

    def subscribe(
        self, event: EVENT, subscriber: SupportsEventHandling | EventHandlerFn
    ) -> None:
        """
        Subscribes a component to a specific event type.

        Args:
            event (EVENT): The event to subscribe to.
            subscriber (SupportsEventHandling | EventHandlerFn): The component to subscribe.
                This can either be a class that implements the SupportsEventHandling protocol
                (i.e. has a handle_event method) or a function that takes a time and event as
                arguments. See SupportsEventHandling and EventHandlerFn for the method signature.
        """
        logger.bind(event=True).info(f"Subscribing {subscriber} to {event}")
        if event not in self._subscribers:
            self._subscribers[event] = []

        if isinstance(subscriber, SupportsEventHandling):
            self._subscribers[event].append(subscriber.handle_event)
        else:
            self._subscribers[event].append(subscriber)

    def _publish(self, time: datetime.datetime, event: EVENT) -> None:
        """
        Publishes an event to all subscribers of that event type.
        """

        logger.bind(event=True).info(f"Publishing {event} at {time}")
        if event in self._subscribers:
            for subscriber in self._subscribers[event]:
                logger.bind(event=True).info(f"Dispatching {event} to {subscriber}")
                subscriber(time, event)

    def schedule_event(
        self, event: EVENT, delay: Optional[datetime.timedelta] = None
    ) -> None:
        """
        Schedules an event to be published after a delay.
        """
        event_time = self.current_time + delay if delay else self.current_time
        heapq.heappush(self._event_queue, (event_time, event))

    def __iter__(self) -> EventManager:
        return self

    def _update_current_time(self, time: Timestamp) -> None:
        self.current_time = time
        logger.bind(event=True).info(f"Current Time: {time}")

    def __next__(self) -> Tuple[Timestamp, EVENT]:

        # Get the next market event and time to see if any schedule events need to be run
        # before it.
        market_event_time, market_event = self._market_events.next_market_event(
            self.current_time
        )

        # Drain event queue if there are events scheduled and it's time to handle them
        if self._event_queue and self._event_queue[0][0] <= market_event_time:
            event_time, event = heapq.heappop(self._event_queue)
            # advance time to the next event time
            self._update_current_time(event_time)
            self._publish(event_time, event)
            return event_time, event

        # If the next market event is after the end time, end the simulation
        if market_event_time > self.end_time:
            raise StopIteration

        # If there are no scheduled events that can be run, look for next market event
        # and advance time to that event
        # advance time to the next market event
        self._update_current_time(market_event_time)
        self._publish(market_event_time, market_event)
        return market_event_time, market_event
