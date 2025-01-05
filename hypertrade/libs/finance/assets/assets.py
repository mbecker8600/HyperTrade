
from dataclasses import dataclass


@dataclass
class Asset:
    symbol: str
    asset_name: str
    price_multiplier: float = 1.0


class Equity(Asset):
    pass


class Future(Asset):
    expiration_date: str
