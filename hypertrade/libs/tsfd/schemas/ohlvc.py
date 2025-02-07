import pandera as pa
import pandas as pd

ohlvc_schema = pa.DataFrameSchema(
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
