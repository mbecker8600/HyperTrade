import pandera as pa
import pandas as pd


headline_schema = pa.DataFrameSchema(
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
