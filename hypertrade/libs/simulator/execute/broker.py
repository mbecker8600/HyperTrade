from typing import Type

import pandas as pd
from loguru import logger
from pandas._libs.tslibs.nattype import NaTType

from hypertrade.libs.service.locator import ServiceLocator, register_service
from hypertrade.libs.simulator.assets import Asset
from hypertrade.libs.simulator.event.service import EventManager
from hypertrade.libs.simulator.event.types import EVENT_TYPE, Event
from hypertrade.libs.simulator.execute.commission import CommissionModel, NoCommission
from hypertrade.libs.simulator.execute.types import Order, Transaction
from hypertrade.libs.tsfd.datasets.asset import PricesDataset

BROKER_SERVICE_NAME = "broker_service"
DEFAULT_EXECUTION_DELAY = pd.Timedelta(milliseconds=3)


@register_service(BROKER_SERVICE_NAME)
class BrokerService:

    SERVICE_NAME: str = BROKER_SERVICE_NAME

    def __init__(
        self,
        dataset: PricesDataset,
        execution_delay: pd.Timedelta | NaTType = DEFAULT_EXECUTION_DELAY,
        commission_model: Type[CommissionModel] = NoCommission,
    ) -> None:
        self.event_manager: EventManager = ServiceLocator[EventManager]().get(
            EventManager.SERVICE_NAME
        )
        self.commission_model = commission_model
        if isinstance(execution_delay, NaTType):
            raise ValueError("Execution delay cannot be NaT")
        self.execution_delay: pd.Timedelta = execution_delay
        self.event_manager.subscribe(EVENT_TYPE.ORDER_PLACED, self._execute_trade)
        self.dataset = dataset

    def place_order(self, asset: Asset, amount: int) -> Order:
        current_time = self.event_manager.current_time
        open_time = self.event_manager._market_events.calendar.next_open(current_time)
        close_time = self.event_manager._market_events.calendar.next_close(current_time)

        if not self.event_manager._market_events.calendar.is_trading_minute(
            current_time
        ) and not (open_time <= current_time < close_time):
            logger.bind(simulation_time=current_time).debug(
                "Scheduling order for next market open"
            )
            delayed_time = open_time
        else:
            delayed_time = current_time

        order = Order(asset=asset, amount=amount, order_placed=delayed_time)
        self.event_manager.schedule_event(
            Event(event_type=EVENT_TYPE.ORDER_PLACED, payload=order),
            delay=(
                (delayed_time - current_time) if delayed_time > current_time else None
            ),
        )
        return order

    def _execute_trade(self, event: Event[Order]) -> None:
        current_time = self.event_manager.current_time
        logger.bind(simulation_time=current_time).debug(
            f"Executing trade order for order: {event.payload}"
        )
        if event.payload is None:
            raise ValueError("Order data is None")
        order: Order = event.payload
        current_price = float(
            self.dataset[current_time]["price"].loc[order.asset.symbol]
        )
        transaction = Transaction(
            dt=current_time + self.execution_delay,
            order_id=order.id,
            asset=order.asset,
            amount=order.amount,
            price=current_price,
        )
        logger.bind(simulation_time=current_time).debug(
            f"Trade executed for {order}: {current_price}"
        )
        self.event_manager.schedule_event(
            Event(event_type=EVENT_TYPE.ORDER_FULFILLED, payload=transaction),
            delay=self.execution_delay,
        )
