from typing import Protocol, cast

import pandas as pd
import pandera as pa


class IndexStrategy(Protocol):

    def size(self, df: pd.DataFrame) -> int: ...

    def loc(self, df: pd.DataFrame, timestamp: pd.Timestamp) -> pd.DataFrame: ...

    def loc_slice(self, df: pd.DataFrame, timestamp: slice) -> pd.DataFrame: ...

    def get_timestamp_at_index(self, df: pd.DataFrame, idx: int) -> pd.Timestamp: ...


class SingleIndexStrategy(IndexStrategy):

    def size(self, df: pd.DataFrame) -> int:
        return len(df.index.unique())

    def loc(self, df: pd.DataFrame, timestamp: pd.Timestamp) -> pd.DataFrame:
        latest_ts = df.loc[df.index <= timestamp].last_valid_index()
        data = df.loc[latest_ts]
        if isinstance(data, pd.Series):
            data = data.to_frame().T
            data.index.name = "date"
        return data

    def loc_slice(self, df: pd.DataFrame, timestamp: slice) -> pd.DataFrame:
        return df.loc[(df.index >= timestamp.start) & (df.index < timestamp.stop)]

    def get_timestamp_at_index(self, df: pd.DataFrame, idx: int) -> pd.Timestamp:
        index = df.index.unique().sort_values()
        return cast(pd.Timestamp, index[idx])


class MultiIndexStrategy(IndexStrategy):

    def size(self, df: pd.DataFrame) -> int:
        return len(df.index.get_level_values(0).unique())

    def loc(self, df: pd.DataFrame, timestamp: pd.Timestamp) -> pd.DataFrame:
        latest_ts = df.loc[
            (df.index.get_level_values(0) <= timestamp),
            :,
        ].last_valid_index()[0]
        data = df.loc[[latest_ts]]
        if isinstance(data, pd.Series):
            data = data.to_frame().T
        return data

    def loc_slice(self, df: pd.DataFrame, timestamp: slice) -> pd.DataFrame:

        return df.loc[
            (df.index.get_level_values(0) >= timestamp.start)
            & (df.index.get_level_values(0) < timestamp.stop),
            :,
        ]

    def get_timestamp_at_index(self, df: pd.DataFrame, idx: int) -> pd.Timestamp:
        index = df.index.get_level_values(0).unique().sort_values()
        return cast(pd.Timestamp, index[idx])


def get_index_strategy(
    idx: pa.Index | pa.MultiIndex | pd.Index | pd.MultiIndex,
) -> IndexStrategy:
    if isinstance(idx, pa.MultiIndex) or isinstance(idx, pd.MultiIndex):
        return MultiIndexStrategy()
    return SingleIndexStrategy()
