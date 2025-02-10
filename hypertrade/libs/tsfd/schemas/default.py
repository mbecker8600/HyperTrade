import pandas as pd
import pandera as pa

default_schema = pa.DataFrameSchema(
    index=pa.MultiIndex([pa.Index(pd.Timestamp, name="date")]),
)
