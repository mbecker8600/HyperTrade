from __future__ import annotations

import enum
import uuid
from typing import Any, Generic, Optional, TypeVar

from pandas import Timestamp


class EVENT_TYPE(enum.Enum):
    """Registry of all events that can be subscribed to."""

    MARKET_OPEN = 1
    """Emitted at market open.
    Publisher: MarketEvents
    Payload: None
    """

    MARKET_CLOSE = 2
    """Emitted at market close.
    Publisher: MarketEvents
    Payload: None
    """

    ORDER_PLACED = 3
    """Emitted when a strategy places an order.
    Publisher: TradingStrategy
    Payload: Order
    """

    ORDER_FULFILLED = 4
    """Emitted when an order executes.
    Publisher: BrokerService
    Payload: Transaction
    """

    PORTFOLIO_UPDATE = 5
    """Emitted when the portfolio changes.
    Publisher: PortfolioManager
    Payload: None
    """

    PRICE_CHANGE = 6
    """Emitted on new price data.
    Publisher: MarketPriceService
    Payload: PriceChangeData
    """

    PRE_MARKET_OPEN = 7
    """Emitted 15 minutes before market open.
    Publisher: MarketEvents
    Payload: None
    """

    POST_MARKET_CLOSE = 8
    """Emitted 15 minutes after market close.
    Publisher: MarketEvents
    Payload: None
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
