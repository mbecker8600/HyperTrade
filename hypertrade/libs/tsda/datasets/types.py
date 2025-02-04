from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Iterator,
    Optional,
    Tuple,
    TypeVar,
)

import pandas as pd
from pandas._libs.tslibs.nattype import NaTType

from hypertrade.libs.tsda.sources.types import DataSource


class Dataset(ABC):
    """
    Abstract base class for all datasets. A dataset is a collection of data that can be
    fetched at a specific point in time. It adheres to a protocol compatible with
    the PyTorch Dataset and IterableDataset classes so that it can be used with PyTorch
    DataLoader objects.
    """

    @abstractmethod
    def __len__(self) -> int: ...

    @abstractmethod
    def __getitem__(self, idx: pd.Timestamp | NaTType | slice) -> pd.DataFrame: ...

    @abstractmethod
    def _load_data(self, idx: pd.Timestamp | NaTType | slice) -> pd.DataFrame: ...

    @abstractmethod
    def __repr__(self) -> str: ...

    def __iter__(self) -> Dataset:
        return self

    @abstractmethod
    def __next__(self) -> pd.DataFrame: ...


class TimeSeriesDataset(Dataset):
    """
    Abstract base class for all datasets. A dataset is a collection of data that can be
    fetched at a specific point in time. It adheres to a protocol compatible with
    the PyTorch Dataset and IterableDataset classes so that it can be used with PyTorch
    DataLoader objects.
    """

    def __init__(self, data_source: DataSource, name: Optional[str] = None):
        self.data_source = data_source
        self.name = name
        self.full_data: pd.DataFrame | pd.Series = self.data_source.fetch()
        self.timestamps: pd.Index = self.full_data.index

    def __len__(self) -> int:
        return len(self.data_source)

    def __getitem__(self, idx: pd.Timestamp | NaTType | slice) -> pd.DataFrame:
        return self._load_data(idx)

    def _load_data(self, idx: pd.Timestamp | NaTType | slice) -> pd.DataFrame: ...

    def __repr__(self) -> str:  # Improved representation for easier debugging
        return f"{self.__class__.__name__}(name={self.name}, shape={self.full_data.shape}, time_range={self.get_time_range()})"

    def get_time_range(self) -> Tuple[pd.Timestamp, pd.Timestamp]:
        """Returns the start and end timestamps of the dataset."""
        return self.timestamps.min(), self.timestamps.max()

    def __next__(self) -> Tuple[pd.Timestamp, pd.DataFrame]:
        return next(self.full_data.iterrows())


# class MultiDataset(Dataset):
#     def __init__(self, datasets: List[TimeSeriesDataset]):
#         if not isinstance(datasets, list):
#             raise TypeError("datasets must be a list.")
#         if not all(
#             isinstance(dataset, (TimeSeriesDataset, StaticDataset))
#             for dataset in datasets
#         ):
#             raise TypeError(
#                 "All elements in datasets must be TimeSeriesDataset or StaticDataset instances."
#             )

#         self.datasets = datasets
#         time_series_datasets = [
#             ds for ds in self.datasets if isinstance(ds, TimeSeriesDataset)
#         ]
#         if time_series_datasets:  # Check if there are any time series datasets
#             all_timestamps = pd.concat(
#                 [dataset.timestamps for dataset in time_series_datasets]
#             )
#             self.timestamps: List[pd.Timestamp] = sorted(list(all_timestamps.unique()))
#         else:
#             # Handle the case where there are no TimeSeriesDatasets
#             self.timestamps = []

#     def __len__(self) -> int:
#         return len(self.timestamps)

#     def __getitem__(
#         self, idx: Union[int, slice]
#     ) -> Union[Dict[str, Optional[pd.Series]], pd.DataFrame]:
#         if isinstance(idx, int):
#             if (
#                 not self.timestamps
#             ):  # Handle the case where there are no TimeSeriesDatasets
#                 data_dict: Dict[str, Optional[pd.Series]] = {}
#                 for dataset in self.datasets:
#                     data_dict[dataset.name or "unnamed"] = dataset[:]
#                 return data_dict

#             timestamp = self.timestamps[idx]
#             data_dict: Dict[str, Optional[pd.Series]] = {}
#             for dataset in self.datasets:
#                 if isinstance(dataset, TimeSeriesDataset):
#                     if timestamp in dataset.timestamps:
#                         data_dict[dataset.name or "unnamed"] = dataset[
#                             dataset.timestamps.get_loc(timestamp)
#                         ]
#                     else:
#                         data_dict[dataset.name or "unnamed"] = None
#                 elif isinstance(dataset, StaticDataset):
#                     data_dict[dataset.name or "unnamed"] = dataset[
#                         :
#                     ]  # Include all rows for static datasets

#             return data_dict
#         elif isinstance(idx, slice):

#             if (
#                 not self.timestamps
#             ):  # Handle the case where there are no TimeSeriesDatasets
#                 combined_df = pd.DataFrame()
#                 for dataset in self.datasets:
#                     combined_df = combined_df.join(dataset[:], how="outer")
#                 return combined_df

#             timestamps_slice = self.timestamps[idx]
#             combined_df = pd.DataFrame(index=timestamps_slice)
#             for dataset in self.datasets:
#                 if isinstance(dataset, TimeSeriesDataset):
#                     dataset_slice = dataset[dataset.timestamps.isin(timestamps_slice)]
#                     combined_df = combined_df.join(dataset_slice, how="left")
#                 elif isinstance(dataset, StaticDataset):
#                     combined_df = combined_df.join(
#                         dataset[:], how="left"
#                     )  # Include all rows for static datasets

#             return combined_df
#         else:
#             raise TypeError("Index must be an integer or a slice")

#     def load_data(self, data_slice: Optional[slice] = None):
#         for dataset in self.datasets:
#             dataset.load_data(data_slice)
