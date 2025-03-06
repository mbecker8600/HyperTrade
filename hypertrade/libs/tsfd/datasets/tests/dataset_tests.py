import os
import unittest

import exchange_calendars as xcals
import pandas as pd
import pytz
from torch import Size
from torch.utils.data import DataLoader

# import hypertrade.libs.debugging  # donotcommit
from hypertrade.libs.tsfd.datasets.asset import OHLVCDataset, PricesDataset
from hypertrade.libs.tsfd.sources.csv import CSVSource
from hypertrade.libs.tsfd.sources.formats.ohlvc import OHLVCDataSourceFormat
from hypertrade.libs.tsfd.transforms import Flatten, RollingFeatures, ToTensor
from hypertrade.libs.tsfd.transforms.interface import Compose
from hypertrade.libs.tsfd.transforms.scale import Normalize
from hypertrade.libs.tsfd.transforms.util import DropFeature


class TestOHLVCCsvDataSet(unittest.TestCase):

    def setUp(self) -> None:
        ws = os.path.dirname(__file__)
        self.ohlvc_sample_data_path = os.path.join(
            ws, "../../tests/data/ohlvc/sample.csv"
        )
        self.cal = xcals.get_calendar("XNYS")
        self.tz = pytz.timezone("America/New_York")

    def test_single_index(self) -> None:

        ohlvc_dataset = OHLVCDataset(
            data_source=OHLVCDataSourceFormat(
                CSVSource(source=self.ohlvc_sample_data_path),
            ),
            name="ohlvc",
            trading_calendar=self.cal,
        )

        data = ohlvc_dataset[pd.Timestamp("2018-12-03", tz=self.tz)]
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(data.shape, (3, 6))
        if isinstance(data, pd.DataFrame):
            self.assertTrue(
                all(
                    [
                        ts == pd.Timestamp("2018-12-03", tz=self.tz)
                        for ts in data.index.get_level_values(0).to_list()
                    ]
                )
            )
            self.assertEqual(
                data.loc[pd.IndexSlice[:, ["GE"]], :]["open"].values[0], 35.42
            )

    def test_filtering(self) -> None:

        ohlvc_dataset = OHLVCDataset(
            data_source=OHLVCDataSourceFormat(
                CSVSource(source=self.ohlvc_sample_data_path)
            ),
            name="ohlvc",
            trading_calendar=self.cal,
            symbols=["GE", "BA"],
        )

        data = ohlvc_dataset[pd.Timestamp("2018-12-03", tz=self.tz)]
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(data.shape, (2, 6))
        if isinstance(data, pd.DataFrame):
            self.assertTrue(
                all(
                    [
                        ts == pd.Timestamp("2018-12-03", tz=self.tz)
                        for ts in data.index.get_level_values(0).to_list()
                    ]
                )
            )

    def test_iterator(self) -> None:
        ohlvc_dataset = OHLVCDataset(
            data_source=OHLVCDataSourceFormat(
                CSVSource(source=self.ohlvc_sample_data_path)
            ),
            trading_calendar=self.cal,
            name="ohlvc",
        )
        for data in ohlvc_dataset:
            self.assertEqual(data.shape, (3, 6))

    def test_transforms(self) -> None:
        datasource = CSVSource(source=self.ohlvc_sample_data_path)
        ohlvc_dataset = OHLVCDataset(
            data_source=OHLVCDataSourceFormat(
                datasource=datasource,
            ),
            trading_calendar=self.cal,
            name="ohlvc",
            transforms=Compose(
                datasource=datasource,
                transforms=[
                    DropFeature("lastupdated"),
                    Normalize(),
                    RollingFeatures(window=3, metric="mean", groupby_level="ticker"),
                    ToTensor(),
                    Flatten(),
                ],
            ),
        )
        dl = DataLoader(ohlvc_dataset, batch_size=2, drop_last=True)
        for i, data in enumerate(dl):
            # Shape is 30 because we have 5 features (x2 with 1 new rolling featgures) and 3 symbols
            self.assertEqual(
                data.shape,
                Size([2, 30]),
                msg=f"Batch {i} failed because of shape {data.shape} != (2, 30)",
            )


class TestPricesCsvDataSet(unittest.TestCase):
    def setUp(self) -> None:
        ws = os.path.dirname(__file__)
        ohlvc_sample_data_path = os.path.join(ws, "../../tests/data/ohlvc/sample.csv")
        self.cal = xcals.get_calendar("XNYS")
        self.prices_dataset = PricesDataset(
            data_source=OHLVCDataSourceFormat(
                CSVSource(source=ohlvc_sample_data_path),
            ),
            symbols=["GE", "BA"],
            name="prices",
            trading_calendar=self.cal,
        )
        self.nytz = pytz.timezone("America/New_York")

    def test_current_price_market_open(self) -> None:

        # Fetch OCHLV data
        data = self.prices_dataset[pd.Timestamp("2018-12-31 09:30:00", tz=self.nytz)]
        self.assertIsInstance(data, pd.DataFrame)
        self.assertEqual(len(data), 2)
        if isinstance(data, pd.DataFrame):
            self.assertEqual(set(data.index.to_list()), set(["GE", "BA"]))
            self.assertEqual(data.loc["GE"].values[0], 35.37)
            self.assertEqual(data.loc["BA"].values[0], 311.45)

    def test_current_price_market_close(self) -> None:

        # Fetch OCHLV data
        data = self.prices_dataset[pd.Timestamp("2018-12-31 16:00:00", tz=self.nytz)]
        self.assertEqual(len(data), 2)
        self.assertIsInstance(data, pd.DataFrame)
        if isinstance(data, pd.DataFrame):
            self.assertEqual(set(data.index.to_list()), set(["GE", "BA"]))
            self.assertEqual(data.loc["GE"].values[0], 35.61)
            self.assertEqual(data.loc["BA"].values[0], 313.39)

    def test_current_price_before_open(self) -> None:

        # Fetch OCHLV data
        data = self.prices_dataset[pd.Timestamp("2018-12-31 8:00:00", tz=self.nytz)]
        self.assertEqual(len(data), 2)
        self.assertIsInstance(data, pd.DataFrame)
        if isinstance(data, pd.DataFrame):
            self.assertEqual(set(data.index.to_list()), set(["GE", "BA"]))
            self.assertEqual(data.loc["GE"].values[0], 35.33)
            self.assertEqual(data.loc["BA"].values[0], 307.44)


class TestObservationShape(unittest.TestCase):
    def setUp(self) -> None:
        ws = os.path.dirname(__file__)
        ohlvc_sample_data_path = os.path.join(ws, "../../tests/data/ohlvc/sample.csv")
        self.cal = xcals.get_calendar("XNYS")
        self.nytz = pytz.timezone("America/New_York")
        self.datasource = OHLVCDataSourceFormat(
            CSVSource(source=ohlvc_sample_data_path),
        )

    def test_no_transforms(self) -> None:
        dataset_no_transforms = OHLVCDataset(
            data_source=self.datasource,
            name="no_transforms",
            trading_calendar=self.cal,
        )

        data = dataset_no_transforms[pd.Timestamp("2018-12-31 8:00:00", tz=self.nytz)]
        self.assertEqual(data.shape, dataset_no_transforms.observation_shape)
        self.assertEqual(data.shape, (3, 6))

    def test_normalization_transforms(self) -> None:
        dataset_normalization_transforms = OHLVCDataset(
            data_source=self.datasource,
            name="normalization_transforms",
            trading_calendar=self.cal,
            # BUG: Make the transform work when not using the compose function
            transforms=Compose(
                datasource=self.datasource,
                transforms=[
                    Normalize(),
                ],
            ),
        )

        data = dataset_normalization_transforms[
            pd.Timestamp("2018-12-31 8:00:00", tz=self.nytz)
        ]
        self.assertEqual(data.shape, dataset_normalization_transforms.observation_shape)
        self.assertEqual(data.shape, (3, 6))

    def test_drop_feature_transforms(self) -> None:
        dataset_normalization_transforms = OHLVCDataset(
            data_source=self.datasource,
            trading_calendar=self.cal,
            name="normalization_transforms",
            transforms=Compose(
                datasource=self.datasource,
                transforms=[
                    DropFeature(feature="lastupdated"),
                ],
            ),
        )

        data = dataset_normalization_transforms[
            pd.Timestamp("2018-12-31 8:00:00", tz=self.nytz)
        ]
        self.assertEqual(data.shape, dataset_normalization_transforms.observation_shape)
        self.assertEqual(data.shape, (3, 5))

    def test_rolling_transforms(self) -> None:
        dataset_normalization_transforms = OHLVCDataset(
            data_source=self.datasource,
            trading_calendar=self.cal,
            name="normalization_transforms",
            transforms=Compose(
                datasource=self.datasource,
                transforms=[
                    DropFeature(feature="lastupdated"),
                    RollingFeatures(window=3, metric="mean", groupby_level="ticker"),
                ],
            ),
        )

        # Test with integer index
        data = dataset_normalization_transforms[3]
        self.assertEqual(data.shape, dataset_normalization_transforms.observation_shape)
        self.assertEqual(data.shape, (3, 10))

        # Test with timestamp index
        data = dataset_normalization_transforms[
            pd.Timestamp("2018-12-31 8:00:00", tz=self.nytz)
        ]
        self.assertEqual(data.shape, dataset_normalization_transforms.observation_shape)
        self.assertEqual(data.shape, (3, 10))


if __name__ == "__main__":
    unittest.main()
