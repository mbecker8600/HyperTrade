from abc import ABC, abstractmethod
import datetime
from functools import cached_property
from os import times
from typing import List, Any, Optional, overload
import pandas as pd
import pytz
import exchange_calendars as xcals

from hypertrade.libs.simulator.assets import (
    Asset,
)


class Dataset(ABC):
    """
    Abstract base class for all data.
    """

    @overload
    def fetch(
        self,
        timestamp: pd.Timestamp,
        assets: List[Asset],
    ) -> Any: ...

    @overload
    def fetch(
        self, timestamp: pd.Timestamp, assets: List[Asset], lookback: pd.Timedelta
    ) -> Any: ...

    @abstractmethod
    def fetch(
        self,
        timestamp: pd.Timestamp,
        assets: List[Asset],
        lookback: Optional[pd.Timedelta] = None,
    ) -> Any:
        """
        Fetches point-in-time data for the given symbols at the specified timestamp.

        Args:
            timestamp: The point in time for which to fetch data.
            symbols: A list of symbols to fetch data for.

        Returns:
            A dictionary where keys are symbols and values are the data for that symbol.
            The format of the data depends on the data source.
        """
        ...

    @abstractmethod
    def fetch_current_price(
        self,
        timestamp: pd.Timestamp,
        assets: List[Asset] | List[str],
    ) -> pd.Series: ...


class Source(ABC):
    """"""

    @abstractmethod
    def _fetch(
        self,
        timestamp: pd.Timestamp,
        lookback: Optional[pd.Timedelta] = None,
    ) -> pd.DataFrame:
        """
        Internal method to fetch data based on the storage mechanism.
        """
        pass


class CSVDataSource(Source):
    """CSVDataSource represents time series datasources in CSV format

    The format can be any schema such that it has a "date" column that can be used to fetch all
    information at that particular timestamp.

    """

    def __init__(self, filepath: str, **kwargs: Any) -> None:
        """CSVDataSource initialization

        Args:
            - filepath (str): The file you want to load
            - **kwargs (any): Additional kwargs to pass to the pd.read_csv(...) function
                See https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
                for additional arguments to be passed in.

        """
        self.filepath = filepath
        self.kwargs = kwargs

    @cached_property
    def data(self) -> pd.DataFrame:
        data = pd.read_csv(self.filepath, **self.kwargs)
        return data

    def _fetch(
        self,
        timestamp: pd.Timestamp,
        lookback: Optional[pd.Timedelta] = None,
    ) -> pd.DataFrame:
        """
        Internal method to fetch data based on the storage mechanism.
        """
        data = self.data
        return data.loc(axis=0)[pd.IndexSlice[timestamp.date().strftime("%Y-%m-%d"), :]]


class OHLCVDataset(Dataset):
    """
    Data source for reading OCHLV data from a file.
    """

    def __init__(
        self,
        source: Source,
        tz: str = "America/New_York",
        exchange: str = "XNYS",
    ) -> None:
        self.source = source
        self.tz = pytz.timezone(tz)
        self.calendar: xcals.ExchangeCalendar = xcals.get_calendar(exchange)

    @overload
    def fetch(
        self,
        timestamp: pd.Timestamp,
        assets: List[Asset],
    ) -> pd.Series: ...

    @overload
    def fetch(
        self, timestamp: pd.Timestamp, assets: List[Asset], lookback: pd.Timedelta
    ) -> pd.DataFrame: ...

    def fetch(
        self,
        timestamp: pd.Timestamp,
        assets: List[Asset],
        lookback: Optional[pd.Timedelta] = None,
    ) -> pd.Series | pd.DataFrame:
        """ """
        data = self.source._fetch(timestamp, lookback)
        return data[data["ticker"].isin([asset.symbol for asset in assets])]

    def fetch_current_price(
        self,
        timestamp: pd.Timestamp,
        assets: List[Asset] | List[str],
    ) -> pd.Series:
        """ """
        # Filter to assets we care about
        if isinstance(assets[0], Asset):
            assets = [asset.symbol for asset in assets]  # type: ignore

        # Since OHLVC has a coarse understanding of prices, we have to pick the nearest
        # time without looking into the future.
        if timestamp.time() < datetime.time(9, 30, tzinfo=self.tz):
            # Get previous closing date data
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
