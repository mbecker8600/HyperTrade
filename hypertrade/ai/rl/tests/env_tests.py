import os
import unittest

import exchange_calendars as xcals
import pytz
import torch
from pandas import Timestamp

# import hypertrade.libs.debugging  # donotcommit
from hypertrade.ai.rl.env import TradingEnvironment
from hypertrade.libs.logging.setup import initialize_logging
from hypertrade.libs.tsfd.datasets.asset import OHLVCDataset, PricesDataset
from hypertrade.libs.tsfd.sources.csv import CSVSource
from hypertrade.libs.tsfd.sources.formats.ohlvc import OHLVCDataSourceFormat
from hypertrade.libs.tsfd.transforms import Compose as tsfd_Compose
from hypertrade.libs.tsfd.transforms import (
    DropFeature,
    Flatten,
    Normalize,
    RollingFeatures,
    ToTensor,
)
from hypertrade.libs.tsfd.utils.time import cast_timestamp


class TestRLTradingEnvironment(unittest.TestCase):

    def setUp(self) -> None:
        ws = os.path.dirname(__file__)
        ohlvc_sample_data_path = os.path.join(
            ws, "../../../libs/simulator/data/tests/data/ohlvc/sample.csv"
        )
        self.cal = xcals.get_calendar("XNYS")
        self.nytz = pytz.timezone("America/New_York")
        self.datasource = OHLVCDataSourceFormat(
            CSVSource(source=ohlvc_sample_data_path),
        )
        self.prices_dataset = PricesDataset(
            data_source=self.datasource,
            name="prices",
            trading_calendar=self.cal,
        )
        self.features_dataset = OHLVCDataset(
            data_source=self.datasource,
            name="features",
            trading_calendar=self.cal,
            transforms=tsfd_Compose(
                datasource=self.datasource,
                transforms=[
                    DropFeature("lastupdated"),
                    Normalize(),
                    RollingFeatures(window=3, metric="mean", groupby_level="ticker"),
                    ToTensor(),
                    Flatten(),
                ],
            ),
        )

    def test_reset_w_empty_batch(self) -> None:
        nytz = pytz.timezone("America/New_York")
        start = Timestamp("2018-09-14", tz=nytz)
        end = Timestamp("2018-12-31", tz=nytz)
        env = TradingEnvironment(
            symbols=["GE", "BA", "AAPL"],
            prices_dataset=self.prices_dataset,
            feature_dataset=self.features_dataset,
            min_start=cast_timestamp(start),
            max_end=cast_timestamp(end),
        )
        tensordict = env.reset()
        self.assertEqual(tensordict.batch_size, torch.Size([]))
        self.assertEqual(tensordict["allocations"].shape, torch.Size([3]))
        self.assertEqual(
            tensordict["features"].shape, self.features_dataset.observation_shape
        )

    # TODO: Test the reset function with random portofolio allocations
    # TODO: Test the reset function with a non-empty batch
    # TODO: Test the reset function with random start and end dates

    def test_rollout(self) -> None:
        nytz = pytz.timezone("America/New_York")
        start = Timestamp("2018-09-14", tz=nytz)
        end = Timestamp("2018-12-31", tz=nytz)
        env = TradingEnvironment(
            symbols=["GE", "BA", "AAPL"],
            prices_dataset=self.prices_dataset,
            feature_dataset=self.features_dataset,
            min_start=cast_timestamp(start),
            max_end=cast_timestamp(end),
        )

        tensordict = env.rollout(max_steps=20)
        pass


if __name__ == "__main__":
    initialize_logging(level="DEBUG")
    unittest.main()
