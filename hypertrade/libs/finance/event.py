from __future__ import annotations
import datetime
import heapq
from typing import Dict, List, Optional, Protocol, Tuple
from pandas import Timestamp
import exchange_calendars as xcals

import enum
from loguru import logger
import pytz


class Frequency(enum.Enum):
    DAILY = 1


class EVENT(enum.Enum):
    MARKET_OPEN = 1
    MARKET_CLOSE = 2
    PLACE_ORDER = 3
    ORDER_FULLFILLED = 4


class SupportsEventHandling(Protocol):
    def handle_event(self, time: datetime.datetime, event: EVENT) -> None: ...


class MarketEvents:
    """Handles market events and provides the next market event after a given time."""

    def __init__(
        self,
        start_time: Timestamp,
        end_time: Timestamp,
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
        self.calendar: xcals.ExchangeCalendar = xcals.get_calendar(
            exchange, start=start_time, end=end_time
        )
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

    def __init__(
        self,
        start_time: Timestamp,
        end_time: Timestamp,
        exchange: str = "XNYS",
        frequency: Frequency = Frequency.DAILY,
        tz: str = "America/New_York",
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
        self.subscribers: Dict[EVENT, List[SupportsEventHandling]] = {}
        self.current_time = start_time
        self.end_time = end_time
        self.market_events = MarketEvents(start_time, end_time, frequency=frequency)
        self.event_queue: List[Tuple[datetime.datetime, EVENT]] = []

    def subscribe(self, event: EVENT, subscriber: SupportsEventHandling) -> None:
        """
        Subscribes a component to a specific event type.
        """
        logger.debug(f"Subscribing {subscriber} to {event}")
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(subscriber)

    def _publish(self, time: datetime.datetime, event: EVENT) -> None:
        """
        Publishes an event to all subscribers of that event type.
        """
        logger.debug(f"Publishing {event} at {time}")
        if event in self.subscribers:
            for subscriber in self.subscribers[event]:
                logger.debug(f"Dispatching {event} to {subscriber}")
                subscriber.handle_event(time, event)

    def schedule_event(
        self, event: EVENT, delay: Optional[datetime.timedelta] = None
    ) -> None:
        """
        Schedules an event to be published after a delay.
        """
        event_time = self.current_time + delay if delay else self.current_time
        heapq.heappush(self.event_queue, (event_time, event))

    def __iter__(self) -> EventManager:
        return self

    def __next__(self) -> Tuple[Timestamp, EVENT]:

        # Drain event queue if there are events scheduled and it's time to handle them
        if self.event_queue and self.event_queue[0][0] <= self.current_time:
            event_time, event = heapq.heappop(self.event_queue)
            # advance time to the next event time
            self.current_time = event_time
            self._publish(event_time, event)
            return event_time, event

        # If there are no scheduled events that can be run, look for next market event
        # and advance time to that event
        event_time, event = self.market_events.next_market_event(self.current_time)

        # If the next market event is after the end time, end the simulation
        if event_time > self.end_time:
            raise StopIteration

        # advance time to the next market event
        self.current_time = event_time
        self._publish(event_time, event)
        return event_time, event
