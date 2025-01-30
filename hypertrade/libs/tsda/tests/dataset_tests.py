import os
import unittest

import pandas as pd
import numpy as np
import pytz

from hypertrade.libs.tsda.core.factory import DataSourceFactory
from hypertrade.libs.tsda.datasets.prices import OHLCVDataset
from hypertrade.libs.logging.setup import initialize_logging

# import hypertrade.libs.debugging  # donotcommit

nytz = pytz.timezone("America/New_York")


class TestOhlvcCsvDatasource(unittest.TestCase):

    def test_current_price_market_open(self) -> None:

        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(ws, "data/ohlvc/sample.csv")

        # Create an OCHLV data source using a CSV file
        csv_source = DataSourceFactory.create_source("csv", filepath=sample_data_path)
        # Create an OHLCV dataset
        ohlcv_dataset = OHLCVDataset(source=csv_source)

        # Fetch OCHLV data
        data = ohlcv_dataset.fetch_current_price(
            pd.Timestamp("2018-12-31 09:30:00", tz=nytz),
            ["GE", "BA"],
        )
        self.assertEquals(len(data), 2)
        self.assertEquals(data.index.to_list(), ["GE", "BA"])
        self.assertAlmostEqual(data.loc["GE"], 35.37, places=2)
        self.assertAlmostEqual(data.loc["BA"], 311.45, places=2)

    def test_current_price_market_close(self) -> None:

        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(ws, "data/ohlvc/sample.csv")

        sample_data_path = os.path.join(ws, "data/ohlvc/sample.csv")

        # Create an OCHLV data source using a CSV file
        csv_source = DataSourceFactory.create_source("csv", filepath=sample_data_path)
        # Create an OHLCV dataset
        ohlcv_dataset = OHLCVDataset(source=csv_source)

        # Fetch OCHLV data
        data = ohlcv_dataset.fetch_current_price(
            pd.Timestamp("2018-12-31 16:00:00", tz=nytz),
            ["GE", "BA"],
        )
        self.assertEquals(len(data), 2)
        self.assertEquals(data.index.to_list(), ["GE", "BA"])
        self.assertAlmostEqual(data.loc["GE"], 35.61, places=2)
        self.assertAlmostEqual(data.loc["BA"], 313.39, places=2)

    def test_current_price_before_open(self) -> None:

        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(ws, "data/ohlvc/sample.csv")

        # Create an OCHLV data source using a CSV file
        csv_data_source = DataSourceFactory.create_source(
            "csv", filepath=sample_data_path
        )
        ohlvc_data = OHLCVDataset(csv_data_source)

        # Fetch OCHLV data
        data = ohlvc_data.fetch_current_price(
            pd.Timestamp("2018-12-31 8:00:00", tz=nytz),
            ["GE", "BA"],
        )
        self.assertEquals(len(data), 2)
        self.assertEquals(data.index.to_list(), ["GE", "BA"])
        self.assertAlmostEqual(data.loc["GE"], 35.33, places=2)
        self.assertAlmostEqual(data.loc["BA"], 307.44, places=2)


if __name__ == "__main__":
    initialize_logging(level="DEBUG")
    unittest.main()
