from typing import Type

from loguru import logger
import pandas as pd

from hypertrade.libs.simulator.data.datasource import Dataset
from hypertrade.libs.simulator.assets import Asset
from hypertrade.libs.simulator.execute.commission import CommissionModel, NoCommission
from hypertrade.libs.simulator.event import EVENT_TYPE, Event, EventManager
from hypertrade.libs.simulator.execute.types import Order, Transaction
from hypertrade.libs.service.locator import ServiceLocator, register_service


BROKER_SERVICE_NAME = "broker_service"


@register_service(BROKER_SERVICE_NAME)
class BrokerService:

    SERVICE_NAME = BROKER_SERVICE_NAME

    def __init__(
        self,
        dataset: Dataset,
        execution_delay: pd.Timedelta = pd.Timedelta(milliseconds=3),
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
        assert event.data is not None, "Order data is None"
        order: Order = event.data
        current_price = float(
            self.dataset.fetch_current_price(current_time, [order.asset]).loc[
                order.asset.symbol
            ]
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
