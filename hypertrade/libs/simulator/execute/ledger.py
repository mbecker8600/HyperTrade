import pandas as pd
from loguru import logger

from hypertrade.libs.service.locator import ServiceLocator, register_service
from hypertrade.libs.simulator.event import EVENT_TYPE, Event, EventManager
from hypertrade.libs.simulator.execute.types import Transaction


class Ledger:
    """Object providing read-only access to current ledger state.

    Attributes
    ----------
    transactions : pd.DataFrame, optional
        Executed trade volumes and fill prices.
        - One row per trade.
        - Trades on different names that occur at the
          same time will have identical indicies.
        - Example:
            index                  amount   price    symbol
            2004-01-09 12:18:01    483      324.12   'AAPL'
            2004-01-09 12:18:01    122      83.10    'MSFT'
            2004-01-13 14:12:23    -75      340.43   'AAPL'

    """

    def __init__(self) -> None:
        self.transactions = pd.DataFrame(columns=["amount", "price", "symbol"])


LEDGER_SERVICE_NAME = "ledger_service"


@register_service(LEDGER_SERVICE_NAME)
class LedgerService:

    SERVICE_NAME = LEDGER_SERVICE_NAME

    def __init__(self) -> None:
        self.ledger = Ledger()
        self.event_manager: EventManager = ServiceLocator[EventManager]().get(
            EventManager.SERVICE_NAME
        )
        self.event_manager.subscribe(
            EVENT_TYPE.ORDER_FULFILLED, self.record_transaction
        )

    def record_transaction(self, event: Event[Transaction]) -> None:
        """Record a transaction in the ledger."""
        logger.bind(simulation_time=self.event_manager.current_time).debug(
            f"Recording transaction in ledger : {event}"
        )
        transaction = event.data
        assert transaction is not None, "Transaction data is None"
        self.ledger.transactions.loc[transaction.dt] = [
            transaction.amount,
            transaction.price,
            transaction.asset.symbol,
        ]
