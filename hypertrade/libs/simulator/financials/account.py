"""Accounting classes for the finance module like portfolio tracking and general accounts."""

from dataclasses import dataclass

import pandas as pd

from hypertrade.libs.simulator.assets import Asset


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
    buying_power = float("inf")
    equity_with_loan = 0.0
    total_positions_value = 0.0
    total_positions_exposure = 0.0
    regt_equity = 0.0
    regt_margin = float("inf")
    initial_margin_requirement = 0.0
    maintenance_margin_requirement = 0.0
    available_funds = 0.0
    excess_liquidity = 0.0
    cushion = 0.0
    day_trades_remaining = float("inf")
    leverage = 0.0
    net_leverage = 0.0
    net_liquidation = 0.0


class AccountManager:
    pass
