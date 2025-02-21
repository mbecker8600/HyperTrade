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
            self.assertEqual(transformed_df.shape, (5, 8))


if __name__ == "__main__":
    unittest.main()
