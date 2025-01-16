import pandas as pd

from hypertrade.libs.finance.event import EventManager, Frequency
from hypertrade.libs.finance.portfolio import PortfolioManager


class TradingEngine:
    def __init__(
        self,
        start_time: pd.Timestamp,
        end_time: pd.Timestamp,
        frequency: Frequency = Frequency.DAILY,
        capital_base: float = 0.0,
    ) -> None:
        self.event_manager = EventManager(start_time=start_time, end_time=end_time)
        self.portfolio_manager = PortfolioManager(start_time, capital_base)

    def run(self) -> None:

        for event in self.event_manager:
            pass
