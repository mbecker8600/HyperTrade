from typing import Type

import pandas as pd
from loguru import logger

from hypertrade.libs.service.locator import ServiceLocator, register_service
from hypertrade.libs.simulator.assets import Asset
from hypertrade.libs.simulator.event import EVENT_TYPE, Event, EventManager
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
        execution_delay: pd.Timedelta = DEFAULT_EXECUTION_DELAY,
        commission_model: Type[CommissionModel] = NoCommission,
    ) -> None:
        self.event_manager: EventManager = ServiceLocator[EventManager]().get(
            EventManager.SERVICE_NAME
        )
        self.commission_model = commission_model
        self.execution_delay = execution_delay
        self.event_manager.subscribe(EVENT_TYPE.ORDER_PLACED, self._execute_trade)
        self.dataset = dataset

    def place_order(self, asset: Asset, amount: int) -> Order:
        """

        Raises:


        Returns:
            Order: The pending placed order (if successful).
                NOTE: This doesn't mean it has been executed
        """
        current_time = self.event_manager.current_time
        logger.bind(simulation_time=current_time).debug(
            f"Placing order for asset: {asset} and amount: {amount}"
        )
        order = Order(asset=asset, amount=amount, order_placed=current_time)
        self.event_manager.schedule_event(
            Event(event_type=EVENT_TYPE.ORDER_PLACED, data=order)
        )
        return order

    def _execute_trade(self, event: Event[Order]) -> None:
        current_time = self.event_manager.current_time
        logger.bind(simulation_time=current_time).debug(
            f"Executing trade order for order: {event.data}"
        )
        if event.data is None:
            raise ValueError("Order data is None")
        order: Order = event.data
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
            Event(event_type=EVENT_TYPE.ORDER_FULFILLED, data=transaction),
            delay=self.execution_delay,
        )
