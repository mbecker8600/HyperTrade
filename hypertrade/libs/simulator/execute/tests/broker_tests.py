import os
import unittest

import exchange_calendars as xcals
import pandas as pd
import pytz

# import hypertrade.libs.debugging  # donotcommit
from hypertrade.libs.simulator.assets import Asset
from hypertrade.libs.simulator.event.service import EventManager
from hypertrade.libs.simulator.execute.broker import BrokerService
from hypertrade.libs.tsfd.datasets.asset import PricesDataset
from hypertrade.libs.tsfd.sources.csv import CSVSource
from hypertrade.libs.tsfd.sources.formats.ohlvc import OHLVCDataSourceFormat
from hypertrade.libs.tsfd.utils.time import cast_timestamp


class TestBrokerService(unittest.TestCase):
    def setUp(self) -> None:
        nytz = pytz.timezone("America/New_York")
        self.start_time = pd.Timestamp("2021-10-01 08:00:00", tz=nytz)
        self.end_time = pd.Timestamp("2021-10-02 20:00:00", tz=nytz)
        self.event_manager = EventManager(
            start_time=cast_timestamp(self.start_time),
            end_time=cast_timestamp(self.end_time),
        )
        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(ws, "../../data/tests/data/ohlvc/sample.csv")

        # Create an OCHLV data source using a CSV file
        cal = xcals.get_calendar("XNYS")
        self.dataset = PricesDataset(
            data_source=OHLVCDataSourceFormat(
                CSVSource(filepath=sample_data_path),
            ),
            symbols=["GE", "BA"],
            name="prices",
            trading_calendar=cal,
        )
        self.broker_service = BrokerService(dataset=self.dataset)
        self.asset = Asset(sid=1, symbol="AAPL", asset_name="Apple")

    def test_order_on_open(self) -> None:
        """Placing an order before market open should schedule at next open."""
        next(self.event_manager)  # Advance to market pre open
        next(self.event_manager)  # Advance to market open
        self.assertEqual(
            self.event_manager.current_time,
            pd.Timestamp("2021-10-01 09:30:00", tz=pytz.timezone("America/New_York")),
        )
        order = self.broker_service.place_order(self.asset, 10)
        self.assertEqual(order.order_placed, self.event_manager.current_time)

    def test_order_before_open(self) -> None:
        """Placing an order before market open should schedule at next open."""
        order = self.broker_service.place_order(self.asset, 10)
        self.assertGreater(order.order_placed, self.start_time)

    def test_order_after_close(self) -> None:
        """Placing an order after market close should schedule at next open."""
        next(self.event_manager)  # Advance to market pre open
        next(self.event_manager)  # Advance to market open
        next(self.event_manager)  # Advance to market close
        next(self.event_manager)  # Advance to market post close
        self.assertEqual(
            self.event_manager.current_time,
            pd.Timestamp("2021-10-01 16:15:00", tz=pytz.timezone("America/New_York")),
        )
        order = self.broker_service.place_order(self.asset, 5)
        self.assertGreater(order.order_placed, self.event_manager.current_time)


if __name__ == "__main__":
    unittest.main()
