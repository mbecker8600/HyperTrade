import pandas as pd

from hypertrade.libs.simulator.assets import Asset
from hypertrade.libs.simulator.event import EventManager, Frequency
from hypertrade.libs.simulator.execute.broker import BrokerService
from hypertrade.libs.simulator.execute.ledger import LedgerService
from hypertrade.libs.simulator.financials.performance import (
    PerformanceTrackingService,
)
from hypertrade.libs.simulator.financials.portfolio import PortfolioManager
from hypertrade.libs.simulator.market import MarketPriceSimulator
from hypertrade.libs.simulator.strategy import StrategyBuilder, StrategyFunction
from hypertrade.libs.tsfd.datasets.asset import PricesDataset


class TradingEngine:
    def __init__(
        self,
        start_time: pd.Timestamp,
        end_time: pd.Timestamp,
        prices_dataset: PricesDataset,
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
        self.ledger_service = LedgerService()
        self.performance_tracking_service = PerformanceTrackingService()
        self.trading_strategy = strategy_builder.build(
            strategy_function=strategy_function
        )

    def run(self) -> None:
        for _event in self.event_manager:
            pass

    @property
    def current_time(self) -> pd.Timestamp:
        return self.event_manager.current_time
