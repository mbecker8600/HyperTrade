from typing import Optional
import unittest

import pandas as pd
from loguru import logger
import pytz


from hypertrade.libs.finance.engine import TradingEngine
from hypertrade.libs.finance.event import EVENT_TYPE
from hypertrade.libs.finance.order import Order
from hypertrade.libs.finance.strategy import (
    StrategyData,
    StrategyBuilder,
    StrategyContext,
)
from hypertrade.libs.logging.setup import initialize_logging

import hypertrade.libs.debugging  # donotcommit


def buy_hold_strategy(
    context: StrategyContext, market_data: StrategyData
) -> Optional[Order]:
    return None


class TestTradingEngine(unittest.TestCase):

    def test_engine(self) -> None:
        nytz = pytz.timezone("America/New_York")
        start_time = pd.Timestamp("2020-01-01", tz=nytz)

        # Since no time is provide, the timestamp defaults to 00:00:00, meaning this day will not be
        # included in the simulation.
        end_time = pd.Timestamp("2020-01-10", tz=nytz)
        strategy_builder = (
            StrategyBuilder()
            .on_event(EVENT_TYPE.MARKET_OPEN)
            .with_current_prices()
            .with_historical_data(lookback_period=pd.Timedelta(days=10))
        )
        engine = TradingEngine(
            start_time=start_time,
            end_time=end_time,
            capital_base=1000,
            strategy_function=buy_hold_strategy,
            strategy_builder=strategy_builder,
        )
        engine.run()


if __name__ == "__main__":
    initialize_logging(level="DEBUG")
    unittest.main()
