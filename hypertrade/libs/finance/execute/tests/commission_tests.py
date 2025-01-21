import unittest

import pandas as pd

from hypertrade.libs.finance.assets import Asset
from hypertrade.libs.finance.execute.commission import NoCommission
from hypertrade.libs.finance.execute.types import Order, Transaction


class TestNoCommisionModel(unittest.TestCase):

    def test_no_commision_returns_zero(self) -> None:
        """NoCommission Commision Model should return zero for all trades"""
        dummy_asset: Asset = Asset(sid=1, symbol="AAPL", asset_name="Apple Inc.")
        dummy_order: Order = Order(
            order_placed=pd.Timestamp("2001-08-01"), asset=dummy_asset, amount=100
        )
        dummy_txn: Transaction = Transaction(
            asset=dummy_asset,
            amount=100,
            dt=pd.Timestamp("2001-08-01"),
            price=100.0,
            order_id="1234",
        )
        self.assertEqual(NoCommission.calculate(dummy_order, dummy_txn), 0.0)
