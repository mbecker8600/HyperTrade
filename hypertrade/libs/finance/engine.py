from loguru import logger
import pandas as pd

from hypertrade.libs.finance.assets import Asset
from hypertrade.libs.finance.data.datasource import Dataset
from hypertrade.libs.finance.event import EventManager, Frequency
from hypertrade.libs.finance.market import MarketPriceSimulator
from hypertrade.libs.finance.execute.broker import BrokerService
from hypertrade.libs.finance.portfolio import PortfolioManager
from hypertrade.libs.finance.strategy import StrategyBuilder, StrategyFunction


class TradingEngine:
    def __init__(
        self,
        start_time: pd.Timestamp,
        end_time: pd.Timestamp,
        prices_dataset: Dataset,
        strategy_builder: StrategyBuilder,
        strategy_function: StrategyFunction,
        frequency: Frequency = Frequency.DAILY,
        capital_base: float = 0.0,
    ) -> None:
        self.event_manager = EventManager(start_time=start_time, end_time=end_time)

        self.portfolio_manager = PortfolioManager(prices_dataset, capital_base)
        self.market_price_simulator = MarketPriceSimulator(
            universe=[Asset(1, "GOOGL", "Google")]
        )
        self.order_manager = BrokerService(dataset=prices_dataset)
        self.trading_strategy = strategy_builder.build(
            strategy_function=strategy_function
        )

    def run(self) -> None:
        for event in self.event_manager:
            pass
