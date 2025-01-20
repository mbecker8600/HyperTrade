from __future__ import annotations

from dataclasses import dataclass, field
import enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import pandas as pd

from hypertrade.libs.finance.event import EVENT_TYPE, Event, EventManager
from hypertrade.libs.finance.market import CurrentPrices, HistoricalData
from hypertrade.libs.finance.order import Order
from hypertrade.libs.finance.portfolio import Portfolio, PortfolioManager
from hypertrade.libs.service.locator import ServiceLocator


# Officially supported datatypes
class DATA_TYPE(enum.Enum):
    CURRENT_PRICES = 1
    HISTORICAL_PRICES = 2


@dataclass
class StrategyContext:
    portfolio: Portfolio
    time: pd.Timestamp
    event: EVENT_TYPE


@dataclass
class StrategyData:
    data: Dict[DATA_TYPE, Any] = field(default_factory=dict)
    """Incoming data for the strategy based on the StrategyBuilder datasources"""


StrategyFunction = Callable[[StrategyContext, StrategyData], Optional[Order]]


class StrategyBuilder:
    def __init__(self) -> None:
        self._data_sources: List[Callable[[Event[Any]], Tuple[DATA_TYPE, Any]]] = []
        self._strategy_function: Optional[StrategyFunction] = None
        self.events: List[EVENT_TYPE] = []

    def on_event(self, event: EVENT_TYPE) -> StrategyBuilder:
        self.events.append(event)
        return self

    def with_current_prices(self) -> StrategyBuilder:
        self._data_sources.append(
            lambda event: (
                DATA_TYPE.CURRENT_PRICES,
                CurrentPrices.fetch(event.time),
            )
        )
        return self

    def with_historical_data(self, lookback_period: pd.Timedelta) -> StrategyBuilder:
        self._data_sources.append(
            lambda event: (
                DATA_TYPE.HISTORICAL_PRICES,
                HistoricalData.fetch(event.time, lookback_period),
            )
        )
        return self

    # def with_custom_data(self, *args, **kwargs) -> StrategyBuilder:
    #     self._data_sources.append(
    #         lambda event: (
    #             DATA_TYPE.HISTORICAL_PRICES,
    #             HistoricalData.fetch(event.time, lookback_period),
    #         )
    #     )
    #     return self

    def build(self, strategy_function: StrategyFunction) -> TradingStrategy:
        self._strategy_function = strategy_function
        return TradingStrategy(self)


class TradingStrategy:

    def __init__(self, builder: StrategyBuilder) -> None:
        self._data_sources = builder._data_sources
        assert builder._strategy_function, "Strategy function is None"
        self._strategy_function: StrategyFunction = builder._strategy_function

        self.event_manager = ServiceLocator[EventManager]().get(
            EventManager.SERVICE_NAME
        )
        for event in builder.events:
            self.event_manager.subscribe(event, self.execute)

    def get_market_data(self, event: Event[Any]) -> StrategyData:
        """Fetches and processes data for the given event."""
        market_data = StrategyData()
        for data_source in self._data_sources:
            # Fetch data from each source
            data_type, data = data_source(event)
            market_data.data[data_type] = data  # Add the fetched data to StrategyData

        return market_data

    def execute(self, event: Event[Any]) -> None:
        market_data = self.get_market_data(event)
        portfolio: Portfolio = (
            ServiceLocator[PortfolioManager]()
            .get(PortfolioManager.SERVICE_NAME)
            .portfolio
        )
        context = StrategyContext(
            portfolio=portfolio,
            time=event.time,
            event=event.event_type,
        )
        order = self._strategy_function(context, market_data)
        if order is not None:
            self.event_manager.schedule_event(
                event=Event(EVENT_TYPE.ORDER_PLACED, data=order)
            )
