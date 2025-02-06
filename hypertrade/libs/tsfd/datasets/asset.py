from typing import List, Optional, Protocol

import pandas as pd
from pandas._libs.tslibs.nattype import NaTType

from hypertrade.libs.tsfd.datasets.types import TimeSeriesDataset
from hypertrade.libs.tsfd.sources.types import DataSource


class SupportsOHLVCDataset(Protocol):

    @classmethod
    def ohlvc_adapter(cls, df: pd.DataFrame) -> pd.DataFrame: ...


class OHLVCDataset(TimeSeriesDataset):
    def __init__(
        self,
        data_source: DataSource,
        name: Optional[str] = None,
        symbols: Optional[List[str]] = None,
    ):
        self.symbols = symbols
        super().__init__(data_source, name)

    def _load_data(self, idx: pd.Timestamp | NaTType | slice | int) -> pd.DataFrame:
        data = self.data_source.fetch(timestamp=idx)
        if isinstance(data, pd.Series):
            data = data.to_frame().T
        if self.symbols is not None:
            data = data[data["ticker"].isin(self.symbols)]
        if isinstance(data, pd.Series):
            data = data.to_frame().T
        return data
