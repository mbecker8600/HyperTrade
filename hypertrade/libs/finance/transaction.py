import pandas as pd

from hypertrade.libs.finance.assets import Asset


class Transaction:
    def __init__(
        self, asset: Asset, amount: int, dt: pd.Timestamp, price: float, order_id: str
    ) -> None:
        self.asset = asset
        self.amount = amount
        self.dt = dt
        self.price = price
        self.order_id = order_id
