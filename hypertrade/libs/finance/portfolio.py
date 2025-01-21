from __future__ import annotations
from dataclasses import dataclass

from loguru import logger
import pandas as pd

from hypertrade.libs.finance.assets import Asset
from hypertrade.libs.finance.execute.types import Transaction
from hypertrade.libs.finance.event import EVENT_TYPE, Event, EventManager
from hypertrade.libs.finance.market import PriceChangeData
from hypertrade.libs.service.locator import ServiceLocator, register_service


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

    def __init__(
        self, start_date: pd.Timestamp = None, capital_base: float = 0.0
    ) -> None:
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
        position_values = pd.Series(
            {
                asset: (
                    position.last_sale_price * position.amount * asset.price_multiplier
                )
                for asset, position in self.positions.items()
            }
        )
        return position_values / self.portfolio_value


PORTFOLIO_SERVICE_NAME = "portfolio_service"


@register_service(PORTFOLIO_SERVICE_NAME)
class PortfolioManager:

    SERVICE_NAME = PORTFOLIO_SERVICE_NAME

    def __init__(self, start_date: pd.Timestamp, capital_base: float = 0.0) -> None:

        self.portfolio = Portfolio(start_date=start_date, capital_base=capital_base)

        service_locator = ServiceLocator[EventManager]()
        self.event_manager = service_locator.get(EventManager.SERVICE_NAME)
        self.event_manager.subscribe(EVENT_TYPE.PRICE_CHANGE, self.handle_price_change)

    def handle_price_change(self, event: Event[PriceChangeData]) -> None:
        logger.bind(simulation_time=self.event_manager.current_time).debug(
            f"Handling price change for event: {event}"
        )

    def update_positions(self, event: Event[Transaction]) -> None:
        logger.bind(simulation_time=self.event_manager.current_time).debug(
            f"Updating portfolio positions: {event}"
        )
