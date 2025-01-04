
from dataclasses import dataclass


@dataclass
class Asset:
    symbol: str
    asset_name: str


class Equity(Asset):
    pass


class Future(Asset):
    expiration_date: str
