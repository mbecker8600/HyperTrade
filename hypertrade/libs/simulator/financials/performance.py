import pyfolio as pf

from hypertrade.libs.simulator.event import EventManager
from hypertrade.libs.service.locator import ServiceLocator, register_service


class PerformanceTracker:

    def __init__(self) -> None:
        pass


METRICS_SERVICE_NAME = "metrics_service"


@register_service(METRICS_SERVICE_NAME)
class PerformanceTrackingService:
    """"""

    SERVICE_NAME = METRICS_SERVICE_NAME

    def __init__(
        self,
    ) -> None:

        event_manager = ServiceLocator[EventManager]().get(EventManager.SERVICE_NAME)

        pf.create_full_tear_sheet(
            returns=event_manager.returns,
            positions=event_manager.positions,
            transactions=event_manager.transactions,
            benchmark_rets=event_manager.benchmark_rets,
        )
