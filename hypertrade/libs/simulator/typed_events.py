from typing import Optional, TypedDict, overload

import pandas as pd

from hypertrade.libs.simulator.event import EVENT_TYPE, Event


class OrderPlacedData(TypedDict):
    order_id: str
    quantity: float

class PortfolioUpdateData(TypedDict):
    positions: dict[str, float]
    total_value: float

@overload
def create_event(event_type: EVENT_TYPE.MARKET_OPEN, time: Optional[pd.Timestamp] = None) -> Event[None]: ...
@overload
def create_event(event_type: EVENT_TYPE.ORDER_PLACED, time: Optional[pd.Timestamp] = None, data: OrderPlacedData = None) -> Event[OrderPlacedData]: ...
@overload
def create_event(event_type: EVENT_TYPE.PORTFOLIO_UPDATE, time: Optional[pd.Timestamp] = None, data: PortfolioUpdateData = None) -> Event[PortfolioUpdateData]: ...

def create_event(event_type, time=None, data=None):
    return Event(event_type, time=time, data=data)
