from dataclasses import dataclass

import pandas as pd


# TODO: Move market.py and market_types.py to a new module
@dataclass
class PriceChangeData:
    prices: pd.Series
