from dataclasses import dataclass
from typing import List

import pandas as pd
from loguru import logger

from hypertrade.libs.service.locator import ServiceLocator, register_service
from hypertrade.libs.simulator.assets import Asset
from hypertrade.libs.simulator.event import EVENT_TYPE, Event, EventManager


@dataclass
class PriceChangeData:
    prices: pd.Series


MARKET_PRICE_SIMULATOR_SERVICE_NAME = "market_price_simulator"


@register_service(MARKET_PRICE_SIMULATOR_SERVICE_NAME)
class MarketPriceSimulator:

    SERVICE_NAME = MARKET_PRICE_SIMULATOR_SERVICE_NAME

    def __init__(self, universe: List[Asset]) -> None:
        service_locator = ServiceLocator[EventManager]()
        self.event_manager = service_locator.get(EventManager.SERVICE_NAME)
        self.event_manager.subscribe(EVENT_TYPE.MARKET_CLOSE, self.handle_market_close)
        self.event_manager.subscribe(EVENT_TYPE.MARKET_OPEN, self.handle_market_open)

        self.universe = universe

    def handle_market_close(self, event: Event[None]) -> None:
        logger.bind(simulation_time=self.event_manager.current_time).debug(
            f"Handling price changes at {event}"
        )
        prices = self._get_prices(event.time)
        self.event_manager.schedule_event(
            Event(EVENT_TYPE.PRICE_CHANGE, data=PriceChangeData(prices=prices))
        )

    def handle_market_open(self, event: Event[None]) -> None:
        logger.bind(simulation_time=self.event_manager.current_time).debug(
            f"Handling price changes at {event}"
        )
        prices = self._get_prices(event.time)
        self.event_manager.schedule_event(
            Event(EVENT_TYPE.PRICE_CHANGE, data=PriceChangeData(prices=prices))
        )

    def _get_prices(self, time: pd.Timestamp) -> pd.Series:
        # TODO: Go get prices from data source
        return pd.Series({asset: 100 for asset in self.universe})
