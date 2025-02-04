import os
import unittest

import pandas as pd

from hypertrade.libs.tsda.sources.csv import CSVSource

# import hypertrade.libs.debugging  # donotcommit


class TestCsvDatasource(unittest.TestCase):

    def test_full_data_load(self) -> None:
        ws = os.path.dirname(__file__)
        ohlvc_sample_data_path = os.path.join(ws, "../../tests/data/ohlvc/sample.csv")

        csv_source = CSVSource(filepath=ohlvc_sample_data_path)

        full_data = csv_source.fetch()

        # Note that it is 7 columns because the date is the index
        self.assertEqual(full_data.shape, (246, 7))
        self.assertEqual(len(csv_source), 246)

    def test_partial_data_load(self) -> None:
        ws = os.path.dirname(__file__)
        ohlvc_sample_data_path = os.path.join(ws, "../../tests/data/ohlvc/sample.csv")

        csv_source = CSVSource(filepath=ohlvc_sample_data_path)
        partial_data = csv_source.fetch(timestamp=pd.Timestamp("2018-12-03"))

        # There are three symbols in the sample data so it should have 3 rows
        self.assertEqual(partial_data.shape, (3, 7))
        self.assertEqual(len(csv_source), 246)

    def test_partial_data_load_w_lookback(self) -> None:
        ws = os.path.dirname(__file__)
        ohlvc_sample_data_path = os.path.join(ws, "../../tests/data/ohlvc/sample.csv")

        csv_source = CSVSource(filepath=ohlvc_sample_data_path)

        partial_data = csv_source.fetch(
            timestamp=pd.Timestamp("2018-12-03"),
            lookback=pd.Timedelta(days=3),
        )

        # There are three symbols in the sample data so it should have 3 rows
        self.assertEqual(partial_data.shape, (9, 7))
        self.assertEqual(len(csv_source), 246)

    def test_int_index(self) -> None:
        ws = os.path.dirname(__file__)
        ohlvc_sample_data_path = os.path.join(ws, "../../tests/data/ohlvc/sample.csv")

        csv_source = CSVSource(filepath=ohlvc_sample_data_path)

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
        self.assertEqual(len(csv_source), 246)


if __name__ == "__main__":
    unittest.main()
