import pandas as pd
import pandera as pa

prices_schema = pa.DataFrameSchema(
    {
        "price": pa.Column(
            float,
            checks=pa.Check.greater_than_or_equal_to(0),
        ),
    },
    index=pa.MultiIndex(
        [pa.Index(pd.Timestamp, name="date"), pa.Index(str, name="ticker")]
    ),
)
