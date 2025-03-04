import os
import unittest
from typing import Any
from unittest.mock import MagicMock, patch

import exchange_calendars as xcals
import pandas as pd
import pytz

# import hypertrade.libs.debugging  # donotcommit
from hypertrade.libs.logging.setup import initialize_logging
from hypertrade.libs.service.locator import ServiceLocator
from hypertrade.libs.simulator.assets import Asset
from hypertrade.libs.simulator.event.market import MarketEvents
from hypertrade.libs.simulator.event.service import EventManager
from hypertrade.libs.simulator.execute.broker import BrokerService
from hypertrade.libs.simulator.financials.portfolio import Portfolio, PortfolioManager
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
                CSVSource(sample_data_path),
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


class TestBrokerServiceOrderByWeights(unittest.TestCase):

    def setUp(self) -> None:
        # Mock dependencies
        self.mock_event_manager = MagicMock(spec=EventManager)
        self.mock_market_events = MagicMock(spec=MarketEvents)
        self.mock_portfolio = MagicMock(spec=Portfolio)
        self.mock_portfolio_manager = MagicMock(spec=PortfolioManager)
        self.mock_dataset = MagicMock()

        # Mock current time
        self.current_time = pd.Timestamp(
            "2024-01-01 09:30:00", tz=pytz.timezone("America/New_York")
        )
        self.mock_event_manager.current_time = self.current_time
        self.mock_event_manager._market_events = self.mock_market_events

        # Return exchange calendar for market events
        self.mock_market_events.calendar = xcals.get_calendar("XNYS")

        # Mock portfolio value and positions
        self.mock_portfolio_manager.portfolio = self.mock_portfolio
        self.mock_portfolio.portfolio_value = 100000  # Example portfolio value

        # Patch ServiceLocator to return the mocked services
        self.service_locator_patcher = patch.object(
            ServiceLocator,
            "get",
            side_effect=self._get_service,
        )
        self.service_locator_patcher.start()

        # Create BrokerService instance
        self.broker_service = BrokerService(dataset=self.mock_dataset)
        self.broker_service.event_manager = self.mock_event_manager
        self.broker_service.dataset = self.mock_dataset

    def _get_service(self, service_name: str) -> Any:
        if service_name == EventManager.SERVICE_NAME:
            return self.mock_event_manager
        elif service_name == PortfolioManager.SERVICE_NAME:
            return self.mock_portfolio_manager
        else:
            return None

    def tearDown(self) -> None:
        self.service_locator_patcher.stop()

    def test_place_order_by_weights_basic(self) -> None:
        """Test placing orders based on target weights with no existing positions."""
        # Mock dataset to return a price
        self.mock_dataset.__getitem__.return_value = pd.DataFrame(
            {"price": {"AAPL": 100, "MSFT": 200}}
        )

        self.mock_portfolio.positions = pd.DataFrame(
            # trunk-ignore(pyright/reportArgumentType)
            columns=["amount", "cost_basis"],
            index=pd.MultiIndex.from_arrays([[], []]),
        )

        # Define target weights
        target_weights = {Asset(1, "AAPL", "AAPL"): 0.5, Asset(2, "MSFT", "MSFT"): 0.5}

        # Place order
        orders = self.broker_service.place_order_by_weights(target_weights)

        # Assert that orders were placed for the correct amounts
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0].asset.symbol, "AAPL")
        self.assertEqual(orders[0].amount, 500)  # 50000 / 100 = 500
        self.assertEqual(orders[1].asset.symbol, "MSFT")
        self.assertEqual(orders[1].amount, 250)  # 50000 / 200 = 250

    def test_place_order_by_weights_selling_equities(self) -> None:
        """Test placing orders based on target weights that require selling existing positions."""
        # Mock existing positions
        self.mock_portfolio.positions = pd.DataFrame(
            {"amount": [100], "cost_basis": [50]},
            index=pd.MultiIndex.from_tuples(
                [
                    (
                        "AAPL",
                        pd.Timestamp(
                            "2023-12-31 09:30:00", tz=pytz.timezone("America/New_York")
                        ),
                    )
                ],
                names=["symbol", "time"],
            ),
        )

        # Mock dataset to return a price
        self.mock_dataset.__getitem__.return_value = pd.DataFrame(
            {"price": {"AAPL": 100, "MSFT": 200}}
        )

        # Define target weights (selling AAPL to buy MSFT)
        target_weights = {Asset(1, "AAPL", "AAPL"): 0.0, Asset(2, "MSFT", "MSFT"): 1.0}

        # Place order
        orders = self.broker_service.place_order_by_weights(target_weights)

        # Assert that orders were placed for the correct amounts
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders[0].asset.symbol, "AAPL")
        self.assertEqual(orders[0].amount, -100)  # Sell existing 100 shares
        self.assertEqual(orders[1].asset.symbol, "MSFT")
        self.assertEqual(
            orders[1].amount, 500
        )  # Buy MSFT with proceeds from AAPL sale + existing cash

    def test_place_order_by_weights_insufficient_capital(self) -> None:
        # Mock dataset to return a price
        self.mock_dataset.__getitem__.return_value = pd.DataFrame(
            {"price": {"AAPL": 1000}}
        )  # High price

        self.mock_portfolio.positions = pd.DataFrame(
            # trunk-ignore(pyright/reportArgumentType)
            columns=["amount", "cost_basis"],
            index=pd.MultiIndex.from_arrays([[], []]),
        )

        # Define target weights
        target_weights = {Asset(1, "AAPL", "AAPL"): 1.0}

        # Place order
        orders = self.broker_service.place_order_by_weights(target_weights)

        # Assert that no orders were placed due to insufficient capital
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].asset.symbol, "AAPL")
        self.assertEqual(orders[0].amount, 100)

    def test_place_order_by_weights_zero_weights(self) -> None:
        """Test placing orders based on target weights with zero weight for an asset."""
        # Mock existing positions
        self.mock_portfolio.positions = pd.DataFrame(
            {"amount": [100], "cost_basis": [50]},
            index=pd.MultiIndex.from_tuples(
                [
                    (
                        "AAPL",
                        pd.Timestamp(
                            "2023-12-31 09:30:00", tz=pytz.timezone("America/New_York")
                        ),
                    )
                ],
                names=["symbol", "time"],
            ),
        )

        # Mock dataset to return a price
        self.mock_dataset.__getitem__.return_value = pd.DataFrame(
            {"price": {"AAPL": 100}}
        )

        # Define target weights (zero weight for AAPL)
        target_weights = {Asset(1, "AAPL", "AAPL"): 0.0}

        # Place order
        orders = self.broker_service.place_order_by_weights(target_weights)

        # Assert that an order was placed to sell all AAPL shares
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].asset.symbol, "AAPL")
        self.assertEqual(orders[0].amount, -100)

    def test_place_order_by_weights_invalid_asset(self) -> None:
        # Mock dataset to return a price for only one asset
        self.mock_dataset.__getitem__.return_value = pd.DataFrame(
            {"price": {"MSFT": 200}}
        )

        self.mock_portfolio.positions = pd.DataFrame(
            # trunk-ignore(pyright/reportArgumentType)
            columns=["amount", "cost_basis"],
            index=pd.MultiIndex.from_arrays([[], []]),
        )

        # Define target weights including an invalid asset
        target_weights = {
            Asset(1, "AAPL", "AAPL"): 0.5,
            Asset(2, "MSFT", "MSFT"): 0.5,
        }  # AAPL is invalid

        # Place order
        with self.assertRaises(KeyError):
            self.broker_service.place_order_by_weights(target_weights)

    def test_place_order_by_weights_fractional_shares(self) -> None:
        # Mock dataset to return a price that results in fractional shares
        self.mock_dataset.__getitem__.return_value = pd.DataFrame(
            {"price": {"AAPL": 101}}
        )

        self.mock_portfolio.positions = pd.DataFrame(
            # trunk-ignore(pyright/reportArgumentType)
            columns=["amount", "cost_basis"],
            index=pd.MultiIndex.from_arrays([[], []]),
        )

        # Define target weights
        target_weights = {Asset(1, "AAPL", "AAPL"): 1.0}

        # Place order
        orders = self.broker_service.place_order_by_weights(target_weights)

        # Assert that the order amount is an integer (floor of the fractional share calculation)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].asset.symbol, "AAPL")
        self.assertEqual(orders[0].amount, 990)  # 100000 / 101 = 990.099 -> 990


if __name__ == "__main__":
    initialize_logging(level="DEBUG")
    unittest.main()
