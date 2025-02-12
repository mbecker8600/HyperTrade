from typing import Optional

import pandas as pd
from pandas._libs.tslibs.nattype import NaTType

from hypertrade.libs.tsfd.schemas.default import default_schema
from hypertrade.libs.tsfd.sources.types import (
    DataSource,
    DataSourceFormat,
    FetchMode,
    Granularity,
)


class DefaultDataSourceFormat(DataSourceFormat):
    def __init__(
        self, datasource: DataSource, granularity: Granularity = Granularity.DAILY
    ):
        super().__init__(datasource)
        self.granularity = granularity

    schema = default_schema

    def fetch(
        self,
        timestamp: Optional[pd.Timestamp | NaTType | slice | int] = None,
        mode: FetchMode = FetchMode.LATEST,
    ) -> pd.DataFrame:
        if isinstance(timestamp, pd.Timestamp) and timestamp.tzinfo is None:
            timestamp = timestamp.tz_localize("UTC")
        return super().fetch(timestamp, mode)
