
import unittest

from datetime import datetime

from hypertrade.libs.finance.assets import Asset
from hypertrade.libs.finance.commission import NoCommission
from hypertrade.libs.finance.order import Order
from hypertrade.libs.finance.transaction import Transaction


class TestNoCommisionModel(unittest.TestCase):

    def test_no_commision_returns_zero(self) -> None:
        """NoCommission Commision Model should return zero for all trades"""
        dummy_asset: Asset = Asset(
            sid=1, symbol="AAPL", asset_name="Apple Inc.")
        dummy_order: Order = Order(
            dt=datetime(2001, 8, 1), asset=dummy_asset, amount=100)
        dummy_txn: Transaction = Transaction(asset=dummy_asset, amount=100,
                                             dt=datetime(2001, 8, 1), price=100.0,
                                             order_id="1234")
        self.assertEqual(NoCommission.calculate(dummy_order, dummy_txn), 0.0)
