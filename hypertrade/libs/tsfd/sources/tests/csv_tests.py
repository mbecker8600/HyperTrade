import os
import unittest

import pandas as pd

from hypertrade.libs.tsfd.sources.csv import CSVSource
from hypertrade.libs.tsfd.sources.formats.news import HeadlineDataSourceFormat
from hypertrade.libs.tsfd.sources.formats.ohlvc import OHLVCDataSourceFormat

# import hypertrade.libs.debugging  # donotcommit


class TestOHLVCCsvDatasource(unittest.TestCase):
    """Test the CSVSource class with OHLVCFormat"""

    def setUp(self) -> None:
        ws = os.path.dirname(__file__)
        self.ohlvc_sample_data_path = os.path.join(
            ws, "../../tests/data/ohlvc/sample.csv"
        )
        self.bad_schema_ohlvc_sample_data_path = os.path.join(
            ws, "../../tests/data/ohlvc/bad_schema.csv"
        )

    def test_bad_schema(self) -> None:
        with self.assertRaises(ValueError):
            source = OHLVCDataSourceFormat(
                CSVSource(filepath=self.bad_schema_ohlvc_sample_data_path)
            )
            source.fetch()

    def test_full_data_load(self) -> None:

        csv_source = OHLVCDataSourceFormat(
            CSVSource(filepath=self.ohlvc_sample_data_path)
        )

        full_data = csv_source.fetch()

        # Note that it is 7 columns because the date is the index
        self.assertEqual(full_data.shape, (246, 6))
        self.assertEqual(len(csv_source), 82)

    def test_partial_data_load(self) -> None:

        csv_source = OHLVCDataSourceFormat(
            CSVSource(filepath=self.ohlvc_sample_data_path)
        )
        partial_data = csv_source.fetch(timestamp=pd.Timestamp("2018-12-03"))

        # There are three symbols in the sample data so it should have 3 rows
        self.assertEqual(partial_data.shape, (3, 6))
        self.assertEqual(len(csv_source), 82)

    def test_int_index(self) -> None:

        csv_source = OHLVCDataSourceFormat(
            CSVSource(filepath=self.ohlvc_sample_data_path)
        )

        partial_data = csv_source.fetch(
            timestamp=1,
        )

        # There are three symbols in the sample data so it should have 3 rows
        self.assertEqual(partial_data.shape, (3, 6))
        self.assertTrue(
            all(
                [
                    ts == pd.Timestamp("2018-09-05")
                    for ts in partial_data.index.get_level_values(0).to_list()
                ]
            )
        )
        self.assertEqual(len(csv_source), 82)

    def test_slice(self) -> None:
        csv_source = OHLVCDataSourceFormat(
            CSVSource(filepath=self.ohlvc_sample_data_path)
        )

        data = csv_source.fetch(
            timestamp=slice(pd.Timestamp("2018-12-03"), pd.Timestamp("2018-12-06"))
        )

        # Start index: The slice includes the element at the start index.
        # End index: The slice goes up to, but does not include, the element at the end index.
        self.assertEqual(data.shape, (6, 6))


class TestHeadlineCsvDatasource(unittest.TestCase):
    """Test the CSVSource class with HeadlineFormat"""

    def setUp(self) -> None:
        ws = os.path.dirname(__file__)
        ohlvc_sample_data_path = os.path.join(
            ws, "../../tests/data/news/headline_sample.csv"
        )
        self.csv_source = HeadlineDataSourceFormat(
            CSVSource(filepath=ohlvc_sample_data_path)
        )

    def test_full_data_load(self) -> None:

        full_data = self.csv_source.fetch()

        # Note that it is 7 columns because the date is the index
        self.assertEqual(full_data.shape, (2800, 2))
        self.assertEqual(len(self.csv_source), 2474)

    def test_partial_data_load(self) -> None:

        partial_data = self.csv_source.fetch(
            timestamp=pd.Timestamp("2020-07-17 19:51:00")
        )
        self.assertEqual(partial_data.shape, (1, 2))

    def test_int_index(self) -> None:

        partial_data = self.csv_source.fetch(
            timestamp=1,
        )

        # There are three symbols in the sample data so it should have 3 rows
        self.assertEqual(partial_data.shape, (2, 2))
        self.assertTrue(
            all(
                [
                    ts == pd.Timestamp("2017-12-22 19:07:00")
                    for ts in partial_data.index.to_list()
                ]
            )
        )

    def test_slice(self) -> None:
        data = self.csv_source.fetch(
            timestamp=slice(pd.Timestamp("2020-07-15"), pd.Timestamp("2020-07-17"))
        )

        self.assertEqual(data.shape, (8, 2))


if __name__ == "__main__":
    unittest.main()
