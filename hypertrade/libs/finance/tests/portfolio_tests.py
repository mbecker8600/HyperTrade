from calendar import c
import os
import unittest

import pytz
import pandas as pd
from loguru import logger

from hypertrade.libs.finance.assets import Asset
from hypertrade.libs.finance.data.datasource import CSVDataSource, OHLCVDataset
from hypertrade.libs.finance.event import EVENT_TYPE, Event, EventManager
from hypertrade.libs.finance.execute.types import Transaction
from hypertrade.libs.finance.portfolio import Portfolio, PortfolioManager

from hypertrade.libs.logging.setup import initialize_logging

# import hypertrade.libs.debugging  # donotcommit


class TestPortfolioService(unittest.TestCase):
    def setUp(self) -> None:
        logger.debug("Test setup")
        # Use sample data for testing
        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(ws, "../data/tests/data/ohlvc/sample.csv")

        # Create an OCHLV data source using a CSV file
        csv_source = CSVDataSource(sample_data_path, index_col=["date", "ticker"])
        self.ohlvc_dataset = OHLCVDataset(csv_source)

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
        self.assertEqual(self.portfolio_manager.portfolio.pnl, 0.0)
        self.assertEqual(self.portfolio_manager.portfolio.returns, 0.0)
        self.assertTrue(self.portfolio_manager.portfolio.positions.empty)
        self.assertEqual(self.portfolio_manager.portfolio.positions_value, 0.0)
        self.assertEqual(self.portfolio_manager.portfolio.positions_exposure, 0.0)
        self.assertEqual(self.portfolio_manager.portfolio.cash_flow, 0.0)
        self.assertEqual(self.portfolio_manager.portfolio.capital_used, 0.0)

        weights = self.portfolio_manager.portfolio.current_portfolio_weights
        self.assertTrue(weights.empty)

    def test_buy_hold(self) -> None:
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


class TestPortfolio(unittest.TestCase):

    def setUp(self) -> None:
        logger.debug("Test setup")
        # Use sample data for testing
        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(ws, "../data/tests/data/ohlvc/sample.csv")

        # Create an OCHLV data source using a CSV file
        csv_source = CSVDataSource(sample_data_path, index_col=["date", "ticker"])
        self.ohlvc_dataset = OHLCVDataset(csv_source)

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
        self.assertEqual(portfolio.pnl, 0.0)
        self.assertEqual(portfolio.returns, 0.0)
        self.assertTrue(portfolio.positions.empty)
        self.assertEqual(portfolio.positions_value, 0.0)
        self.assertEqual(portfolio.positions_exposure, 0.0)
        self.assertEqual(portfolio.cash_flow, 0.0)
        self.assertEqual(portfolio.capital_used, 0.0)

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
        prices = self.ohlvc_dataset.fetch_current_price(
            self.event_manager.current_time, [boeing_asset]
        )
        portfolio.update(tx=tx)
        portfolio.current_market_prices = prices
        self.assertEqual(portfolio.cash, capital_base - (n_shares * tx_price))

        weights = portfolio.current_portfolio_weights
        self.assertEqual(weights[boeing_asset.symbol], 1.0)
        # portfolio value shouldn't change because market value hasn't changed yet.
        self.assertEqual(portfolio.portfolio_value, 1000)
        self.assertEqual(portfolio.positions_value, tx_price)

        next(self.event_manager)  # Simulate to the next market event
        prices = self.ohlvc_dataset.fetch_current_price(
            self.event_manager.current_time, [boeing_asset]
        )
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
