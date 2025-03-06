from functools import cached_property
from typing import Any, List, Optional, cast

import pandas as pd
import pandera as pa
from pandas._libs.tslibs.nattype import NaTType

from hypertrade.libs.tsfd.sources.formats.default import DefaultDataSourceFormat
from hypertrade.libs.tsfd.sources.types import (
    DataSource,
    DataSourceFormat,
    FetchMode,
    Granularity,
)
from hypertrade.libs.tsfd.utils.dataframe import get_index_strategy
from hypertrade.libs.tsfd.utils.time import cast_timestamp


class CSVSource(DataSource):
    """CSVDataSource represents time series datasources in CSV format

    The format can be any schema such that it has a "date" column that can be used to fetch all
    information at that particular timestamp.
    """

    def __init__(
        self,
        source: str | pd.DataFrame,
        granularity: Granularity = Granularity.DAILY,
        **kwargs: Any
    ) -> None:
        """

        Args:
            source (str | pd.DataFrame): The source of the data. If a string, it is treated as a file path.
            granularity (Granularity, optional): The granularity of the data. Defaults to Granularity.DAILY.
            **kwargs (Any): Additional keyword arguments to pass to the pandas read_csv function.

        """
        super().__init__(granularity)
        self._source = source
        self._kwargs = kwargs
        self._format: Optional[DataSourceFormat] = None
        self._index: pa.Index | pa.MultiIndex | pd.Index | pd.MultiIndex
        if isinstance(self._source, pd.DataFrame):
            self._index = cast(pd.Index | pd.MultiIndex, self._source.index)
        else:
            self._format = DefaultDataSourceFormat(self)
            self._index = cast(pa.Index | pa.MultiIndex, self._format.schema.index)

        self._index_strategy = get_index_strategy(self._index)

    @property
    def format(self) -> Optional[DataSourceFormat]:
        return self._format

    @format.setter
    def format(self, value: DataSourceFormat) -> None:
        self._format = value
        self._index = cast(pa.Index | pa.MultiIndex, value.schema.index)
        self._index_strategy = get_index_strategy(self._index)

    @cached_property
    def data(self) -> pd.DataFrame:
        index_col = cast(List[str], self._index.names)
        data = (
            self._source
            if isinstance(self._source, pd.DataFrame)
            else pd.read_csv(
                self._source, parse_dates=True, index_col=index_col, **self._kwargs
            )
        )
        data = data.sort_index()
        if data is None:
            raise ValueError(
                "Source must be a DataFrame, but got a {}".format(type(data))
            )
        if self.format is not None:
            self.format.schema.validate(data)
        return data

    def __len__(self) -> int:
        return self._index_strategy.size(self.data)

    def _fetch(
        self,
        timestamp: Optional[pd.Timestamp | NaTType | slice | int] = None,
        mode: FetchMode = FetchMode.LATEST,
    ) -> pd.DataFrame:

        # Handle full data fetch
        if timestamp is None:
            return self.data

        if isinstance(timestamp, slice):
            if all(
                isinstance(x, int) or x is None
                for x in [timestamp.start, timestamp.stop]
            ):
                start = self._index_strategy.get_timestamp_at_index(
                    self.data, timestamp.start
                )
                stop = self._index_strategy.get_timestamp_at_index(
                    self.data, timestamp.stop
                )
                timestamp = slice(start, stop, timestamp.step)
            data = self._index_strategy.loc_slice(self.data, timestamp)
            return data

        # Handle integer index by converting to timestamp
        if isinstance(timestamp, int):
            timestamp = self._index_strategy.get_timestamp_at_index(
                self.data, timestamp
            )

        if isinstance(timestamp, pd.Timestamp) or isinstance(timestamp, NaTType):
            timestamp = cast_timestamp(timestamp)

        # Return data at timestamp
        data = self._index_strategy.loc(self.data, timestamp)
        return data

    @cached_property
    def mean(self) -> pd.Series | pd.DataFrame:
        return self._index_strategy.mean(self.data)

    @cached_property
    def std(self) -> pd.Series | pd.DataFrame:
        return self._index_strategy.std(self.data)
