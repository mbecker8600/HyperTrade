import math
from typing import Dict, Type

import pandas as pd
from loguru import logger
from pandas._libs.tslibs.nattype import NaTType

from hypertrade.libs.service.locator import ServiceLocator, register_service
from hypertrade.libs.simulator.assets import Asset
from hypertrade.libs.simulator.event.service import EventManager
from hypertrade.libs.simulator.event.types import EVENT_TYPE, Event
from hypertrade.libs.simulator.execute.commission import CommissionModel, NoCommission
from hypertrade.libs.simulator.execute.types import Order, Transaction
from hypertrade.libs.simulator.financials.portfolio import PortfolioManager
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

    def _get_maybe_delayed_time(self) -> pd.Timestamp:
        """Determine if the trade execution should be delayed based on market hours.

        If the current time is not a trading minute or the market is closed, schedule the order for the next market open.
        """
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
        return delayed_time

    def place_order(self, asset: Asset, amount: int) -> Order:
        """Place an order based on asset and amount"""
        return self.place_order_by_amount(asset, amount)

    def place_order_by_weights(
        self, target_weights: Dict[Asset, float] | Dict[str, float]
    ) -> list[Order]:
        """Place orders to achieve the target portfolio weights.

        Args:
            target_weights (dict[Asset, float]): A dictionary of target portfolio weights for each asset.
                The keys are the assets and the values are the target weights.
        """
        current_time = self.event_manager.current_time
        delayed_time = self._get_maybe_delayed_time()

        portfolio_manager: PortfolioManager = ServiceLocator[PortfolioManager]().get(
            PortfolioManager.SERVICE_NAME
        )
        current_portfolio_value = portfolio_manager.portfolio.portfolio_value
        current_positions = portfolio_manager.portfolio.positions.groupby(
            level=0
        ).sum()["amount"]
        orders: list[Order] = []
        for asset, target_weight in target_weights.items():
            if isinstance(asset, str):
                # FIXME: Need to create an AssetFinder service to grab the asset object
                # from the datasource
                asset = Asset(sid=1, symbol=asset, asset_name=asset)
            # Get current price
            batch = self.dataset[current_time]
            if not isinstance(batch, pd.DataFrame):
                raise ValueError("Batch is not a DataFrame")
            price = batch["price"]
            if not isinstance(price, pd.Series):
                raise ValueError("Price is not a Series")
            current_price = float(price.loc[asset.symbol])

            # Calculate target position
            target_position_value = current_portfolio_value * target_weight
            target_shares = math.floor(target_position_value / current_price)

            # Calculate trade amount
            if current_positions is None:
                raise ValueError("Current positions is None")
            if asset.symbol in current_positions.index:
                current_shares = current_positions.loc[asset.symbol]
            else:
                current_shares = 0
            trade_amount = int(target_shares - current_shares)

            if trade_amount == 0:
                logger.bind(simulation_time=current_time).debug(
                    f"No trade needed for {asset.symbol}"
                )
                continue

            order = Order(asset=asset, amount=trade_amount, order_placed=delayed_time)
            self.event_manager.schedule_event(
                Event(event_type=EVENT_TYPE.ORDER_PLACED, payload=order),
                delay=(
                    (delayed_time - current_time)
                    if delayed_time > current_time
                    else None
                ),
            )
            orders.append(order)
        return orders

    def place_order_by_amount(self, asset: Asset, amount: int) -> Order:
        current_time = self.event_manager.current_time
        delayed_time = self._get_maybe_delayed_time()

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
        batch = self.dataset[current_time]
        if not isinstance(batch, pd.DataFrame):
            raise ValueError("Batch is not a DataFrame")
        price = batch["price"]
        if not isinstance(price, pd.Series):
            raise ValueError("Price is not a Series")
        current_price = float(price.loc[order.asset.symbol])
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
