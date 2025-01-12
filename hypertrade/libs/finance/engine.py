from datetime import datetime

from hypertrade.libs.finance.event import EventManager, Frequency


class TradingEngine:
    def __init__(
        self,
        start_time: datetime,
        end_time: datetime,
        frequency: Frequency = Frequency.DAILY,
    ) -> None:
        self.event_manager = EventManager(start_time=start_time, end_time=end_time)

    def run(self) -> None:

        for event, state in self.event_manager:
            pass
