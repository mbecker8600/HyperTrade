import unittest

import pandas as pd

# import hypertrade.libs.debugging  # donotcommit
from hypertrade.libs.tsfd.sources.csv import CSVSource
from hypertrade.libs.tsfd.transforms import Compose, RollingFeatures


class TestSingleIndexRollingFeatures(unittest.TestCase):

    def setUp(self) -> None:
        self.date_index = pd.date_range(start="1/1/2018", periods=5, freq="D")
        self.single_index_df = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5],
                "B": [5, 4, 3, 2, 1],
                "C": [1, 2, 3, 4, 5],
                "D": [5, 4, 3, 2, 1],
            },
            index=self.date_index,
        )
        self.single_index_df.index.name = "date"

    def test_moving_average(self) -> None:
        datasource = CSVSource(self.single_index_df)
        transforms = Compose(
            datasource=datasource, transforms=[RollingFeatures(window=3)]
        )
        transformed_df = transforms(self.single_index_df)
        self.assertIsInstance(transformed_df, pd.DataFrame)
        if isinstance(transformed_df, pd.DataFrame):
            self.assertEqual(transformed_df.shape, (1, 8))


class TestRollingFeaturesEdgeCases(unittest.TestCase):
    def test_rolling_window_too_large(self) -> None:
        df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})
        datasource = CSVSource(df)
        transforms = Compose(
            datasource=datasource, transforms=[RollingFeatures(window=10)]
        )
        with self.assertRaises(ValueError):
            transforms(df)


class TestMultiIndexRollingFeatures(unittest.TestCase):
    def test_multiindex_separate(self) -> None:
        # Create a synthetic DataFrame: 2 tickers x 5 dates = 10 rows
        dates = pd.date_range("2022-01-01", periods=5, freq="D")
        tickers = ["AAPL"] * 5 + ["MSFT"] * 5
        idx = pd.MultiIndex.from_arrays(
            [dates.append(dates), tickers], names=["date", "ticker"]
        )
        df = pd.DataFrame({"value": [1, 2, 3, 4, 5, 10, 20, 30, 40, 50]}, index=idx)

        # RollingFeatures with window=3
        datasource = CSVSource(df)
        transforms = Compose(
            datasource=datasource,
            transforms=[RollingFeatures(window=3, groupby_level="ticker")],
        )

        # Apply transform
        rolled_df = transforms(df)

        # RollingFeatures keeps only the latest row after calculations,
        # so we expect shape=(2, 2) if each ticker ends up with 1 final row.
        self.assertEqual(
            rolled_df.shape, (2, 2), f"Got shape {rolled_df.shape} instead of (2, 2)."
        )


if __name__ == "__main__":
    unittest.main()
