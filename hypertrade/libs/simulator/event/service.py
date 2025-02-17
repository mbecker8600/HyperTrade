from __future__ import annotations

import datetime
import heapq
import os
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    overload,
)

from loguru import logger
from pandas import Timestamp

from hypertrade.libs.service.locator import register_service
from hypertrade.libs.simulator.event.market import MarketEvents
from hypertrade.libs.simulator.event.types import EVENT_TYPE, Event, Frequency
from hypertrade.libs.simulator.execute.types import Order, Transaction

if TYPE_CHECKING:
    from loguru import Record


EventHandlerFn = Callable[[Event[Any]], None]  # More general type for methods


EVENT_SERVICE_NAME = "event_manager"


@register_service(EVENT_SERVICE_NAME)
class EventManager:
    """Handles event creation, scheduling (with timestamps), and dispatching to subscribers"""

    SERVICE_NAME: str = EVENT_SERVICE_NAME

    def __init__(
        self,
        start_time: Timestamp,
        end_time: Timestamp,
        exchange: str = "XNYS",
        frequency: Frequency = Frequency.DAILY,
        tz: str = "America/New_York",
        # trunk-ignore(bandit/B108)
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
        self._current_time = start_time
        self.end_time = end_time

        # private attributes
        self._subscribers: Dict[EVENT_TYPE, List[EventHandlerFn]] = {}
        self._market_events = MarketEvents(
            exchange=exchange, frequency=frequency, tz=tz
        )
        self._event_queue: List[Tuple[Timestamp, Event[Any]]] = []

        self._configure_event_logging(event_log_dir=event_log_dir)

    @property
    def current_time(self) -> Timestamp:
        return self._current_time

    def _format_with_sim_time(self, record: Record) -> str:
        """
        Custom formatter function to add simulation time.
        """
        sim_time = self._current_time
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

    @overload
    def subscribe(
        self,
        event_type: Literal[EVENT_TYPE.MARKET_OPEN],
        subscriber: Callable[[Event[None]], None],
    ) -> None: ...
    @overload
    def subscribe(
        self,
        event_type: Literal[EVENT_TYPE.MARKET_CLOSE],
        subscriber: Callable[[Event[None]], None],
    ) -> None: ...
    @overload
    def subscribe(
        self,
        event_type: Literal[EVENT_TYPE.ORDER_PLACED],
        subscriber: Callable[[Event[Order]], None],
    ) -> None: ...
    @overload
    def subscribe(
        self,
        event_type: Literal[EVENT_TYPE.ORDER_FULFILLED],
        subscriber: Callable[[Event[Transaction]], None],
    ) -> None: ...
    @overload
    def subscribe(
        self,
        event_type: Literal[EVENT_TYPE.PRICE_CHANGE],
        subscriber: Callable[[Event[PriceChangeData]], None],
    ) -> None: ...

    def subscribe(
        self,
        event_type: EVENT_TYPE,
        subscriber: EventHandlerFn,
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
        logger.bind(event=True, simulation_time=self.current_time).info(
            f"Subscribing {subscriber} to {event_type}"
        )
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        self._subscribers[event_type].append(subscriber)

    def _publish(self, event: Event[Any]) -> None:
        """
        Publishes an event to all subscribers of that event type.
        """

        logger.bind(event=True, simulation_time=self.current_time).debug(
            f"Publishing {event.event_type}"
        )
        if event.event_type in self._subscribers:
            for subscriber in self._subscribers[event.event_type]:
                logger.bind(event=True, simulation_time=self.current_time).trace(
                    f"Dispatching {event.event_type} to {subscriber}"
                )
                subscriber(event)

    def schedule_event(
        self, event: Event[Any], delay: Optional[datetime.timedelta] = None
    ) -> None:
        """
        Schedules an event to be published after a delay.
        """
        event_time = self._current_time + delay if delay else self._current_time
        event.time = event_time
        heapq.heappush(self._event_queue, (event_time, event))

    def __iter__(self) -> EventManager:
        return self

    def _update_current_time(self, time: Timestamp) -> None:
        if self._current_time != time:
            logger.bind(event=True, simulation_time=self.current_time).info(
                f"Advancing time from {self._current_time} --> {time}"
            )
            self._current_time = time

    def __next__(self) -> Event[Any]:

        # Get the next market event and time to see if any schedule events need to be run
        # before it.
        next_market_event: Event[Any] = self._market_events.next_market_event(
            self._current_time
        )
        if next_market_event.time is None:
            raise ValueError(
                "next_market_event came back with None time. Something went wrong"
            )
        # Drain event queue if there are events scheduled and it's time to handle them
        if self._event_queue and self._event_queue[0][0] <= next_market_event.time:
            event_time, event = heapq.heappop(self._event_queue)
            # advance time to the next event time
            self._update_current_time(event_time)
            self._publish(event)
            return event

        # If the next market event is after the end time, end the simulation
        if next_market_event.time > self.end_time:
            raise StopIteration

        # If there are no scheduled events that can be run, look for next market event
        # and advance time to that event
        # advance time to the next market event
        self._update_current_time(next_market_event.time)
        self._publish(next_market_event)
        return next_market_event
