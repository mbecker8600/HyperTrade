import os
import unittest

import exchange_calendars as xcals
import pandas as pd
import pytz
from loguru import logger

# import hypertrade.libs.debugging  # donotcommit
from hypertrade.libs.logging.setup import initialize_logging
from hypertrade.libs.simulator.assets import Asset
from hypertrade.libs.simulator.event import EVENT_TYPE, Event, EventManager
from hypertrade.libs.simulator.execute.types import Transaction
from hypertrade.libs.simulator.financials.portfolio import Portfolio, PortfolioManager
from hypertrade.libs.tsfd.datasets.asset import PricesDataset
from hypertrade.libs.tsfd.sources.csv import CSVSource
from hypertrade.libs.tsfd.sources.formats.ohlvc import OHLVCDataSourceFormat


class TestPortfolioService(unittest.TestCase):
    def setUp(self) -> None:
        logger.debug("Test setup")
        # Use sample data for testing
        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(ws, "../../data/tests/data/ohlvc/sample.csv")

        # Create an OCHLV data source using a CSV file
        self.cal = xcals.get_calendar("XNYS")
        self.ohlvc_dataset = PricesDataset(
            data_source=OHLVCDataSourceFormat(
                CSVSource(filepath=sample_data_path),
            ),
            symbols=["GE", "BA"],
            name="prices",
            trading_calendar=self.cal,
        )

        nytz = pytz.timezone("America/New_York")
        start_time = pd.Timestamp("2018-12-26", tz=nytz)

        # Since no time is provide, the timestamp defaults to 00:00:00, meaning this day will not be
        # included in the simulation.
        end_time = pd.Timestamp("2018-12-31", tz=nytz)
        self.event_manager = EventManager(start_time=start_time, end_time=end_time)
        self.portfolio_manager = PortfolioManager(
            self.ohlvc_dataset, capital_base=1000.0
        )
        next(self.event_manager)  # Simulate to the first market event

    def test_portfolio_manager_initialization(self) -> None:
        """Basic initialization of the PortfolioManager object"""
        logger.info("Testing PortfolioManager initialization")
        self.assertEqual(self.portfolio_manager.portfolio.starting_cash, 1000.0)
        self.assertEqual(self.portfolio_manager.portfolio.cash, 1000.0)
        self.assertEqual(self.portfolio_manager.portfolio.portfolio_value, 1000.0)
        self.assertTrue(self.portfolio_manager.portfolio.positions.empty)
        self.assertEqual(self.portfolio_manager.portfolio.positions_value, 0.0)

        weights = self.portfolio_manager.portfolio.current_portfolio_weights
        self.assertTrue(weights.empty)

    def test_buy_hold_multiple_positions(self) -> None:
        """Test buying and holding a single asset"""
        logger.debug("Testing buying and holding a single asset")
        # Buy 1 share of Boeing
        self.event_manager.schedule_event(
            Event(
                event_type=EVENT_TYPE.ORDER_FULFILLED,
                data=Transaction(
                    amount=1,
                    asset=Asset(
                        sid=1, symbol="BA", asset_name="Boeing", price_multiplier=1.0
                    ),
                    dt=pd.Timestamp("2018-12-26 09:30:00"),
                    price=290.18,
                    order_id="testing",
                ),
            )
        )
        next(self.event_manager)  # Simulate to the next market event
        self.assertEqual(self.portfolio_manager.portfolio.cash, 1000.0 - 290.18)
        self.assertEqual(self.portfolio_manager.portfolio.positions_value, 290.18)
        self.assertEqual(self.portfolio_manager.portfolio.portfolio_value, 1000.0)
        self.event_manager.schedule_event(
            Event(
                event_type=EVENT_TYPE.ORDER_FULFILLED,
                data=Transaction(
                    amount=1,
                    asset=Asset(
                        sid=2,
                        symbol="GE",
                        asset_name="General Electric",
                        price_multiplier=1.0,
                    ),
                    dt=pd.Timestamp("2018-12-26 09:30:00"),
                    price=32.88,
                    order_id="testing",
                ),
            )
        )
        next(self.event_manager)  # Simulate to the next market event
        self.assertEqual(self.portfolio_manager.portfolio.cash, 1000.0 - 290.18 - 32.88)
        self.assertEqual(
            self.portfolio_manager.portfolio.positions_value, 290.18 + 32.88
        )
        self.assertEqual(self.portfolio_manager.portfolio.portfolio_value, 1000.0)

        next(self.event_manager)  # Simulate to the next market event
        self.event_manager.schedule_event(
            Event(
                event_type=EVENT_TYPE.PRICE_CHANGE,
                data=None,
            )
        )
        next(self.event_manager)  # advanced to price change event
        self.assertEqual(self.portfolio_manager.portfolio.cash, 1000.0 - 290.18 - 32.88)
        self.assertEqual(
            self.portfolio_manager.portfolio.positions_value,
            305.06 + 34.76,  # closing prices on 2018-12-26
        )
        self.assertEqual(
            self.portfolio_manager.portfolio.portfolio_value,
            self.portfolio_manager.portfolio.cash + 305.06 + 34.76,
        )


class TestPortfolio(unittest.TestCase):

    def setUp(self) -> None:
        logger.debug("Test setup")
        # Use sample data for testing
        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(ws, "../../data/tests/data/ohlvc/sample.csv")

        # Create an OCHLV data source using a CSV file
        self.cal = xcals.get_calendar("XNYS")
        self.ohlvc_dataset = PricesDataset(
            data_source=OHLVCDataSourceFormat(
                CSVSource(filepath=sample_data_path),
            ),
            symbols=["GE", "BA"],
            name="prices",
            trading_calendar=self.cal,
        )

        nytz = pytz.timezone("America/New_York")
        start_time = pd.Timestamp("2018-12-26", tz=nytz)

        # Since no time is provide, the timestamp defaults to 00:00:00, meaning this day will not be
        # included in the simulation.
        end_time = pd.Timestamp("2018-12-31", tz=nytz)
        self.event_manager = EventManager(start_time=start_time, end_time=end_time)
        next(self.event_manager)  # Simulate to the first market event

    def test_portfolio_initialization(self) -> None:
        """Basic initialization of the Portfolio object"""
        logger.info("Testing Portfolio initialization")
        portfolio = Portfolio(capital_base=1000.0)
        self.assertEqual(portfolio.starting_cash, 1000.0)
        self.assertEqual(portfolio.cash, 1000.0)
        self.assertEqual(portfolio.portfolio_value, 1000.0)
        self.assertTrue(portfolio.positions.empty)
        self.assertEqual(portfolio.positions_value, 0.0)

        weights = portfolio.current_portfolio_weights
        self.assertTrue(weights.empty)

    def test_portfolio_current_portfolio_weights_single_asset(self) -> None:
        """Basic initialization of the Portfolio object"""
        logger.debug("Testing Portfolio.current_portfolio_weights with a single asset")
        capital_base = 1000.0
        portfolio = Portfolio(capital_base=capital_base)

        boeing_asset = Asset(
            sid=1, symbol="BA", asset_name="Boeing", price_multiplier=1.0
        )
        n_shares = 1
        tx_price = 290.18
        tx = Transaction(
            amount=n_shares,
            asset=boeing_asset,
            dt=pd.Timestamp("2018-12-26 09:30:00"),
            price=tx_price,
            order_id="testing",
        )

        prices = self.ohlvc_dataset[self.event_manager.current_time]["price"]
        prices = prices.filter([boeing_asset.symbol])
        if not isinstance(prices, pd.Series):
            raise ValueError("Prices df is not a series")
        portfolio.update(tx=tx)
        portfolio.current_market_prices = prices
        self.assertEqual(portfolio.cash, capital_base - (n_shares * tx_price))

        weights = portfolio.current_portfolio_weights
        self.assertEqual(weights[boeing_asset.symbol], 1.0)
        # portfolio value shouldn't change because market value hasn't changed yet.
        self.assertEqual(portfolio.portfolio_value, 1000)
        self.assertEqual(portfolio.positions_value, tx_price)

        next(self.event_manager)  # Simulate to the next market event
        prices = self.ohlvc_dataset[self.event_manager.current_time]["price"]
        prices = prices.filter([boeing_asset.symbol])
        if not isinstance(prices, pd.Series):
            raise ValueError("Prices df is not a series")
        portfolio.current_market_prices = prices
        self.assertEqual(weights[boeing_asset.symbol], 1.0)
        # Now the portfolio value should change because the market value has changed.
        self.assertAlmostEqual(portfolio.portfolio_value, 1014.88, places=2)
        self.assertEqual(portfolio.positions_value, 305.06)

        logger.debug(
            "Ending test Portfolio.current_portfolio_weights with a single asset"
        )


if __name__ == "__main__":
    initialize_logging(level="DEBUG")
    unittest.main()
