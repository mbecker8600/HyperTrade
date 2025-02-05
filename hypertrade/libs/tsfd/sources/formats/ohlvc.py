import pandas as pd

from hypertrade.libs.tsfd.sources.formats.types import DataSourceFormatter


class OHLVCConverter(DataSourceFormatter):
    def convert(self, df: pd.DataFrame) -> pd.DataFrame:
        return df
