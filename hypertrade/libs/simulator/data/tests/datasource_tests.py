import os
import unittest

import pandas as pd
import pytz

from hypertrade.libs.logging.setup import initialize_logging
from hypertrade.libs.simulator.assets import Asset
from hypertrade.libs.simulator.data.datasource import CSVDataSource, OHLCVDataset

# import hypertrade.libs.debugging  # donotcommit

nytz = pytz.timezone("America/New_York")


class TestOhlvcCsvDatasource(unittest.TestCase):

    def test_current_price_market_open(self) -> None:

        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(ws, "data/ohlvc/sample.csv")

        # Create an OCHLV data source using a CSV file
        csv_impl = CSVDataSource(sample_data_path, index_col=["date", "ticker"])
        ohlvc_data_source = OHLCVDataset(csv_impl)

        # Fetch OCHLV data
        data = ohlvc_data_source.fetch_current_price(
            pd.Timestamp("2018-12-31 09:30:00", tz=nytz),
            [
                Asset(sid=1, symbol="GE", asset_name="General Electric"),
                Asset(sid=2, symbol="BA", asset_name="Boeing"),
            ],
        )
        self.assertEquals(len(data), 2)
        self.assertEquals(data.index.to_list(), ["GE", "BA"])
        self.assertAlmostEqual(data.loc["GE"], 35.37, places=2)
        self.assertAlmostEqual(data.loc["BA"], 311.45, places=2)

    def test_current_price_market_close(self) -> None:

        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(ws, "data/ohlvc/sample.csv")

        # Create an OCHLV data source using a CSV file
        csv_data_source = CSVDataSource(sample_data_path, index_col=["date", "ticker"])
        ohlvc_data = OHLCVDataset(csv_data_source)

        # Fetch OCHLV data
        data = ohlvc_data.fetch_current_price(
            pd.Timestamp("2018-12-31 16:00:00", tz=nytz),
            [
                Asset(sid=1, symbol="GE", asset_name="General Electric"),
                Asset(sid=2, symbol="BA", asset_name="Boeing"),
            ],
        )
        self.assertEquals(len(data), 2)
        self.assertEquals(data.index.to_list(), ["GE", "BA"])
        self.assertAlmostEqual(data.loc["GE"], 35.61, places=2)
        self.assertAlmostEqual(data.loc["BA"], 313.39, places=2)

    def test_current_price_before_oppen(self) -> None:

        ws = os.path.dirname(__file__)
        sample_data_path = os.path.join(ws, "data/ohlvc/sample.csv")

        # Create an OCHLV data source using a CSV file
        csv_data_source = CSVDataSource(sample_data_path, index_col=["date", "ticker"])
        ohlvc_data = OHLCVDataset(csv_data_source)

        # Fetch OCHLV data
        data = ohlvc_data.fetch_current_price(
            pd.Timestamp("2018-12-31 8:00:00", tz=nytz),
            [
                Asset(sid=1, symbol="GE", asset_name="General Electric"),
                Asset(sid=2, symbol="BA", asset_name="Boeing"),
            ],
        )
        self.assertEquals(len(data), 2)
        self.assertEquals(data.index.to_list(), ["GE", "BA"])
        self.assertAlmostEqual(data.loc["GE"], 35.33, places=2)
        self.assertAlmostEqual(data.loc["BA"], 307.44, places=2)


if __name__ == "__main__":
    initialize_logging(level="DEBUG")
    unittest.main()
