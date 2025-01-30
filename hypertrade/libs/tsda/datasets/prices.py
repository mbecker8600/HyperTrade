from typing import Optional
import pandas as pd
from hypertrade.libs.tsda.core.dataset import PriceDataset
from hypertrade.libs.tsda.core.source import Source
from hypertrade.libs.tsda.format.ohlvc import OHLCVFormatMixin
from hypertrade.libs.tsda.format.tick import TickFormatMixin


class OHLCVDataset(PriceDataset, OHLCVFormatMixin):
    """
    Data source for reading OHLCV data.
    """

    def __init__(
        self,
        source: Source,
        tz: str = "America/New_York",
        exchange: str = "XNYS",
    ) -> None:
        super().__init__(source, tz, exchange)

    def fetch(
        self,
        timestamp: pd.Timestamp,
        lookback: Optional[pd.Timedelta] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Fetches OHLCV data at the specified timestamp.
        """
        assets = kwargs[
            "assets"
        ]  # TODO: Tests and error handling for missing assets or wrong format
        return self.fetch_ohlcv(timestamp, assets, lookback)


class TickDataset(PriceDataset, TickFormatMixin):
    """
    Data source for reading tick data.
    """

    def __init__(
        self,
        source: Source,
        tz: str = "America/New_York",
        exchange: str = "XNYS",
    ) -> None:
        super().__init__(source, tz, exchange)

    def fetch(
        self,
        timestamp: pd.Timestamp,
        lookback: Optional[pd.Timedelta] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Fetches tick data at the specified timestamp.
        """
        assets = kwargs[
            "assets"
        ]  # TODO: Tests and error handling for missing assets or wrong format
        return self.fetch_tick_data(timestamp, assets, lookback)
