"""Accounting classes for the finance module like portfolio tracking and general accounts."""

from dataclasses import dataclass

import debugpy
import pandas as pd

from hypertrade.libs.finance.assets.assets import Asset


@dataclass
class Account:
    """
    The account object tracks information about the trading account. The
    values are updated as the algorithm runs and its keys remain unchanged.
    If connected to a broker, one can update these values with the trading
    account values as reported by the broker.
    """
    settled_cash = 0.0
    accrued_interest = 0.0
    buying_power = float('inf')
    equity_with_loan = 0.0
    total_positions_value = 0.0
    total_positions_exposure = 0.0
    regt_equity = 0.0
    regt_margin = float('inf')
    initial_margin_requirement = 0.0
    maintenance_margin_requirement = 0.0
    available_funds = 0.0
    excess_liquidity = 0.0
    cushion = 0.0
    day_trades_remaining = float('inf')
    leverage = 0.0
    net_leverage = 0.0
    net_liquidation = 0.0


@dataclass
class Position:
    """
    A position held by an algorithm.
    """

    asset: Asset
    amount: int
    cost_basis: float
    last_sale_price: float
    last_sale_date: pd.Timestamp


Positions = dict[Asset, Position]


class Portfolio:
    def __init__(self, start_date: pd.Timestamp = None, capital_base: float = 0.0) -> None:
        self.cash_flow = 0.0
        self.starting_cash = capital_base
        self.portfolio_value = capital_base
        self.pnl = 0.0
        self.returns = 0.0
        self.cash = capital_base
        self.positions: Positions = {}
        self.start_date = start_date
        self.positions_value = 0.0
        self.positions_exposure = 0.0

    @property
    def capital_used(self) -> float:
        return self.cash_flow

    @property
    def current_portfolio_weights(self) -> pd.Series:
        """
        Compute each asset's weight in the portfolio by calculating its held
        value divided by the total value of all positions.

        Each equity's value is its price times the number of shares held. Each
        futures contract's value is its unit price times number of shares held
        times the multiplier.
        """
        position_values = pd.Series({
            asset: (
                position.last_sale_price *
                position.amount *
                asset.price_multiplier
            )
            for asset, position in self.positions.items()
        })
        return position_values / self.portfolio_value
