from typing import Optional
from loguru import logger
import pandas as pd
from copy import deepcopy

from hypertrade.libs.simulator.event import EVENT_TYPE, Event, EventManager
from hypertrade.libs.service.locator import ServiceLocator, register_service
from hypertrade.libs.simulator.financials.portfolio import Portfolio


class PerformanceTracker:
    """Historical performance metrics for a trading strategy.

    This class tracks daily returns and positions of a trading strategy.

    attributes
    ----------
    daily_returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - Time series with decimal returns.
         - Example:
            2015-07-16    -0.012143
            2015-07-17    0.045350
            2015-07-20    0.030957
            2015-07-21    0.004902
    daily_positions : pd.DataFrame, optional
        Daily net position values.
         - Time series of dollar amount invested in each position and cash.
         - Days where stocks are not held can be represented by 0 or NaN.
         - Non-working capital is labelled 'cash'
         - Example:
            index         'AAPL'         'MSFT'          cash
            2004-01-09    13939.3800     -14012.9930     711.5585
            2004-01-12    14492.6300     -14624.8700     27.1821
            2004-01-13    -13853.2800    13653.6400      -43.6375

    """

    def __init__(self) -> None:
        self.daily_returns: pd.Series = pd.Series(dtype=float)
        self.daily_positions: pd.DataFrame = pd.DataFrame()
        self._previous_portfolio: Optional[Portfolio] = None

    def record_daily_metrics(
        self,
        date: pd.Timestamp,
        portfolio: Portfolio,
    ) -> None:
        """Update daily performance metrics."""

        # Record daily returns if positions are held
        if self._previous_portfolio is not None:
            self.daily_returns.loc[date] = (
                portfolio.portfolio_value - self._previous_portfolio.portfolio_value
            ) / self._previous_portfolio.portfolio_value

        current_positions_df = pd.DataFrame(
            portfolio.positions.groupby(level=0).sum()["amount"].to_dict(), index=[date]
        )
        self.daily_positions = pd.concat(
            [self.daily_positions, current_positions_df], axis=0
        )
        self._previous_portfolio = deepcopy(portfolio)


METRICS_SERVICE_NAME = "metrics_service"


@register_service(METRICS_SERVICE_NAME)
class PerformanceTrackingService:
    """"""

    SERVICE_NAME = METRICS_SERVICE_NAME

    def __init__(
        self,
    ) -> None:

        self.event_manager = ServiceLocator[EventManager]().get(
            EventManager.SERVICE_NAME
        )
        self.performance_tracker = PerformanceTracker()

        self.event_manager.subscribe(EVENT_TYPE.MARKET_CLOSE, self.record_daily_metrics)

    def record_daily_metrics(self, event: Event[None]) -> None:
        """Record daily metrics."""
        current_time = self.event_manager.current_time
        logger.bind(simulation_time=current_time).debug(
            f"Recording daily metrics at {current_time}"
        )
