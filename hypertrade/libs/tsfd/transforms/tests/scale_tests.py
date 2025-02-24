import unittest

import pandas as pd
import torch

# import hypertrade.libs.debugging  # donotcommit
from hypertrade.libs.tsfd.sources.csv import CSVSource
from hypertrade.libs.tsfd.transforms import Compose, Flatten, Normalize, ToTensor


class TestSingleIndexTransforms(unittest.TestCase):

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

    def test_normalize(self) -> None:
        datasource = CSVSource(self.single_index_df)
        transforms = Compose(datasource=datasource, transforms=[Normalize()])
        transformed_df = transforms(self.single_index_df)
        self.assertIsInstance(transformed_df, pd.DataFrame)
        if isinstance(transformed_df, pd.DataFrame):
            self.assertTrue((transformed_df.iloc[2] == 0).all())

    def test_normalize_w_compose(self) -> None:
        datasource = CSVSource(self.single_index_df)
        transforms = Compose(
            datasource=datasource, transforms=[Normalize(), ToTensor(), Flatten()]
        )
        transformed_df = transforms(self.single_index_df)
        self.assertEqual(transformed_df.shape, torch.Size([20]))


class TestMultiIndexTransforms(unittest.TestCase):

    def setUp(self) -> None:
        date_index = pd.date_range(start="1/1/2018", periods=5, freq="D")
        index = pd.MultiIndex.from_arrays(
            [date_index, ["AAPL" for _ in range(5)]], names=("date", "ticker")
        )
        self.multi_index_df = pd.DataFrame(
            {
                "A": [1, 2, 3, 4, 5],
                "B": [5, 4, 3, 2, 1],
                "C": [1, 2, 3, 4, 5],
                "D": [5, 4, 3, 2, 1],
            },
            index=index,
        )

    def test_normalize(self) -> None:
        datasource = CSVSource(self.multi_index_df)
        transforms = Compose(datasource=datasource, transforms=[Normalize()])
        transformed_df = transforms(self.multi_index_df)
        self.assertIsInstance(transformed_df, pd.DataFrame)
        if isinstance(transformed_df, pd.DataFrame):
            self.assertTrue((transformed_df.iloc[2] == 0).all())

    def test_normalize_w_compose(self) -> None:
        datasource = CSVSource(self.multi_index_df)
        transforms = Compose(
            datasource=datasource, transforms=[Normalize(), ToTensor(), Flatten()]
        )
        transformed_df = transforms(self.multi_index_df)
        self.assertEqual(transformed_df.shape, torch.Size([20]))


class TestNormalizeMultiIndexSeparation(unittest.TestCase):
    """
    Ensures that normalization is applied without combining multiple symbols.
    In other words, the transform should avoid blending different tickers' stats.
    """

    def test_normalize_per_ticker(self) -> None:
        # Create a multi-index DataFrame with 2 tickers and distinct ranges
        dates = pd.date_range("2020-01-01", periods=5, freq="D")
        tickers = ["AAPL"] * 5 + ["MSFT"] * 5
        idx = pd.MultiIndex.from_arrays(
            [dates.append(dates), tickers], names=["date", "ticker"]
        )
        df = pd.DataFrame(
            {
                "price": [1, 2, 3, 4, 5, 10, 20, 30, 40, 50],
            },
            index=idx,
        )

        # Construct a CSVSource so that .mean and .std are computed from df
        datasource = CSVSource(df)

        # Apply normalization
        transform = Compose(
            datasource=datasource,
            transforms=[Normalize()],
        )
        normalized_df = transform(df)

        self.assertIsInstance(normalized_df, pd.DataFrame)
        if isinstance(normalized_df, pd.DataFrame):
            # Group by ticker and compute the mean of each group
            grouped = normalized_df.groupby(level="ticker").mean()

            # Check that each ticker is near 0 mean if genuinely normalized per ticker
            # If they were combined incorrectly, we might see offset means.
            for ticker in grouped.index:
                mean_value = grouped.loc[ticker, "price"]
                self.assertAlmostEqual(
                    mean_value,
                    0.0,
                    places=6,
                    msg=f"Ticker {ticker} mean was not ~0. Instead got {mean_value}",
                )

            # check standard dev is ~1 if desired
            std_grouped = normalized_df.groupby(level="ticker").std()
            # trunk-ignore(pyright/reportAttributeAccessIssue)
            for ticker in std_grouped.index:
                # trunk-ignore(pyright/reportAttributeAccessIssue)
                std_value = std_grouped.loc[ticker, "price"]
                self.assertAlmostEqual(
                    std_value,
                    1.0,
                    places=6,
                    msg=f"Ticker {ticker} std was not ~1. Instead got {std_value}",
                )


if __name__ == "__main__":
    unittest.main()
