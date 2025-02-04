import os
import unittest

import pandas as pd

# import hypertrade.libs.debugging  # donotcommit
from hypertrade.libs.tsda.datasets.asset import OHLVCDataset
from hypertrade.libs.tsda.sources.csv import CSVSource


class TestOHLVCCsvDataSet(unittest.TestCase):

    def setUp(self) -> None:
        ws = os.path.dirname(__file__)
        self.ohlvc_sample_data_path = os.path.join(
            ws, "../../tests/data/ohlvc/sample.csv"
        )

    def test_single_index(self) -> None:

        ohlvc_dataset = OHLVCDataset(
            data_source=CSVSource(filepath=self.ohlvc_sample_data_path), name="ohlvc"
        )

        data = ohlvc_dataset[pd.Timestamp("2018-12-03")]
        self.assertEqual(data.shape, (3, 7))
        self.assertTrue(
            all([ts == pd.Timestamp("2018-12-03") for ts in data.index.to_list()])
        )
        self.assertEqual(
            data[data["ticker"] == "GE"].at[pd.Timestamp("2018-12-03"), "open"], 35.42
        )

    def test_filtering(self) -> None:

        ohlvc_dataset = OHLVCDataset(
            data_source=CSVSource(filepath=self.ohlvc_sample_data_path),
            name="ohlvc",
            symbols=["GE", "BA"],
        )

        data = ohlvc_dataset[pd.Timestamp("2018-12-03")]
        self.assertEqual(data.shape, (2, 7))
        self.assertTrue(
            all([ts == pd.Timestamp("2018-12-03") for ts in data.index.to_list()])
        )

    def test_iterator(self) -> None:
        ohlvc_dataset = OHLVCDataset(
            data_source=CSVSource(filepath=self.ohlvc_sample_data_path), name="ohlvc"
        )
        for data in ohlvc_dataset:
            self.assertEqual(data.shape, (3, 7))

    # def test_slice(self) -> None:
    #     ws = os.path.dirname(__file__)
    #     ohlvc_sample_data_path = os.path.join(ws, "../../tests/data/ohlvc/sample.csv")

    #     ohlvc_dataset = OHLVCDataset(
    #         data_source=CSVSource(filepath=ohlvc_sample_data_path), name="ohlvc"
    #     )

    #     data = ohlvc_dataset[pd.Timestamp("2018-12-03") : pd.Timestamp("2018-12-06")]


if __name__ == "__main__":
    unittest.main()
