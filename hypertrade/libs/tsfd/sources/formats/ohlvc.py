import pandas as pd

from hypertrade.libs.tsfd.datasets.asset import OhlvcDatasetAdapter
from hypertrade.libs.tsfd.schemas.ohlvc import ohlvc_schema
from hypertrade.libs.tsfd.sources.types import DataSourceFormat


class OHLVCDataSourceFormat(DataSourceFormat, OhlvcDatasetAdapter):

    schema = ohlvc_schema

    def ohlvc_adapter(self, df: pd.DataFrame) -> pd.DataFrame:
        return df
