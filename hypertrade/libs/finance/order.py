
from typing import Optional
import enum
import uuid
from datetime import datetime

from hypertrade.libs.finance.assets.assets import Asset


class ORDER_STATUS(enum.Enum):
    OPEN = 1
    FILLED = 2
    CANCELLED = 3
    REJECTED = 4
    HELD = 5


class Order:

    def __init__(self, dt: datetime, asset: Asset, amount: int, filled: int = 0,
                 commission: int = 0, id: Optional[str] = None) -> None:
        """
        @dt - datetime.datetime that the order was placed
        @asset - asset for the order.
        @amount - the number of shares to buy/sell
                  a positive sign indicates a buy
                  a negative sign indicates a sell
        @filled - how many shares of the order have been filled so far
        """

        # get a string representation of the uuid.
        self.id = self.make_id() if id is None else id

    @staticmethod
    def make_id() -> str:
        return uuid.uuid4().hex
