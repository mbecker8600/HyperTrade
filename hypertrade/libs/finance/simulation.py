from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

import pandas as pd

from hypertrade.libs.finance.event import EVENT
from hypertrade.libs.finance.time import Frequency, TradingClock


@dataclass
class SimulationState():
    current_time: datetime
    """The current time of the simulation"""

    current_prices: pd.Series
    """The current prices of the assets in the simulation
    """


class Simulator():

    def __init__(self, start_time: datetime, end_time: datetime, frequency: Frequency = Frequency.DAILY) -> None:
        self.clock = TradingClock(
            start_time=start_time, end_time=end_time, frequency=frequency)

    def __iter__(self) -> Simulator:
        return self

    def __next__(self) -> Tuple[EVENT, SimulationState]:
        event, current_time = next(self.clock)
        prices = self._retrieve_prices(current_time)
        return event, SimulationState(current_time=current_time, current_prices=prices)

    def _retrieve_prices(self, current_time: datetime) -> pd.Series:
        # TODO: Get prices at current time
        return pd.Series([100.0, 200.0], index=[
            "GOOGL", "AAPL"])
