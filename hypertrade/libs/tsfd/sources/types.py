from abc import ABC, abstractmethod
from typing import Optional, Type

import pandas as pd
from pandas._libs.tslibs.nattype import NaTType

from hypertrade.libs.tsfd.sources.formats.types import DataSourceFormat


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
    def format(self) -> Type[DataSourceFormat]: ...
