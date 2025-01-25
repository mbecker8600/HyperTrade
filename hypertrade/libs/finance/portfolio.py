from __future__ import annotations

from functools import cached_property

from loguru import logger
import pandera as pa
import pandas as pd

from hypertrade.libs.finance.data.datasource import Dataset
from hypertrade.libs.finance.execute.types import Transaction
from hypertrade.libs.finance.event import EVENT_TYPE, Event, EventManager
from hypertrade.libs.finance.market import PriceChangeData
from hypertrade.libs.service.locator import ServiceLocator, register_service


PRICES_SCHEMA: pa.SeriesSchema = pa.SeriesSchema()


class Portfolio:
    """Object providing read-only access to current portfolio state.

    This object only provide a point in time view of the portfolio. It does not
    provide functionality for placing orders, modifying positions, or any other
    actions. It is only used to provide information about the current state of
    the portfolio at any given point in time.

    Parameters:
        capital_base : float
            The starting value for the portfolio. This will be used as the starting
            cash, current cash, and portfolio value.

    Attributes:
        positions: pd.Dataframe
            Dict-like object containing information about currently-held positions.
        cash : float
            Amount of cash currently held in portfolio.
        portfolio_value : float
            Current liquidation value of the portfolio's holdings.
            This is equal to ``cash + sum(shares * price)``
        starting_cash : float
            Amount of cash in the portfolio at the start of the backtest.
        capital_used : float
            Amount of capital used in the current period.
        current_portfolio_weights : pd.Series
            Series containing the percentage of the portfolio invested in each asset.
            The index is the asset symbol and the values are the percentage of the
            portfolio invested in each asset.
    """

    def __init__(
        self,
        capital_base: float = 0.0,
    ) -> None:
        self.positions: pd.DataFrame = pd.DataFrame(
            columns=["amount", "cost_basis"], index=pd.MultiIndex.from_arrays([[], []])
        )
        self.starting_cash = capital_base
        self.cash_flow = 0.0
        self.pnl = 0.0
        self.returns = 0.0
        self.cash = capital_base

        self.positions_exposure = 0.0
        self._current_market_prices: pd.Series = pd.Series()

    def update(self, tx: Transaction) -> None:
        """Update the portfolio given a processed transaction"""
        # Set the positions dataframe (indexed by (symbol, time)) to the number of shares and cost basis (i.e. original price)
        self.positions.loc[(tx.asset.symbol, tx.dt), :] = [tx.amount, tx.price]
        self.cash -= tx.amount * tx.price

    @property
    def capital_used(self) -> float:
        return self.cash_flow

    @property
    def current_market_prices(self) -> pd.Series:
        return self._current_market_prices

    @current_market_prices.setter
    def current_market_prices(self, prices: pd.Series) -> None:
        # Invalidate cached properties
        if hasattr(self, "positions_value"):
            delattr(self, "positions_value")
        if hasattr(self, "portfolio_value"):
            delattr(self, "portfolio_value")
        if hasattr(self, "current_portfolio_weights"):
            delattr(self, "current_portfolio_weights")
        self._current_market_prices = prices

    @cached_property
    def positions_value(self) -> float:
        """Calculate the total value of all positions in the portfolio."""
        if self.positions.empty:
            return 0.0

        symbol_positions = self.positions.groupby(level=0).sum()["amount"]
        return float((self.current_market_prices * symbol_positions).sum())

    @cached_property
    def portfolio_value(self) -> float:
        """Calculate the total value of the portfolio at the current time."""
        total_value: float = self.cash
        if not self.positions.empty:
            symbol_positions = self.positions.groupby(level=0).sum()["amount"]
            total_value += float((self.current_market_prices * symbol_positions).sum())
        return total_value

    @cached_property
    def current_portfolio_weights(self) -> pd.Series:
        """
        Compute each asset's weight in the portfolio by calculating its held
        value divided by the total value of all positions.

        Each equity's value is its price times the number of shares held. Each
        futures contract's value is its unit price times number of shares held
        times the multiplier.
        """
        if self.positions.empty or self.current_market_prices.empty:
            return pd.Series()

        symbol_positions = self.positions.groupby(level=0).sum()["amount"]
        sym_value = symbol_positions * self.current_market_prices
        return sym_value / sym_value.sum()


PORTFOLIO_SERVICE_NAME = "portfolio_service"


@register_service(PORTFOLIO_SERVICE_NAME)
class PortfolioManager:
    """PortfolioManager is a locatable service that handles the event listeners for updating
    the portfolio.

    It doesn't handle calculations or setting values. If you're looking for the logic for
    updating the portfolio, look in the Portfolio class.

    Usage:
        ```python
        portfolio_service = ServiceLocator[PortfolioManager]().get(
            PortfolioManager.SERVICE_NAME
        )
        portfolio_service.portfolio.portfolio_value
        ```

    Subscribed events:
        - EVENT_TYPE.ORDER_FULFILLED: When an order has been filled, and a Transaction created,
        this event will be published and the portfolio values will be updated based on the transaction.

    Attributes:
        - portfolio (Portfolio): The current portfolio at a given timestamp within the simulation.

    """

    SERVICE_NAME = PORTFOLIO_SERVICE_NAME

    def __init__(
        self,
        dataset: Dataset,
        capital_base: float = 0.0,
    ) -> None:

        service_locator = ServiceLocator[EventManager]()
        self.event_manager = service_locator.get(EventManager.SERVICE_NAME)
        self.event_manager.subscribe(EVENT_TYPE.ORDER_FULFILLED, self.update_positions)
        self.event_manager.subscribe(EVENT_TYPE.PRICE_CHANGE, self.handle_price_change)
        self.dataset = dataset
        self.portfolio = Portfolio(capital_base=capital_base)

    def _set_portfolio_market_price(self) -> None:
        """Set the current market prices for the portfolio's positions."""
        assets = self.portfolio.positions.groupby(level=0).sum().index.to_list()
        prices = self.dataset.fetch_current_price(
            self.event_manager.current_time, assets
        )
        self.portfolio.current_market_prices = prices

    def handle_price_change(self, event: Event[PriceChangeData]) -> None:
        """Handle price change events and invalidate the portfolio's cached properties."""
        if not self.portfolio.positions.empty:
            self._set_portfolio_market_price()

    def update_positions(self, event: Event[Transaction]) -> None:
        logger.bind(simulation_time=self.event_manager.current_time).debug(
            f"Updating portfolio positions: {event}"
        )
        assert event.data is not None, "Empty transaction passed to update positions"
        transaction: Transaction = event.data
        self.portfolio.update(transaction)
        self._set_portfolio_market_price()
