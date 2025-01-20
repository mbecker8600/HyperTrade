from typing import Optional
import enum
import uuid

from loguru import logger
import pandas as pd

from hypertrade.libs.finance.assets import Asset
from hypertrade.libs.finance.event import EVENT_TYPE, Event, EventManager
from hypertrade.libs.service.locator import ServiceLocator, register_service


class ORDER_STATUS(enum.Enum):
    OPEN = 1
    FILLED = 2
    CANCELLED = 3
    REJECTED = 4
    HELD = 5


class Order:

    def __init__(
        self,
        asset: Asset,
        amount: int,
        order_placed: pd.Timestamp,
        filled: int = 0,
        commission: int = 0,
        order_status: ORDER_STATUS = ORDER_STATUS.OPEN,
        id: Optional[str] = None,
    ) -> None:
        """
        @order_placed - datetime.datetime that the order was placed
        @asset - asset for the order.
        @amount - the number of shares to buy/sell
                  a positive sign indicates a buy
                  a negative sign indicates a sell
        @filled - how many shares of the order have been filled so far
        @commission - commision amount on order
        """

        # get a string representation of the uuid.
        self.id = self.make_id() if id is None else id
        self.asset = asset
        self.amount = amount
        self.order_placed = order_placed
        self.filled = filled
        self.commission = commission
        self.order_status = order_status

    @staticmethod
    def make_id() -> str:
        return uuid.uuid4().hex


ORDER_SERVICE_NAME = "order_service"


@register_service(ORDER_SERVICE_NAME)
class OrderManager:

    SERVICE_NAME = ORDER_SERVICE_NAME

    def __init__(self) -> None:
        self.event_manager: EventManager = ServiceLocator[EventManager]().get(
            EventManager.SERVICE_NAME
        )

    def place_order(self, asset: Asset, amount: int) -> Order:
        """

        Raises:


        Returns:
            Order: The pending placed order (if successful).
                NOTE: This doesn't mean it has been executed
        """
        current_time = self.event_manager.current_time
        logger.bind(simulation_time=current_time).debug(
            f"Placing order for asset: {asset} and amount: {amount}"
        )
        order = Order(asset=asset, amount=amount, order_placed=current_time)
        self.event_manager.schedule_event(
            Event(event_type=EVENT_TYPE.ORDER_PLACED, data=order)
        )
        return order
