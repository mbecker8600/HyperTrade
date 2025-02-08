import pandas as pd

from hypertrade.libs.tsfd.datasets.asset import SupportsOHLVCDataset
from hypertrade.libs.tsfd.schemas.ohlvc import ohlvc_schema
from hypertrade.libs.tsfd.sources.formats.types import DataSourceFormat


class OHLVCFormat(DataSourceFormat, SupportsOHLVCDataset):

    schema = ohlvc_schema

    @classmethod
    def ohlvc_adapter(cls, df: pd.DataFrame) -> pd.DataFrame:
        return df
