import exchange_calendars as xcals
import pandas as pd
from pandas._libs.tslibs.nattype import NaTType

from hypertrade.libs.tsfd.datasets.asset import (
    OhlvcDatasetAdapter,
    PricesDatasetAdapter,
)
from hypertrade.libs.tsfd.schemas.ohlvc import ohlvc_schema
from hypertrade.libs.tsfd.sources.types import DataSource, DataSourceFormat, Granularity


class OHLVCDataSourceFormat(
    DataSourceFormat, OhlvcDatasetAdapter, PricesDatasetAdapter
):
    """Indicates that the data source is in the OHLVC format.

    To see more about the OHLVC format, see the schema in `hypertrade.libs.tsfd.schemas.ohlvc`.

    Supported Dataset Adapters:
        - OHLVCDataset: for OHLVC datasets
        - PricesDataset: for current prices. This is a special case of OHLVC datasets where the
            dataset only contains the latest price information based on the timestamp.

    """

    def __init__(
        self,
        datasource: DataSource,
        granularity: Granularity = Granularity.DAILY,
    ):
        super().__init__(datasource)
        self.granularity = granularity

    schema = ohlvc_schema

    def ohlvc_adapter(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def prices_adapter(
        self,
        idx: pd.Timestamp | NaTType | slice | int,
        df: pd.DataFrame,
        trading_calendar: xcals.ExchangeCalendar,
    ) -> pd.DataFrame:
        if isinstance(idx, pd.Timestamp) and idx.tzinfo is None:
            idx = idx.tz_localize("UTC")
        dates = df.index.get_level_values(0).unique()
        data = {}
        for date in dates:
            open_ts = trading_calendar.session_open(date.tz_localize(None).normalize())
            open_data = df.xs(date, level="date")["open"]
            if open_data is None:
                raise ValueError(f"No open data found for the given timestamp {date}")
            data[open_ts] = open_data.to_dict()
            close_ts = trading_calendar.session_close(
                date.tz_localize(None).normalize()
            )
            close_data = df.xs(date, level="date")["close"]
            if close_data is None:
                raise ValueError(f"No close data found for the given timestamp {date}")
            data[close_ts] = close_data.to_dict()

        # Convert to DataFrame in the schema format defined in `hypertrade.libs.tsfd.schemas.prices`
        df = pd.DataFrame.from_dict(data, orient="index")
        df_stacked = df.stack()
        df_multiindex = pd.DataFrame(df_stacked).reset_index()
        if df_multiindex is None:
            raise ValueError("No data found for the given timestamp")
        df_multiindex.columns = ["date", "ticker", "price"]
        df_multiindex = df_multiindex.set_index(["date", "ticker"]).sort_index()
        if df_multiindex is None:
            raise ValueError("No data found for the given timestamp")
        return df_multiindex
