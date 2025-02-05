from functools import cached_property
from typing import Any, List, Optional, cast

import exchange_calendars as xcals
import pandas as pd
import pytz
from pandas import IndexSlice
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
    ) -> pd.DataFrame | pd.Series:

        # Handle full data fetch
        if timestamp is None:
            return self.data

        if isinstance(timestamp, slice):
            self.data.sort_index(
                level=["date", "ticker"], ascending=[1, 0], inplace=True
            )
            return self.data.loc[IndexSlice[timestamp, :], :]

        # Handle integer index by converting to timestamp
        if isinstance(timestamp, int):
            index = self.data.index.unique().sort_values()
            timestamp = cast(pd.Timestamp, index[timestamp])

        if isinstance(timestamp, pd.Timestamp) or isinstance(timestamp, NaTType):
            timestamp = cast_timestamp(timestamp)

        # Return data at timestamp
        return self.data.loc[timestamp]
