from typing import cast

import pandas as pd
from pandas._libs.tslibs.nattype import NaTType


def cast_timestamp(timestamp: pd.Timestamp | NaTType) -> pd.Timestamp:
    if timestamp is pd.NaT:
        raise ValueError("timestamp cannot be NaT")
    return cast(pd.Timestamp, timestamp)
