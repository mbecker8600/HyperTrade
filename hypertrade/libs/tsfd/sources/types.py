from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Optional

import pandas as pd
import pandera as pa
from pandas._libs.tslibs.nattype import NaTType


class DataSource(ABC):

    @abstractmethod
    def fetch(
        self,
        timestamp: Optional[pd.Timestamp | NaTType | slice | int] = None,
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
    """Base class for all data source format decorators on top of a DataSource"""

    schema: ClassVar[pa.DataFrameSchema]

    def __init__(self, datasource: DataSource):
        self._datasource = datasource
        self._datasource.format = self

    def fetch(
        self,
        timestamp: Optional[pd.Timestamp | NaTType | slice | int] = None,
    ) -> pd.DataFrame:
        data = self._datasource.fetch(timestamp)
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
