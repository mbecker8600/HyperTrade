from __future__ import annotations

import enum
import uuid
from typing import Any, Generic, Optional, TypedDict, TypeVar

from pandas import Timestamp


class OrderPlacedData(TypedDict):
    order_id: str
    quantity: float


class PriceChangeData(TypedDict):
    # ...any fields needed...
    pass


class EVENT_TYPE(enum.Enum):
    """Registry of all events that can be subscribed to ensure easy discoveryability for anyone looking for
    Events to subscribe to.

    Each event should specify three things:
    1. what it does
    2. what class publishes it
    3. what data object should be used when handling the event. This should be type safe using generics

    Note, if the event doesn't have data (and data is Optional[T]), the typing on the event should be
    Event[None] to indicate there is no data available.

    """

    MARKET_OPEN = 1
    """MARKET_OPEN
    Description:
    Publisher: :py:class:`~hypertrade.libs.simulator.event.MarketEvents`
    Payload: None
    """
    MARKET_CLOSE = 2
    """MARKET_CLOSE
    Description:
    Publisher: :py:class:`~hypertrade.libs.simulator.event.MarketEvents`
    Payload: None
    """
    ORDER_PLACED = 3
    """ORDER_PLACED
    Description:
    Publisher:
    Payload:
    """
    ORDER_FULFILLED = 4
    """ORDER_FULFILLED
    Description:
    Publisher:
    Payload:
    """
    PORTFOLIO_UPDATE = 5
    """PORTFOLIO_UPDATE
    Description:
    Publisher:
    Payload:
    """
    PRICE_CHANGE = 6
    """PRICE_CHANGE
    Description:
    Publisher:
    Payload:
    """


T = TypeVar("T")


class Event(Generic[T]):
    """
    Type-safe event with generic payload.
    """

    def __init__(
        self,
        event_type: EVENT_TYPE,
        time: Optional[Timestamp] = None,
        payload: Optional[T] = None,
    ):
        """
        Args:
            event_type (EVENT_TYPE): Type of event being scheduled
            time (pd.Timestamp): Time the event should occur
                Should be set when scheduled in the EventManager
            payload (Generic[T]): Payload passed to subscribers
        """
        self.event_type = event_type
        self.time = time
        self.payload = payload
        self.id = Event.make_id()

    @staticmethod
    def make_id() -> str:
        return uuid.uuid4().hex

    def __repr__(self) -> str:
        return (
            f"Event Type: {self.event_type}, Time: {self.time}, Payload: {self.payload}"
        )

    def __lt__(self, other: Event[Any]) -> bool:
        if isinstance(other, Event):
            return self.id < other.id
        else:
            raise ValueError(
                f"Events should only compare to other events, but {type(other)} as passed."
            )

    def __le__(self, other: Event[Any]) -> bool:
        if not isinstance(other, Event):
            raise ValueError(
                f"Events should only compare to other events, but {type(other)} as passed."
            )
        return self.id <= other.id


# @overload
# def create_event(event_type: EVENT_TYPE.MARKET_OPEN) -> Event[None]: ...
# @overload
# def create_event(
#     event_type: EVENT_TYPE.ORDER_PLACED, data: OrderPlacedData = None
# ) -> Event[OrderPlacedData]: ...
# @overload
# def create_event(
#     event_type: EVENT_TYPE.PORTFOLIO_UPDATE, data: PortfolioUpdateData = None
# ) -> Event[PortfolioUpdateData]: ...


# def create_event(event_type, time=None, payload=None):
#     return Event(event_type, time=time, payload=data)


class Frequency(enum.Enum):
    DAILY = 1
