from abc import abstractmethod
from typing import List, Optional, cast

import exchange_calendars as xcals
import pandas as pd
import pandera as pa
from pandas._libs.tslibs.nattype import NaTType

from hypertrade.libs.tsfd.datasets.types import TimeSeriesDataset
from hypertrade.libs.tsfd.schemas.ohlvc import ohlvc_schema
from hypertrade.libs.tsfd.schemas.prices import prices_schema
from hypertrade.libs.tsfd.sources.types import DataSource, Granularity
from hypertrade.libs.tsfd.utils.dataframe import get_index_strategy


class OhlvcDatasetAdapter(DataSource):
    """Adapter for OHLVC datasets

    The OHLVCDataset requires that all data sources implement this adapter
    to ensure that they can be be properly loaded into the dataset regardless
    of the underlying data source format.
    """

    @abstractmethod
    def ohlvc_adapter(self, df: pd.DataFrame) -> pd.DataFrame: ...


class OHLVCDataset(TimeSeriesDataset):

    _schema = ohlvc_schema

    def __init__(
        self,
        data_source: OhlvcDatasetAdapter,
        name: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        granularity: Granularity = Granularity.DAILY,
    ):
        super().__init__(data_source, name)
        self.symbols = symbols
        self.granularity = granularity
        self.data_source: OhlvcDatasetAdapter = data_source

    def _load_data(self, idx: pd.Timestamp | NaTType | slice | int) -> pd.DataFrame:
        if isinstance(idx, pd.Timestamp) and idx.tzinfo is None:
            idx = idx.tz_localize("UTC")
        data = self.data_source.fetch(timestamp=idx)
        data = self.data_source.ohlvc_adapter(data)
        if self.symbols is not None:
            data = data.loc[pd.IndexSlice[:, self.symbols], :]
        if isinstance(data, pd.Series):
            data = data.to_frame().T
        self._schema.validate(data)
        return data


class PricesDatasetAdapter(DataSource):
    """Adapter for Prices datasets

    The PricesDataset requires that all data sources implement this adapter
    to ensure that they can be be properly loaded into the dataset regardless
    of the underlying data source format.
    """

    @abstractmethod
    def prices_adapter(
        self,
        idx: pd.Timestamp | NaTType | slice | int,
        df: pd.DataFrame,
        trading_calendar: xcals.ExchangeCalendar,
    ) -> pd.DataFrame:
        """Adapt the data to the PricesDataset format based on the
        trading calendar and the timestamp.

        Example:
            index                  price    symbol
            2004-01-09 16:00:00    83.10    'MSFT'
            2004-01-13 09:30:00    340.43   'AAPL'
            2004-01-13 16:00:00    340.43   'AAPL'

        """
        ...


class PricesDataset(TimeSeriesDataset):
    """PricesDataset will provide the most current prices for a given asset
    at a given point in time. It can accept a continuous stream of timestamps
    and will return the most recent prices for the given asset at each timestamp no
    matter the frequency of the data source.

    For example, if the data source is a daily OHLCV dataset, the PricesDataset will
    return the most recent daily prices for the given asset depending if the timestamp
    is before, durring, or after the trading day; returning the previous close, the open
    price, or the close price respectively.

    Attributes:
        data_source (DataSource): The data source to fetch the data from
        name (str): The name of the dataset
        symbols (List[str]): The list of symbols to fetch the data for
        schema (Schema): The schema to validate the data with

    Usage:
        ```python
        prices_dataset = PricesDataset(
            data_source=OHLVCDataSourceFormat(
                CSVSource(filepath="path/to/data.csv")
            ),
            name="prices",
            symbols=["GE", "BA"],
        )

        data = prices_dataset[pd.Timestamp("2018-12-03")]  # Fetch the prices for the given date
        dl = DataLoader(prices_dataset, batch_size=32)  # for Torch DataLoader
        ```

    """

    _schema = prices_schema

    def __init__(
        self,
        data_source: PricesDatasetAdapter,
        trading_calendar: xcals.ExchangeCalendar,
        name: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        granularity: Granularity = Granularity.DAILY,
    ):
        super().__init__(data_source, name)
        self.symbols = symbols
        self.data_source: PricesDatasetAdapter = data_source
        self.granularity = granularity
        self.trading_calendar = trading_calendar

    def _load_data(self, idx: pd.Timestamp | NaTType | slice | int) -> pd.DataFrame:

        original_idx = idx
        if isinstance(idx, NaTType):
            raise ValueError("Invalid timestamp passed to fetch data")

        if isinstance(idx, pd.Timestamp):
            if idx.tzinfo is None:
                idx = idx.tz_localize("UTC")

            # Need to pass in a slice because if the timestamp is before the current
            # day close, we need to fetch the previous close data
            idx = slice(
                self.trading_calendar.previous_close(idx.normalize()).normalize(), idx
            )

        data = self.data_source.fetch(timestamp=idx)
        data = self.data_source.prices_adapter(idx, data, self.trading_calendar)
        if self.symbols is not None:
            data = data.loc[pd.IndexSlice[:, self.symbols], :].sort_index()
        if isinstance(data, pd.Series):
            data = data.to_frame().T

        index_strategy = get_index_strategy(data.index)
        data = index_strategy.loc(data, original_idx)
        data.reset_index(level=0, drop=True, inplace=True)
        self._schema.validate(data)
        return data
