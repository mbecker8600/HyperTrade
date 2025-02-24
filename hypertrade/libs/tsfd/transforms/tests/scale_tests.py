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


if __name__ == "__main__":
    unittest.main()
