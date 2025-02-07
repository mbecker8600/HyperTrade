from typing import List, Optional, Protocol

import pandas as pd
from pandas._libs.tslibs.nattype import NaTType

from hypertrade.libs.tsfd.datasets.types import TimeSeriesDataset
from hypertrade.libs.tsfd.schemas.ohlvc import ohlvc_schema
from hypertrade.libs.tsfd.sources.types import DataSource


class SupportsOHLVCDataset(Protocol):

    @classmethod
    def ohlvc_adapter(cls, df: pd.DataFrame) -> pd.DataFrame: ...


class OHLVCDataset(TimeSeriesDataset):

    _schema = ohlvc_schema

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
        if self.symbols is not None:
            data = data.loc[pd.IndexSlice[:, self.symbols], :]
        if isinstance(data, pd.Series):
            data = data.to_frame().T
        self._schema.validate(data)
        return data
