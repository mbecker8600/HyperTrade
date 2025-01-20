import os
import unittest

import pandas as pd
import numpy as np

from hypertrade.libs.finance.assets import Asset
from hypertrade.libs.finance.data.datasource import CSVDataSource, OHLCVData
from hypertrade.libs.logging.setup import initialize_logging

# import hypertrade.libs.debugging  # donotcommit


class TestOhlvcCsvDatasource(unittest.TestCase):

    def test_single_point_in_time(self) -> None:

        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(ws, "data/ohlvc/sample.csv")

        # Create an OCHLV data source using a CSV file
        csv_impl = CSVDataSource(sample_data_path)
        ohlvc_data_source = OHLCVData(csv_impl)

        # Fetch OCHLV data
        data = ohlvc_data_source.fetch(
            pd.Timestamp("2018-12-31"),
            [
                Asset(sid=1, symbol="GE", asset_name="General Electric"),
                Asset(sid=2, symbol="BA", asset_name="Boeing"),
            ],
        )
        self.assertEquals(len(data), 2)
        self.assertTrue(all(data["ticker"].unique() == np.array(["GE", "BA"])))


if __name__ == "__main__":
    initialize_logging(level="DEBUG")
    unittest.main()
