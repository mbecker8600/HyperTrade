from abc import abstractmethod
from typing import List, Optional

import pandas as pd
from pandas._libs.tslibs.nattype import NaTType

from hypertrade.libs.tsfd.datasets.types import TimeSeriesDataset
from hypertrade.libs.tsfd.schemas.ohlvc import ohlvc_schema
from hypertrade.libs.tsfd.schemas.prices import prices_schema
from hypertrade.libs.tsfd.sources.types import DataSource, Granularity


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
        self, idx: pd.Timestamp | NaTType | slice | int, df: pd.DataFrame
    ) -> pd.DataFrame: ...


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
        name: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        granularity: Granularity = Granularity.DAILY,
    ):
        super().__init__(data_source, name)
        self.symbols = symbols
        self.data_source: PricesDatasetAdapter = data_source
        self.granularity = granularity

    def _load_data(self, idx: pd.Timestamp | NaTType | slice | int) -> pd.DataFrame:
        if isinstance(idx, pd.Timestamp) and idx.tzinfo is None:
            idx = idx.tz_localize("UTC")
        data = self.data_source.fetch(timestamp=idx)
        data = self.data_source.prices_adapter(idx, data)
        if self.symbols is not None:
            data = data.loc[pd.IndexSlice[:, self.symbols], :]
        if isinstance(data, pd.Series):
            data = data.to_frame().T
        self._schema.validate(data)
        return data
