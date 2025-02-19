import unittest

import pandas as pd

from hypertrade.libs.logging.setup import initialize_logging
from hypertrade.libs.simulator.assets import Asset
from hypertrade.libs.simulator.execute.commission import NoCommission
from hypertrade.libs.simulator.execute.types import Order, Transaction
from hypertrade.libs.tsfd.utils.time import cast_timestamp


class TestNoCommisionModel(unittest.TestCase):

    def test_no_commision_returns_zero(self) -> None:
        """NoCommission Commision Model should return zero for all trades"""
        dummy_asset: Asset = Asset(sid=1, symbol="AAPL", asset_name="Apple Inc.")
        dummy_order: Order = Order(
            order_placed=cast_timestamp(pd.Timestamp("2001-08-01")),
            asset=dummy_asset,
            amount=100,
        )
        dummy_txn: Transaction = Transaction(
            asset=dummy_asset,
            amount=100,
            dt=cast_timestamp(pd.Timestamp("2001-08-01")),
            price=100.0,
            order_id="1234",
        )
        self.assertEqual(NoCommission.calculate(dummy_order, dummy_txn), 0.0)


if __name__ == "__main__":
    initialize_logging(level="DEBUG")
    unittest.main()
