from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import ClassVar, Optional

import pandas as pd
import pandera as pa
from pandas._libs.tslibs.nattype import NaTType


class Granularity(Enum):
    DAILY = "D"
    HOURLY = "H"
    MINUTE = "T"


# TODO: Add support for other fetch modes into the datasource
class FetchMode(Enum):
    """Mode for fetching data at a specific timestamp."""

    STRICT = "strict"
    """Fetch data at the exact timestamp. If timestamp is not available, raise an error."""

    LATEST = "latest"
    """Fetch the latest data available before the timestamp."""

    INTERVAL = "interval"
    """Fetch data within the interval of the timestamp."""


class DataSource(ABC):
    """
    The DataSource is responsible for raw data access and fetch logic. It provides a core API
    for retrieving data by timestamp (or slices) at the specified granularity, without applying
    format-specific rules or dataset-specific logic. Concrete implementations must override
    _fetch() to return the requested data, and also define __len__ and format management.
    """

    def __init__(self, granularity: Granularity = Granularity.DAILY):
        self.granularity = granularity

    def fetch(
        self,
        timestamp: Optional[pd.Timestamp | NaTType | slice | int] = None,
        mode: FetchMode = FetchMode.LATEST,
    ) -> pd.DataFrame:
        """Fetch data at a specific point in time. If timestamp is None, fetch all data.

        Arguments:
            timestamp: Timestamp at which to fetch data. If None, fetch all data.
                Note, if timestamp is not timezone aware, it will be localized to UTC.
            mode: Mode for fetching data at the specified timestamp.
                Default is FetchMode.LATEST which will fetch the latest data available before the timestamp.

        Returns:
            pd.DataFrame: Data at the specified timestamp
        """
        if isinstance(timestamp, pd.Timestamp):
            timestamp = self._maybe_tz_localize(timestamp)
        if (
            isinstance(timestamp, slice)
            and isinstance(timestamp.start, pd.Timestamp)
            and isinstance(timestamp.stop, pd.Timestamp)
        ):
            timestamp = slice(
                self._maybe_tz_localize(timestamp.start),
                self._maybe_tz_localize(timestamp.stop),
                timestamp.step,
            )

        return self._fetch(timestamp, mode)

    def _maybe_tz_localize(self, timestamp: pd.Timestamp) -> pd.Timestamp:
        if timestamp.tzinfo is None:
            return timestamp.tz_localize("UTC")
        return timestamp

    @abstractmethod
    def _fetch(
        self,
        timestamp: Optional[pd.Timestamp | NaTType | slice | int] = None,
        mode: FetchMode = FetchMode.LATEST,
    ) -> pd.DataFrame: ...

    @abstractmethod
    def __len__(self) -> int: ...

    @property
    @abstractmethod
    def format(self) -> DataSourceFormat: ...

    @format.setter
    @abstractmethod
    def format(self, value: DataSourceFormat) -> None: ...


class DataSourceFormat(DataSource):
    """
    The DataSourceFormat is a decorator that adds a schema or format layer on top of a DataSource.
    It ensures data validation against a specific schema, while delegating the underlying data
    retrieval to the wrapped DataSource. It should not contain domain-specific logic for datasets.
    """

    schema: ClassVar[pa.DataFrameSchema]

    def __init__(self, datasource: DataSource):
        self._datasource = datasource
        self._datasource.format = self

    def _fetch(
        self,
        timestamp: Optional[pd.Timestamp | NaTType | slice | int] = None,
        mode: FetchMode = FetchMode.LATEST,
    ) -> pd.DataFrame:
        data = self._datasource.fetch(timestamp, mode)
        self.schema.validate(data)
        return data

    def __len__(self) -> int:
        return len(self._datasource)

    @property
    def format(self) -> DataSourceFormat:
        return self

    @format.setter
    def format(self, value: DataSourceFormat) -> None:
        raise ValueError("Cannot change format of a DataSourceFormat")
