import enum
from typing import Optional
import uuid

import pandas as pd

from hypertrade.libs.finance.assets import Asset


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


class Transaction:
    def __init__(
        self, asset: Asset, amount: int, dt: pd.Timestamp, price: float, order_id: str
    ) -> None:
        self.asset = asset
        self.amount = amount
        self.dt = dt
        self.price = price
        self.order_id = order_id
