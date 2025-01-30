import datetime
from typing import List, Optional
import pandas as pd
import pytz
import exchange_calendars as xcals

from hypertrade.libs.tsda.core.source import Source


class OHLCVFormatMixin:
    """
    Mixin class for handling OHLCV data.
    """

    def __init__(self, source: Source, tz: str, exchange: str) -> None:
        self.source = source
        self.tz = pytz.timezone(tz)
        self.calendar: xcals.ExchangeCalendar = xcals.get_calendar(exchange)

    def fetch_ohlcv(
        self,
        timestamp: pd.Timestamp,
        assets: List[str],
        lookback: Optional[pd.Timedelta] = None,
    ) -> pd.DataFrame:
        """
        Fetches OHLCV data at the specified timestamp.
        """
        data = self.source._fetch(timestamp, lookback)
        if assets:
            return data[data["ticker"].isin(assets)]
        else:
            return data

    def fetch_current_price(
        self,
        timestamp: pd.Timestamp,
        assets: List[str],
    ) -> pd.Series:
        """
        Fetches the current price from OHLCV data at the specified timestamp.
        """
        if timestamp.time() < datetime.time(9, 30, tzinfo=self.tz):
            previous_close = self.calendar.previous_close(timestamp)
            previous_data = self.source._fetch(previous_close)
            return previous_data.droplevel("date")["close"].loc(axis=0)[
                pd.IndexSlice[assets]
            ]
        elif timestamp.time() < datetime.time(16, 00, tzinfo=self.tz):
            data = self.source._fetch(timestamp)
            return data.droplevel("date")["open"].loc(axis=0)[pd.IndexSlice[assets]]
        else:
            data = self.source._fetch(timestamp)
            return data.droplevel("date")["close"].loc(axis=0)[pd.IndexSlice[assets]]
