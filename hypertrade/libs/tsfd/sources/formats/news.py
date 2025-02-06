import pandas as pd
import pandera as pa

from hypertrade.libs.tsfd.sources.formats.types import DataSourceFormat

_headline_schema = pa.DataFrameSchema(
    {
        "headline": pa.Column(
            str,
        ),
        "preview": pa.Column(
            str,
        ),
    },
    index=pa.Index(pd.Timestamp, name="date"),
)


class HeadlineFormat(DataSourceFormat):

    schema = _headline_schema
