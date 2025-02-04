from __future__ import annotations

from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    Protocol,
    Type,
    TypeVar,
    overload,
    runtime_checkable,
)


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


# Create a service locator instance
service_locator: ServiceLocator[Any] = ServiceLocator()


@overload
def register_service(service_name: str, cls: Type[T]) -> Type[T]: ...


@overload
def register_service(service_name: str) -> Callable[[Type[T]], Type[T]]: ...


def register_service(service_name: str, cls: Optional[Type[T]] = None) -> Any:
    """
    Decorator to register a class with the service locator on initialization.
    """

    def decorator(cls: Type[T]) -> Type[T]:
        """
        Inner decorator function.
        """

        # Store the original __init__ method
        original_init = cls.__init__

        def __init__(
            self: SupportsServiceRegistration, *args: Any, **kwargs: Any
        ) -> None:
            """
            Modified __init__ method to register the instance.
            """
            original_init(self, *args, **kwargs)  # Call the original __init__
            service_locator.register(service_name, self)  # Register the instance

        # Replace the original __init__ with the modified one
        cls.__init__ = __init__
        return cls

    return decorator
