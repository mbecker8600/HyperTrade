import os
import unittest
from unittest.mock import patch

import exchange_calendars as xcals
import pandas as pd
import pytz
from loguru import logger

# import hypertrade.libs.debugging  # donotcommit
from hypertrade.libs.logging.setup import initialize_logging
from hypertrade.libs.simulator.assets import Asset
from hypertrade.libs.simulator.engine import TradingEngine
from hypertrade.libs.simulator.event.types import EVENT_TYPE
from hypertrade.libs.simulator.strategy import (
    DATA_TYPE,
    StrategyBuilder,
    StrategyContext,
    StrategyData,
)
from hypertrade.libs.tsfd.datasets.asset import PricesDataset
from hypertrade.libs.tsfd.sources.csv import CSVSource
from hypertrade.libs.tsfd.sources.formats.ohlvc import OHLVCDataSourceFormat
from hypertrade.libs.tsfd.utils.time import cast_timestamp


def buy_hold_strategy(context: StrategyContext, data: StrategyData) -> None:
    with logger.contextualize(simulation_time=context.time):
        logger.info(f"Current time: {context.time}")
        logger.info(f"Current prices: {data.data[DATA_TYPE.CURRENT_PRICES]}")

        if context.portfolio.positions.empty:
            context.broker_service.place_order(
                asset=Asset(sid=1, symbol="GE", asset_name="General Electric"), amount=1
            )

        logger.info(f"Current portfolio value: {context.portfolio.portfolio_value}")


class TestTradingEngine(unittest.TestCase):

    def test_engine_current_prices(self) -> None:
        """Should successfully run engine with current prices strategy

        Test:
            - 3 days of trading (26th - 28th)
            - Using sample data
            - Using buy_hold_strategy
        """
        nytz = pytz.timezone("America/New_York")
        start_time = cast_timestamp(pd.Timestamp("2018-12-26", tz=nytz))

        # Since no time is provide, the timestamp defaults to 00:00:00, meaning this day will not be
        # included in the simulation.
        end_time = cast_timestamp(pd.Timestamp("2018-12-31", tz=nytz))

        # Use sample data for testing
        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(ws, "../data/tests/data/ohlvc/sample.csv")

        # Create an OCHLV data source using a CSV file
        cal = xcals.get_calendar("XNYS")
        ohlvc_dataset = PricesDataset(
            data_source=OHLVCDataSourceFormat(
                CSVSource(filepath=sample_data_path),
            ),
            symbols=["GE", "BA"],
            name="prices",
            trading_calendar=cal,
        )

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
        ):

            trading_strategy = strategy_builder.build(buy_hold_strategy)
            engine = TradingEngine(
                start_time=start_time,
                end_time=end_time,
                prices_dataset=ohlvc_dataset,
                capital_base=1000,
                trading_strategy=trading_strategy,
            )
            engine.run()
            self.assertEqual(engine.portfolio_manager.portfolio.cash, 967.12)
            self.assertEqual(
                engine.portfolio_manager.portfolio.portfolio_value, 1002.45
            )
            self.assertEqual(
                engine.portfolio_manager.portfolio.current_portfolio_weights.loc["GE"],
                1.0,
            )

    def test_step_until_event_daily_cycle(self) -> None:
        tz = pytz.timezone("America/New_York")
        start_time = cast_timestamp(pd.Timestamp("2018-11-27", tz=tz))
        end_time = cast_timestamp(pd.Timestamp("2018-11-30", tz=tz))

        # Use sample data for testing
        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(ws, "../data/tests/data/ohlvc/sample.csv")

        # Create an OCHLV data source using a CSV file
        cal = xcals.get_calendar("XNYS")
        ohlvc_dataset = PricesDataset(
            data_source=OHLVCDataSourceFormat(
                CSVSource(filepath=sample_data_path),
            ),
            symbols=["GE", "BA"],
            name="prices",
            trading_calendar=cal,
        )

        engine = TradingEngine(
            start_time=start_time,
            end_time=end_time,
            prices_dataset=ohlvc_dataset,
            capital_base=1000,
        )
        days = [
            pd.Timestamp("2018-11-27 09:15:00-0500", tz="America/New_York"),
            pd.Timestamp("2018-11-28 09:15:00-0500", tz="America/New_York"),
            pd.Timestamp("2018-11-29 09:15:00-0500", tz="America/New_York"),
            pd.Timestamp("2018-11-30 09:15:00-0500", tz="America/New_York"),
        ]
        # Step day by day until MARKET_PRE_OPEN, checking updates
        while True:
            try:
                evt = engine.step_until_event(EVENT_TYPE.PRE_MARKET_OPEN)
                next_day = days.pop(0)
                self.assertEqual(evt.time, next_day)
            except StopIteration:
                break


if __name__ == "__main__":
    initialize_logging(level="TRACE")
    unittest.main()
