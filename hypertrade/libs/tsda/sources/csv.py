from functools import cached_property
from typing import Any, List, Optional

import exchange_calendars as xcals
import pandas as pd
import pytz
from pandas._libs.tslibs.nattype import NaTType

from hypertrade.libs.tsda.sources.types import DataSource
from hypertrade.libs.tsda.utils.time import cast_timestamp

DEFAULT_INDEX_COL = ["date"]


class CSVSource(DataSource):
    """CSVDataSource represents time series datasources in CSV format

    The format can be any schema such that it has a "date" column that can be used to fetch all
    information at that particular timestamp.
    """

    def __init__(
        self,
        filepath: str,
        tz: str = "America/New_York",
        exchange: str = "XNYS",
        index_col: List[str] = DEFAULT_INDEX_COL,
        **kwargs: Any
    ) -> None:
        self._filepath = filepath
        self._kwargs = kwargs
        self._index_col = index_col
        self._tz = pytz.timezone(tz)
        self._calendar: xcals.ExchangeCalendar = xcals.get_calendar(exchange)

    @cached_property
    def data(self) -> pd.DataFrame:
        data = pd.read_csv(
            self._filepath, parse_dates=True, index_col=self._index_col, **self._kwargs
        )
        return data

    def __len__(self) -> int:
        return len(self.data.index.unique())

    def fetch(
        self,
        timestamp: Optional[pd.Timestamp | NaTType | slice | int] = None,
        lookback: Optional[pd.Timedelta] = None,
    ) -> pd.DataFrame | pd.Series:

        # Handle error cases
        if timestamp is None and lookback is not None:
            raise ValueError("lookback cannot be used without a timestamp")

        # Handle full data fetch
        if timestamp is None and lookback is None:
            return self.data

        if timestamp is not None and (isinstance(timestamp, int)):
            timestamp = self.data.index.unique().sort_values()[timestamp]

        if timestamp is not None:
            timestamp = cast_timestamp(timestamp)

        # Handle lookback data
        # TODO: Come back to this and make it more explicit about the lookback since this
        # wont work for tick data.
        if timestamp is not None and lookback is not None:
            return self.data.loc[
                self._calendar.sessions_window(timestamp, -lookback.days)
            ]

        # Return data at timestamp
        return self.data.loc[timestamp]
