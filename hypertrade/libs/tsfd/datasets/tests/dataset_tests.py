import os
import unittest

import pandas as pd
import pytz

# import hypertrade.libs.debugging  # donotcommit
from hypertrade.libs.tsfd.datasets.asset import OHLVCDataset, PricesDataset
from hypertrade.libs.tsfd.sources.csv import CSVSource
from hypertrade.libs.tsfd.sources.formats.ohlvc import OHLVCDataSourceFormat


class TestOHLVCCsvDataSet(unittest.TestCase):

    def setUp(self) -> None:
        ws = os.path.dirname(__file__)
        self.ohlvc_sample_data_path = os.path.join(
            ws, "../../tests/data/ohlvc/sample.csv"
        )

    def test_single_index(self) -> None:

        ohlvc_dataset = OHLVCDataset(
            data_source=OHLVCDataSourceFormat(
                CSVSource(filepath=self.ohlvc_sample_data_path),
            ),
            name="ohlvc",
        )

        data = ohlvc_dataset[pd.Timestamp("2018-12-03")]
        self.assertEqual(data.shape, (3, 6))
        self.assertTrue(
            all(
                [
                    ts == pd.Timestamp("2018-12-03")
                    for ts in data.index.get_level_values(0).to_list()
                ]
            )
        )
        self.assertEqual(data.loc[pd.IndexSlice[:, ["GE"]], :]["open"].values[0], 35.42)

    def test_filtering(self) -> None:

        ohlvc_dataset = OHLVCDataset(
            data_source=OHLVCDataSourceFormat(
                CSVSource(filepath=self.ohlvc_sample_data_path)
            ),
            name="ohlvc",
            symbols=["GE", "BA"],
        )

        data = ohlvc_dataset[pd.Timestamp("2018-12-03")]
        self.assertEqual(data.shape, (2, 6))
        self.assertTrue(
            all(
                [
                    ts == pd.Timestamp("2018-12-03")
                    for ts in data.index.get_level_values(0).to_list()
                ]
            )
        )

    def test_iterator(self) -> None:
        ohlvc_dataset = OHLVCDataset(
            data_source=OHLVCDataSourceFormat(
                CSVSource(filepath=self.ohlvc_sample_data_path)
            ),
            name="ohlvc",
        )
        for data in ohlvc_dataset:
            self.assertEqual(data.shape, (3, 6))

    # def test_slice(self) -> None:
    #     ohlvc_dataset = OHLVCDataset(
    #         data_source=CSVSource(filepath=self.ohlvc_sample_data_path), name="ohlvc"
    #     )

    #     data = ohlvc_dataset[pd.Timestamp("2018-12-03") : pd.Timestamp("2018-12-06")]


class TestPricesCsvDataSet(unittest.TestCase):
    def setUp(self) -> None:
        ws = os.path.dirname(__file__)
        ohlvc_sample_data_path = os.path.join(ws, "../../tests/data/ohlvc/sample.csv")
        self.prices_dataset = PricesDataset(
            data_source=OHLVCDataSourceFormat(
                CSVSource(filepath=ohlvc_sample_data_path),
            ),
            symbols=["GE", "BA"],
            name="prices",
        )
        self.nytz = pytz.timezone("America/New_York")

    def test_current_price_market_open(self) -> None:

        # Fetch OCHLV data
        # TODO: Add timezone awareness, tz=self.nytz
        data = self.prices_dataset[pd.Timestamp("2018-12-31 09:30:00")]
        self.assertEquals(len(data), 2)
        self.assertEquals(data.index.to_list(), ["GE", "BA"])
        self.assertAlmostEquals(data.loc["GE"], 35.37, places=2)
        self.assertAlmostEquals(data.loc["BA"], 311.45, places=2)

    def test_current_price_market_close(self) -> None:

        # Fetch OCHLV data
        # TODO: Add timezone awareness, tz=self.nytz
        data = self.prices_dataset[pd.Timestamp("2018-12-31 16:00:00")]
        self.assertEquals(len(data), 2)
        self.assertEquals(data.index.to_list(), ["GE", "BA"])
        self.assertAlmostEquals(data.loc["GE"], 35.61, places=2)
        self.assertAlmostEquals(data.loc["BA"], 313.39, places=2)

    def test_current_price_before_oppen(self) -> None:

        # Fetch OCHLV data
        # TODO: Add timezone awareness, tz=self.nytz
        data = self.prices_dataset[pd.Timestamp("2018-12-31 8:00:00")]
        self.assertEquals(len(data), 2)
        self.assertEquals(data.index.to_list(), ["GE", "BA"])
        self.assertAlmostEquals(data.loc["GE"], 35.33, places=2)
        self.assertAlmostEquals(data.loc["BA"], 307.44, places=2)


if __name__ == "__main__":
    unittest.main()
