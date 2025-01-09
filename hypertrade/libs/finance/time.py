
from __future__ import annotations

from datetime import datetime, timedelta
import enum


class Frequency(enum.Enum):
    DAILY = 1


class TradingClock:
    def __init__(self, start_time: datetime, end_time: datetime, frequency: Frequency = Frequency.DAILY) -> None:
        self.start_time = start_time
        self.current_time = start_time
        self.end_time = end_time
        self.frequency = frequency

    def __iter__(self) -> TradingClock:
        return self

    def __next__(self) -> datetime:
        self.current_time += timedelta(hours=24)
        if self.current_time < self.end_time:
            return self.current_time
        raise StopIteration
