import os
import unittest

import pandas as pd

# import hypertrade.libs.debugging  # donotcommit
from hypertrade.libs.tsda.datasets.asset import OHLVCDataset
from hypertrade.libs.tsda.sources.csv import CSVSource


class TestOHLVCCsvDataSet(unittest.TestCase):

    def test_single_index(self) -> None:
        ws = os.path.dirname(__file__)
        ohlvc_sample_data_path = os.path.join(ws, "../../tests/data/ohlvc/sample.csv")

        ohlvc_dataset = OHLVCDataset(
            data_source=CSVSource(filepath=ohlvc_sample_data_path), name="ohlvc"
        )

        data = ohlvc_dataset[pd.Timestamp("2018-12-03")]
        self.assertEquals(data.shape, (3, 7))

    # def test_slice(self) -> None:
    #     ws = os.path.dirname(__file__)
    #     ohlvc_sample_data_path = os.path.join(ws, "../../tests/data/ohlvc/sample.csv")

    #     ohlvc_dataset = OHLVCDataset(
    #         data_source=CSVSource(filepath=ohlvc_sample_data_path), name="ohlvc"
    #     )

    #     data = ohlvc_dataset[pd.Timestamp("2018-12-03") : pd.Timestamp("2018-12-06")]


if __name__ == "__main__":
    unittest.main()
