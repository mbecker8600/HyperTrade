import os
import unittest

import pandas as pd

from hypertrade.libs.tsfd.sources.csv import CSVSource

# import hypertrade.libs.debugging  # donotcommit


class TestCsvDatasource(unittest.TestCase):

    def setUp(self) -> None:
        ws = os.path.dirname(__file__)
        self.ohlvc_sample_data_path = os.path.join(
            ws, "../../tests/data/ohlvc/sample.csv"
        )

    def test_full_data_load(self) -> None:

        csv_source = CSVSource(filepath=self.ohlvc_sample_data_path)

        full_data = csv_source.fetch()

        # Note that it is 7 columns because the date is the index
        self.assertEqual(full_data.shape, (246, 7))
        self.assertEqual(len(csv_source), 82)

    def test_partial_data_load(self) -> None:

        csv_source = CSVSource(filepath=self.ohlvc_sample_data_path)
        partial_data = csv_source.fetch(timestamp=pd.Timestamp("2018-12-03"))

        # There are three symbols in the sample data so it should have 3 rows
        self.assertEqual(partial_data.shape, (3, 7))
        self.assertEqual(len(csv_source), 82)

    def test_int_index(self) -> None:

        csv_source = CSVSource(filepath=self.ohlvc_sample_data_path)

        partial_data = csv_source.fetch(
            timestamp=1,
        )

        # There are three symbols in the sample data so it should have 3 rows
        self.assertEqual(partial_data.shape, (3, 7))
        self.assertTrue(
            all(
                [
                    ts == pd.Timestamp("2018-09-05")
                    for ts in partial_data.index.to_list()
                ]
            )
        )
        self.assertEqual(len(csv_source), 82)

    def test_slice(self) -> None:
        csv_source = CSVSource(
            filepath=self.ohlvc_sample_data_path, index_col=["date", "ticker"]
        )

        data = csv_source.fetch(
            timestamp=slice(pd.Timestamp("2018-12-03"), pd.Timestamp("2018-12-06"))
        )

        self.assertEqual(data.shape, (9, 6))
        pass


if __name__ == "__main__":
    unittest.main()
