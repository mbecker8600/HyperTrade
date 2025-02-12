from __future__ import annotations

from abc import abstractmethod
from typing import (
    Any,
    Generator,
    Optional,
    Tuple,
)

import pandas as pd
from pandas._libs.tslibs.nattype import NaTType
from torch.utils.data import IterableDataset

from hypertrade.libs.tsfd.sources.types import DataSource


# trunk-ignore(mypy/misc)
class TsfdDataset(IterableDataset[pd.DataFrame]):
    """
    Abstract base class for all datasets. A dataset is a collection of data that can be
    fetched at a specific point in time. It adheres to a protocol compatible with
    the PyTorch Dataset and IterableDataset classes so that it can be used with PyTorch
    DataLoader objects.
    """

    @abstractmethod
    def __len__(self) -> int: ...

    @abstractmethod
    def __getitem__(
        self, idx: pd.Timestamp | NaTType | slice | int
    ) -> pd.DataFrame: ...

    @abstractmethod
    def _load_data(self, idx: pd.Timestamp | NaTType | slice | int) -> pd.DataFrame: ...

    @abstractmethod
    def __repr__(self) -> str: ...

    @abstractmethod
    def __iter__(self) -> Generator[pd.DataFrame, Any, None]: ...


class TimeSeriesDataset(TsfdDataset):
    """
    The TimeSeriesDataset is an abstraction for applying domain-specific logic to time-series data.
    It references a DataSource (or DataSourceFormat) and adapts the returned data for a particular
    use case, such as OHLCV or current prices. Its role is to manage symbols, apply domain filters or
    transformations, and ensure data integrity at the dataset level, while delegating raw access
    and format validations to the underlying DataSource or DataSourceFormat.
    """

    def __init__(self, data_source: DataSource, name: Optional[str] = None):
        self.data_source = data_source
        self.name = name
        self.full_data: pd.DataFrame = self.data_source.fetch()
        self.timestamps: pd.Index = self.full_data.index

    def __len__(self) -> int:
        return len(self.data_source)

    def __getitem__(self, idx: pd.Timestamp | NaTType | slice | int) -> pd.DataFrame:
        return self._load_data(idx)

    def _load_data(self, idx: pd.Timestamp | NaTType | slice | int) -> pd.DataFrame: ...

    def __repr__(self) -> str:  # Improved representation for easier debugging
        return f"{self.__class__.__name__}(name={self.name}, shape={len(self)}, time_range={self.get_time_range()})"

    def get_time_range(self) -> Tuple[pd.Timestamp, pd.Timestamp]:
        """Returns the start and end timestamps of the dataset."""
        return self.timestamps.min(), self.timestamps.max()

    def __iter__(self) -> Generator[pd.DataFrame, Any, None]:
        for idx in range(len(self)):
            yield self.__getitem__(idx)
