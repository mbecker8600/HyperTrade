from functools import cached_property
from typing import Any, List, Optional, Protocol, cast

import pandas as pd
import pandera as pa
from pandas._libs.tslibs.nattype import NaTType

from hypertrade.libs.tsfd.sources.formats.default import DefaultDataSourceFormat
from hypertrade.libs.tsfd.sources.types import DataSource, DataSourceFormat, Granularity
from hypertrade.libs.tsfd.utils.time import cast_timestamp


class IndexStrategy(Protocol):

    def size(self, df: pd.DataFrame) -> int: ...

    def loc(self, df: pd.DataFrame, timestamp: pd.Timestamp) -> pd.DataFrame: ...

    def loc_slice(self, df: pd.DataFrame, timestamp: slice) -> pd.DataFrame: ...

    def get_timestamp_at_index(self, df: pd.DataFrame, idx: int) -> pd.Timestamp: ...


class SingleIndexStrategy(IndexStrategy):

    def size(self, df: pd.DataFrame) -> int:
        return len(df.index.unique())

    def loc(self, df: pd.DataFrame, timestamp: pd.Timestamp) -> pd.DataFrame:
        data = df.loc[timestamp]
        if isinstance(data, pd.Series):
            data = data.to_frame().T
            data.index.name = "date"
        return data

    def loc_slice(self, df: pd.DataFrame, timestamp: slice) -> pd.DataFrame:
        return df.loc[(df.index >= timestamp.start) & (df.index < timestamp.stop)]

    def get_timestamp_at_index(self, df: pd.DataFrame, idx: int) -> pd.Timestamp:
        index = df.index.unique().sort_values()
        return cast(pd.Timestamp, index[idx])


class MultiIndexStrategy(IndexStrategy):

    def size(self, df: pd.DataFrame) -> int:
        return len(df.index.get_level_values(0).unique())

    def loc(self, df: pd.DataFrame, timestamp: pd.Timestamp) -> pd.DataFrame:
        data = df.xs(timestamp, level="date", drop_level=False)
        if isinstance(data, pd.Series):
            data = data.to_frame().T
        return data

    def loc_slice(self, df: pd.DataFrame, timestamp: slice) -> pd.DataFrame:
        return df.loc[
            (df.index.get_level_values(0) >= timestamp.start)
            & (df.index.get_level_values(0) < timestamp.stop),
            :,
        ]

    def get_timestamp_at_index(self, df: pd.DataFrame, idx: int) -> pd.Timestamp:
        index = df.index.get_level_values(0).unique().sort_values()
        return cast(pd.Timestamp, index[idx])


def _get_index_strategy(idx: pa.Index | pa.MultiIndex) -> IndexStrategy:
    if isinstance(idx, pa.MultiIndex):
        return MultiIndexStrategy()
    return SingleIndexStrategy()


class CSVSource(DataSource):
    """CSVDataSource represents time series datasources in CSV format

    The format can be any schema such that it has a "date" column that can be used to fetch all
    information at that particular timestamp.
    """

    def __init__(
        self, filepath: str, granularity: Granularity = Granularity.DAILY, **kwargs: Any
    ) -> None:
        super().__init__(granularity)
        self._filepath = filepath
        self._kwargs = kwargs

        self._format: DataSourceFormat = DefaultDataSourceFormat(self)
        self._index: pa.Index | pa.MultiIndex = cast(
            pa.Index | pa.MultiIndex, self._format.schema.index
        )
        self._index_strategy = _get_index_strategy(self._index)

    @property
    def format(self) -> DataSourceFormat:
        return self._format

    @format.setter
    def format(self, value: DataSourceFormat) -> None:
        self._format = value
        self._index = cast(pa.Index | pa.MultiIndex, self.format.schema.index)
        self._index_strategy = _get_index_strategy(self._index)

    @cached_property
    def data(self) -> pd.DataFrame:
        index_col = cast(List[str], self._index.names)
        data = pd.read_csv(
            self._filepath, parse_dates=True, index_col=index_col, **self._kwargs
        )
        data = data.sort_index()
        self.format.schema.validate(data)
        return data

    def __len__(self) -> int:
        return self._index_strategy.size(self.data)

    def _fetch(
        self,
        timestamp: Optional[pd.Timestamp | NaTType | slice | int] = None,
    ) -> pd.DataFrame:

        # Handle full data fetch
        if timestamp is None:
            return self.data

        if isinstance(timestamp, slice):
            data = self._index_strategy.loc_slice(self.data, timestamp)
            return data

        # Handle integer index by converting to timestamp
        if isinstance(timestamp, int):
            timestamp = self._index_strategy.get_timestamp_at_index(
                self.data, timestamp
            )

        if isinstance(timestamp, pd.Timestamp) or isinstance(timestamp, NaTType):
            timestamp = cast_timestamp(timestamp)
            # if self.granularity == Granularity.DAILY:
            #     timestamp = timestamp.normalize()

        # Return data at timestamp
        data = self._index_strategy.loc(self.data, timestamp)
        return data
