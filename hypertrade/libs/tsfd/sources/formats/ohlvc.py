import pandas as pd
from pandas._libs.tslibs.nattype import NaTType

from hypertrade.libs.tsfd.datasets.asset import (
    OhlvcDatasetAdapter,
    PricesDatasetAdapter,
)
from hypertrade.libs.tsfd.schemas.ohlvc import ohlvc_schema
from hypertrade.libs.tsfd.sources.types import DataSource, DataSourceFormat, Granularity


class OHLVCDataSourceFormat(
    DataSourceFormat, OhlvcDatasetAdapter, PricesDatasetAdapter
):
    def __init__(
        self, datasource: DataSource, granularity: Granularity = Granularity.DAILY
    ):
        super().__init__(datasource)
        self.granularity = granularity

    schema = ohlvc_schema

    def ohlvc_adapter(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def prices_adapter(
        self, idx: pd.Timestamp | NaTType | slice | int, df: pd.DataFrame
    ) -> pd.DataFrame:
        if isinstance(idx, pd.Timestamp) and idx.tzinfo is None:
            idx = idx.tz_localize("UTC")
        return df
