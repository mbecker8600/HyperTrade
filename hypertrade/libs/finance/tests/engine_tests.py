import os
from typing import Optional
import unittest
from unittest.mock import patch

import pandas as pd
from loguru import logger
import pytz


from hypertrade.libs.finance.assets import Asset
from hypertrade.libs.finance.data.datasource import CSVDataSource, OHLCVDataset
from hypertrade.libs.finance.engine import TradingEngine
from hypertrade.libs.finance.event import EVENT_TYPE
from hypertrade.libs.finance.order import Order
from hypertrade.libs.finance.strategy import (
    DATA_TYPE,
    StrategyData,
    StrategyBuilder,
    StrategyContext,
)
from hypertrade.libs.logging.setup import initialize_logging

# import hypertrade.libs.debugging  # donotcommit


def buy_hold_strategy(context: StrategyContext, data: StrategyData) -> Optional[Order]:

    logger.info(f"Current time: {context.time}")
    logger.info(f"Current prices: {data.data[DATA_TYPE.CURRENT_PRICES]}")

    if not context.portfolio.positions:
        pass

    return None


class TestTradingEngine(unittest.TestCase):

    def test_engine_current_prices(self) -> None:
        """Should successfully run engine with current prices strategy

        Test:
            - 3 days of trading (26th - 28th)

        """
        nytz = pytz.timezone("America/New_York")
        start_time = pd.Timestamp("2018-12-26", tz=nytz)

        # Since no time is provide, the timestamp defaults to 00:00:00, meaning this day will not be
        # included in the simulation.
        end_time = pd.Timestamp("2018-12-31", tz=nytz)

        # Use sample data for testing
        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(ws, "../data/tests/data/ohlvc/sample.csv")

        # Create an OCHLV data source using a CSV file
        csv_source = CSVDataSource(sample_data_path, index_col=["date", "ticker"])
        ohlvc_dataset = OHLCVDataset(csv_source)

        strategy_builder = (
            StrategyBuilder()
            .on_event(EVENT_TYPE.MARKET_OPEN)
            .with_assets(
                [
                    Asset(sid=1, symbol="GE", asset_name="General Electric"),
                    Asset(sid=2, symbol="BA", asset_name="Boeing"),
                ]
            )
            .with_current_prices(data=ohlvc_dataset)
        )

        with patch(
            "__main__.buy_hold_strategy",
            wraps=buy_hold_strategy,
        ) as patched_buy_hold_strategy:
            engine = TradingEngine(
                start_time=start_time,
                end_time=end_time,
                capital_base=1000,
                strategy_function=buy_hold_strategy,
                strategy_builder=strategy_builder,
            )
            engine.run()
            pass


if __name__ == "__main__":
    initialize_logging(level="DEBUG")
    unittest.main()
