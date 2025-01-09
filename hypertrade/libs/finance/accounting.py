"""Accounting classes for the finance module like portfolio tracking and general accounts."""

from dataclasses import dataclass

import pandas as pd

from hypertrade.libs.finance.assets import Asset


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
    """Object providing read-only access to current portfolio state.

    This object only provide a point in time view of the portfolio. It does not
    provide functionality for placing orders, modifying positions, or any other
    actions. It is only used to provide information about the current state of
    the portfolio at any given point in time.

    Parameters: 
        start_date : pd.Timestamp
            The start date for the period being recorded.
        capital_base : float
            The starting value for the portfolio. This will be used as the starting
            cash, current cash, and portfolio value.

    Attributes:
        positions : hypertrade.libs.finance.accounting.Positions
            Dict-like object containing information about currently-held positions.
        cash : float
            Amount of cash currently held in portfolio.
        portfolio_value : float
            Current liquidation value of the portfolio's holdings.
            This is equal to ``cash + sum(shares * price)``
        starting_cash : float
            Amount of cash in the portfolio at the start of the backtest.

    Properties:
        capital_used : float
            Amount of capital used in the current period.
        current_portfolio_weights : pd.Series
            Series containing the percentage of the portfolio invested in each asset.
            The index is the asset symbol and the values are the percentage of the
            portfolio invested in each asset.
    """

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
