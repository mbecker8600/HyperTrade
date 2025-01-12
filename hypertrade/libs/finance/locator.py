from __future__ import annotations
from typing import Dict, Generic, Optional, Protocol, TypeVar, runtime_checkable


@runtime_checkable
class SupportsServiceRegistration(Protocol):
    SERVICE_NAME: str


# Define a generic type that supports service registration
T = TypeVar("T", bound=SupportsServiceRegistration)


class ServiceLocator(Generic[T]):
    """
    Provides a central registry for services (components).
    """

    _instance: Optional[ServiceLocator[T]] = (
        None  # Class-level variable to hold the instance
    )

    def __new__(cls) -> ServiceLocator[T]:
        """
        Ensures that only one instance of ServiceLocator is created.
        """
        if cls._instance is None:
            cls._instance = super(ServiceLocator, cls).__new__(cls)
            cls._instance._services = {}
        return cls._instance

    def __init__(self) -> None:
        self._services: Dict[str, T]

    def register(self, name: str, service: T) -> None:
        """
        Registers a service with a given name.
        """
        self._services[name] = service

    def get(self, name: str) -> T:
        """
        Retrieves a service by its name.
        """
        service = self._services.get(name)
        if service is None:
            raise ValueError(f"Service {name} not found")
        return service
