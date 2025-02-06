import pandas as pd
import pandera as pa

from hypertrade.libs.tsfd.datasets.asset import SupportsOHLVCDataset
from hypertrade.libs.tsfd.sources.formats.types import DataSourceFormat

_ohlvc_schema = pa.DataFrameSchema(
    {
        "open": pa.Column(
            float,
            checks=pa.Check.greater_than_or_equal_to(0),
        ),
        "high": pa.Column(
            float,
            checks=pa.Check.greater_than_or_equal_to(0),
        ),
        "low": pa.Column(
            float,
            checks=pa.Check.greater_than_or_equal_to(0),
        ),
        "close": pa.Column(
            float,
            checks=pa.Check.greater_than_or_equal_to(0),
        ),
        "volume": pa.Column(
            float,
            checks=pa.Check.greater_than_or_equal_to(0),
        ),
    },
    index=pa.MultiIndex(
        [pa.Index(pd.Timestamp, name="date"), pa.Index(str, name="ticker")]
    ),
)


class OHLVCFormat(DataSourceFormat, SupportsOHLVCDataset):

    schema = _ohlvc_schema

    @classmethod
    def ohlvc_adapter(cls, df: pd.DataFrame) -> pd.DataFrame:
        return df
