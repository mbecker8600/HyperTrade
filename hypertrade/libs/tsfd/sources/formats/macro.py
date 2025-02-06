import pandas as pd
import pandera as pa

from hypertrade.libs.tsfd.sources.formats.types import DataSourceFormat

_global_macro_schema = pa.DataFrameSchema(
    {
        "value": pa.Column(
            float,
            checks=pa.Check.greater_than_or_equal_to(0),
        ),
    },
    index=pa.MultiIndex(
        [
            pa.Index(pd.Timestamp, name="date"),
            pa.Index(str, name="country_code"),
            pa.Index(int, name="indicator_code"),
        ]
    ),
)


class GlobalMacroFormat(DataSourceFormat):

    schema = _global_macro_schema
