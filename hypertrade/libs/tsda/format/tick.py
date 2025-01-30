from typing import List, Optional, Union

import pandas as pd


class TickFormatMixin:
    """
    Mixin class for handling tick data.
    """

    def fetch_tick_data(
        self,
        timestamp: pd.Timestamp,
        assets: List[str],
        lookback: Optional[pd.Timedelta] = None,
    ) -> pd.DataFrame:
        """
        Fetches tick data at the specified timestamp.
        """
        data = self.source._fetch(timestamp, lookback)
        if assets:
            return data[data["ticker"].isin(assets)]
        else:
            return data

    def fetch_current_price(
        self,
        timestamp: pd.Timestamp,
        assets: List[str],
    ) -> pd.Series:
        """
        Fetches the current price from tick data at the specified timestamp.
        """
        data = self.fetch_tick_data(timestamp, assets)
        return data.droplevel("date")["bid_price"].loc(axis=0)[pd.IndexSlice[assets]]
