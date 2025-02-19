import pandas as pd
import pandera as pa

tick_schema = pa.DataFrameSchema(
    {
        "price": pa.Column(
            float,
            checks=pa.Check.greater_than_or_equal_to(0),
        ),
        "quantity": pa.Column(
            float,
            checks=pa.Check.greater_than_or_equal_to(0),
        ),
        "ticker": pa.Column(str),
        "date": pa.Column(pd.Timestamp),
    }
)
