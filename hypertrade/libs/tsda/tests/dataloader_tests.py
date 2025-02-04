import os
import unittest

from hypertrade.libs.tsda.datasets.asset import OHLVCDataset
from hypertrade.libs.tsda.sources.csv import CSVSource

# import hypertrade.libs.debugging  # donotcommit


class TestOhlvcCsvDatasource(unittest.TestCase):

    def setUp(self) -> None:
        ws = os.path.dirname(__file__)
        self.ohlvc_sample_data_path = os.path.join(ws, "data/ohlvc/sample.csv")

    def test_basic_indexing(self) -> None:

        ohlvc_dataset = OHLVCDataset(
            CSVSource(filepath=self.ohlvc_sample_data_path), name="ohlvc"
        )

        for batch in ohlvc_dataset:
            print(batch)
            break


if __name__ == "__main__":
    unittest.main()
