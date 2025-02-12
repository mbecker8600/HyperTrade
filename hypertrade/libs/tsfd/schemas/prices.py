import pandera as pa

prices_schema = pa.DataFrameSchema(
    {
        "price": pa.Column(
            float,
            checks=pa.Check.greater_than_or_equal_to(0),
        ),
    },
    index=pa.Index(str, name="ticker"),
)
