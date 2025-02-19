import pandas as pd
import pandera as pa

headline_schema = pa.DataFrameSchema(
    {
        "headline": pa.Column(
            str,
        ),
        "preview": pa.Column(
            str,
        ),
    },
    index=pa.Index(pd.DatetimeTZDtype(tz="UTC"), name="date"),
)
