from datetime import datetime

from hypertrade.libs.finance.simulation import Simulator
from hypertrade.libs.finance.time import Frequency


class TradingEngine:
    def __init__(
        self,
        start_time: datetime,
        end_time: datetime,
        frequency: Frequency = Frequency.DAILY,
    ) -> None:
        self.simulation = Simulator(start_time, end_time, frequency)

    def run(self) -> None:

        for event, state in self.simulation:
            if event == "market_open":
                self.on_market_open(state)
            elif event == "market_close":
                self.on_market_close(state)
            elif event == "order":
                self.on_order(state)
            elif event == "fill":
                self.on_fill(state)
            elif event == "transaction":
                self.on_transaction(state)
            elif event == "end_of_day":
                self.on_end_of_day(state)
            elif event == "end_of_simulation":
                self.on_end_of_simulation(state)
