from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
from pandas._libs.tslibs.nattype import NaTType


class DataSource(ABC):
    @abstractmethod
    def fetch(
        self,
        timestamp: Optional[pd.Timestamp | NaTType | slice | int] = None,
        lookback: Optional[pd.Timedelta] = None,
    ) -> pd.DataFrame | pd.Series: ...

    @abstractmethod
    def __len__(self) -> int: ...
