from typing import Any, Optional

import pandas as pd

from hypertrade.libs.simulator.assets import Asset
from hypertrade.libs.simulator.event.service import EventManager
from hypertrade.libs.simulator.event.types import EVENT_TYPE, Event, Frequency
from hypertrade.libs.simulator.execute.broker import BrokerService
from hypertrade.libs.simulator.execute.ledger import LedgerService
from hypertrade.libs.simulator.financials.performance import (
    PerformanceTrackingService,
)
from hypertrade.libs.simulator.financials.portfolio import PortfolioManager
from hypertrade.libs.simulator.market import MarketPriceService
from hypertrade.libs.simulator.strategy import (
    TradingStrategy,
)
from hypertrade.libs.tsfd.datasets.asset import PricesDataset


class TradingEngine:
    def __init__(
        self,
        start_time: pd.Timestamp,
        end_time: pd.Timestamp,
        prices_dataset: PricesDataset,
        trading_strategy: Optional[TradingStrategy] = None,
        frequency: Frequency = Frequency.DAILY,
        capital_base: float = 0.0,
    ) -> None:
        self.event_manager = EventManager(start_time=start_time, end_time=end_time)

        self.portfolio_manager = PortfolioManager(prices_dataset, capital_base)
        self.market_price_simulator = MarketPriceService(
            universe=[Asset(1, "GOOGL", "Google")]
        )
        self.order_manager = BrokerService(dataset=prices_dataset)
        self.ledger_service = LedgerService()
        self.performance_tracking_service = PerformanceTrackingService()
        self.trading_strategy: Optional[TradingStrategy] = trading_strategy
        if self.trading_strategy is not None:
            self.trading_strategy.register_strategy()

    def run(self) -> None:
        for _event in self.event_manager:
            pass

    @property
    def current_time(self) -> pd.Timestamp:
        return self.event_manager.current_time

    def step_until_event(self, event_type: EVENT_TYPE) -> Event[Any]:
        """
        Advances the simulation until the specified event is reached.

        Args:
            event_type (EVENT_TYPE): The event type to wait for.

        Returns:
            Event[Any]: The event that was waited for.

        Raises:
            StopIteration: If the iteration stops before the event is reached.
        """
        while True:
            evt = next(self.event_manager)
            if evt.event_type == event_type:
                return evt
