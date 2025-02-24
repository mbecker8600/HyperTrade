from __future__ import annotations

from abc import abstractmethod
from typing import (
    Any,
    Generator,
    Optional,
)

import pandas as pd
from pandas._libs.tslibs.nattype import NaTType
from torch import Tensor
from torch.utils.data import IterableDataset

from hypertrade.libs.tsfd.sources.types import DataSource
from hypertrade.libs.tsfd.transforms import RollingFeatures, Transform


# trunk-ignore(mypy/misc)
class TsfdDataset(IterableDataset[pd.DataFrame | Tensor]):
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
    ) -> pd.DataFrame | Tensor: ...

    @abstractmethod
    def _load_data(self, idx: pd.Timestamp | NaTType | slice | int) -> pd.DataFrame: ...

    @abstractmethod
    def __repr__(self) -> str: ...

    @abstractmethod
    def __iter__(self) -> Generator[pd.DataFrame | Tensor, Any, None]: ...


class TimeSeriesDataset(TsfdDataset):
    """
    The TimeSeriesDataset is an abstraction for applying domain-specific logic to time-series data.
    It references a DataSource (or DataSourceFormat) and adapts the returned data for a particular
    use case, such as OHLCV or current prices. Its role is to manage symbols, apply domain filters or
    transformations, and ensure data integrity at the dataset level, while delegating raw access
    and format validations to the underlying DataSource or DataSourceFormat.
    """

    def __init__(
        self,
        data_source: DataSource,
        name: Optional[str] = None,
        transforms: Optional[Transform] = None,
    ) -> None:
        self.data_source = data_source
        self.name = name
        self.full_data: pd.DataFrame = self.data_source.fetch()
        self.timestamps: pd.Index = self.full_data.index
        self.transforms = transforms

    def __len__(self) -> int:
        return len(self.data_source)

    def __getitem__(
        self, idx: pd.Timestamp | NaTType | slice | int
    ) -> pd.DataFrame | Tensor:
        max_window = self._get_rolling_window()
        df = self._load_data_with_window(idx, max_window)
        if self.transforms:
            df = self.transforms(df)
        return df

    def _load_data_with_window(
        self, idx: pd.Timestamp | NaTType | slice | int, window: int
    ) -> pd.DataFrame:
        # Convert a timestamp or integer to the appropriate slice to include (window - 1) extra periods.
        if not window or window < 2:
            return self._load_data(idx)

        # If idx is a slice, expand the start backwards if possible
        if isinstance(idx, slice):
            start, stop = idx.start, idx.stop
            # Expand the slice window backwards if start is a timestamp or int
            if isinstance(start, pd.Timestamp):
                pos = self.timestamps.get_loc(start)
                start_pos = max(pos - (window - 1), 0)
                start = self.timestamps[start_pos]
            elif isinstance(start, int):
                start = max(start - (window - 1), 0)
            extended_slice = slice(start, stop, idx.step)
            return self._load_data(extended_slice)

        # If idx is a single timestamp, convert it to a slice that includes extra rows before
        if isinstance(idx, pd.Timestamp):
            pos = self.timestamps.get_loc(idx)
            start_pos = max(pos - (window - 1), 0)
            extended_slice = slice(self.timestamps[start_pos], idx)
            return self._load_data(extended_slice)

        # If idx is an integer, shift it backwards
        if isinstance(idx, int):
            start_idx = max(idx - window, 0)
            extended_slice = slice(start_idx, idx)
            return self._load_data(extended_slice)

        # Fallback
        return self._load_data(idx)

    def _get_rolling_window(self) -> int:
        if not self.transforms:
            return 0
        # If self.transforms is a Compose, gather all transforms; otherwise just wrap one transform
        transforms_list = getattr(self.transforms, "transforms", [self.transforms])
        max_window = 0
        for t in transforms_list:
            if isinstance(t, RollingFeatures):
                max_window = max(max_window, t.window)
        return max_window

    def _load_data(self, idx: pd.Timestamp | NaTType | slice | int) -> pd.DataFrame: ...

    def __repr__(self) -> str:  # Improved representation for easier debugging
        return f"{self.__class__.__name__}(name={self.name}, shape={len(self)})"

    # def get_time_range(self) -> Tuple[pd.Timestamp, pd.Timestamp]:
    #     """Returns the start and end timestamps of the dataset."""
    #     return self.timestamps.min(), self.timestamps.max()

    def __iter__(self) -> Generator[pd.DataFrame | Tensor, Any, None]:
        max_window = self._get_rolling_window()
        for idx in range(max_window, len(self)):
            df = self.__getitem__(idx)
            yield df
