from typing import Any
from hypertrade.libs.tsda.core.source import CSVDataSource, MongoDBSource, Source


class DataSourceFactory:
    """
    Factory class for creating data sources.
    """

    @staticmethod
    def create_source(source_type: str, **kwargs: Any) -> Source:  # type: ignore
        """
        Creates a data source based on the given type.

        Raises:
            ValueError: If the source type is invalid.

        """
        if source_type == "csv":
            return CSVDataSource(**kwargs)
        elif source_type == "mongodb":
            return MongoDBSource(**kwargs)
        else:
            raise ValueError(f"Invalid source type: {source_type}")
