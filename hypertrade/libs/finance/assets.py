from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Asset:
    sid: int
    symbol: str
    asset_name: str
    price_multiplier: float = 1.0

    def __hash__(self) -> int:
        return hash(self.sid)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Asset):
            return False
        return self.sid == other.sid


class Equity(Asset):
    pass


class Future(Asset):
    expiration_date: str
