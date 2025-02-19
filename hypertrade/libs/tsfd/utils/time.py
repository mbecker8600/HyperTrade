from typing import Optional, cast

import pandas as pd
from pandas._libs.tslibs.nattype import NaTType


def cast_timestamp(timestamp: Optional[pd.Timestamp | NaTType] = None) -> pd.Timestamp:
    if timestamp is None or timestamp is pd.NaT:
        raise ValueError("timestamp cannot be NaT or None")
    return cast(pd.Timestamp, timestamp)
