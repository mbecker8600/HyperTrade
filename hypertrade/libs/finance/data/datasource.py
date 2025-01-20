from abc import ABC, abstractmethod
from functools import cached_property
from typing import List, Dict, Any, Optional, overload
import pandas as pd

from hypertrade.libs.finance.assets import (
    Asset,
)


class Data(ABC):
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


class DataSource(ABC):
    @abstractmethod
    def _fetch(
        self,
        timestamp: pd.Timestamp,
        lookback: pd.Timedelta = None,
    ) -> pd.DataFrame:
        """
        Internal method to fetch data based on the storage mechanism.
        """
        pass


class CSVDataSource(DataSource):
    """CSVDataSource represents time series datasources in CSV format

    The format can be any schema such that it has a "date" column that can be used to fetch all
    information at that particular timestamp.

    """

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath

    @cached_property
    def data(self) -> pd.DataFrame:
        data = pd.read_csv(self.filepath, index_col=["date"])
        return data

    def _fetch(
        self,
        timestamp: pd.Timestamp,
        lookback: pd.Timedelta = None,
    ) -> pd.DataFrame:
        """
        Internal method to fetch data based on the storage mechanism.
        """
        data = self.data
        return data.loc[timestamp.date().strftime("%Y-%m-%d")]


class OHLCVData(Data):
    """
    Data source for reading OCHLV data from a file.
    """

    def __init__(self, datasource: DataSource) -> None:
        self.datasource = datasource

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
        data = self.datasource._fetch(timestamp, lookback)
        return data[data["ticker"].isin([asset.symbol for asset in assets])]
