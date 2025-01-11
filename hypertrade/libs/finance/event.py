from __future__ import annotations
from datetime import datetime, timedelta
import heapq
from typing import Dict, List, Optional, Protocol, Tuple

import enum
from loguru import logger


class Frequency(enum.Enum):
    DAILY = 1


class EVENT(enum.Enum):
    MARKET_OPEN = 1
    MARKET_CLOSE = 2
    PLACE_ORDER = 3
    ORDER_FULLFILLED = 4


class SupportsEventHandling(Protocol):
    def handle_event(self, time: datetime, event: EVENT) -> None:
        ...


class MarketEvents():
    def __init__(self, start_time: datetime, end_time: datetime, frequency: Frequency = Frequency.DAILY) -> None:
        self.start_time = start_time
        self.current_time = start_time
        self.end_time = end_time
        self.frequency = frequency

    def __iter__(self) -> MarketEvents:
        return self

    def __next__(self) -> EVENT:
        self.current_time += timedelta(hours=24)
        if self.current_time < self.end_time:
            return EVENT.MARKET_OPEN
        raise StopIteration


class EventManager():
    """Handles event creation, scheduling (with timestamps), and dispatching to subscribers"""

    def __init__(self, start_time: datetime, end_time: datetime, frequency: Frequency = Frequency.DAILY) -> None:
        self.subscribers: Dict[EVENT, List[SupportsEventHandling]] = {}
        self.current_time = start_time
        self.market_events = MarketEvents(start_time, end_time, frequency)
        self.event_queue: List[Tuple[datetime, EVENT]] = []

    def subscribe(self, event: EVENT, subscriber: SupportsEventHandling) -> None:
        """
        Subscribes a component to a specific event type.
        """
        logger.debug(f"Subscribing {subscriber} to {event}")
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(subscriber)

    def publish(self, time: datetime, event: EVENT) -> None:
        """
        Publishes an event to all subscribers of that event type.
        """
        logger.debug(f"Publishing {event} at {time}")
        if event in self.subscribers:
            for subscriber in self.subscribers[event]:
                logger.debug(f"Dispatching {event} to {subscriber}")
                subscriber.handle_event(time, event)

    def schedule_event(self, event: EVENT, delay: Optional[timedelta] = None) -> None:
        """
        Schedules an event to be published after a delay.
        """
        event_time = self.current_time + delay if delay else self.current_time
        heapq.heappush(self.event_queue, (event_time, event))

    def __iter__(self) -> EventManager:
        return self

    def __next__(self) -> Tuple[EVENT, datetime]:
        while self.event_queue and self.event_queue[0][0] <= self.current_time:
            event_time, event = heapq.heappop(self.event_queue)
            self.handle_event(event)

        # Publish TimeUpdated event
        self.publish_event(Event("TimeUpdated", self.current_time))

        # Advance time
        self.current_time += self.time_step
