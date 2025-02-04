from typing import List, Optional

import pandas as pd
from pandas._libs.tslibs.nattype import NaTType

from hypertrade.libs.tsda.datasets.types import TimeSeriesDataset
from hypertrade.libs.tsda.sources.types import DataSource


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
        if self.symbols is not None:
            data = data[data["ticker"].isin(self.symbols)]
        if isinstance(data, pd.Series):
            data = data.to_frame().T
        return data
