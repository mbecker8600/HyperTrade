
from datetime import datetime

from hypertrade.libs.finance.assets.assets import Asset


class Transaction():
    def __init__(self, asset: Asset, amount: int, dt: datetime, price: float, order_id: str) -> None:
        self.asset = asset
        self.amount = amount
        self.dt = dt
        self.price = price
        self.order_id = order_id
