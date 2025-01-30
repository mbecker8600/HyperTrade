from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, Optional

import pandas as pd


class Source(ABC):
    """
    Abstract base class for data sources.
    """

    @abstractmethod
    def _fetch(
        self,
        timestamp: pd.Timestamp,
        lookback: Optional[pd.Timedelta] = None,
    ) -> pd.DataFrame:
        """
        Internal method to fetch data based on the storage mechanism.
        """
        pass


class CSVDataSource(Source):
    """
    CSVDataSource represents time series datasources in CSV format.
    """

    def __init__(self, filepath: str, **kwargs: Any) -> None:
        """
        CSVDataSource initialization.

        Args:
            filepath: The file you want to load.
            **kwargs: Additional kwargs to pass to the pd.read_csv(...) function.
        """
        self.filepath = filepath
        self.kwargs = kwargs

    @cached_property
    def data(self) -> pd.DataFrame:
        data = pd.read_csv(self.filepath, **self.kwargs)
        return data

    def _fetch(
        self,
        timestamp: pd.Timestamp,
        lookback: Optional[pd.Timedelta] = None,
    ) -> pd.DataFrame:
        """
        Internal method to fetch data based on the storage mechanism.
        """
        data = self.data
        if lookback is None:
            return data.loc(axis=0)[
                pd.IndexSlice[timestamp.date().strftime("%Y-%m-%d"), :]
            ]
        else:
            start_time = timestamp - lookback
            return data.loc(axis=0)[pd.IndexSlice[start_time:timestamp, :]]


class MongoDBSource(Source):
    """
    MongoDBSource represents a data source stored in a MongoDB database.
    """

    def __init__(
        self, connection_string: str, database_name: str, collection_name: str
    ):
        """
        MongoDBSource initialization.

        Args:
            connection_string: MongoDB connection string.
            database_name: Name of the database.
            collection_name: Name of the collection.
        """
        # Initialize MongoDB client and connect to the database and collection
        # ... (Implementation for MongoDB connection)

    def _fetch(
        self,
        timestamp: pd.Timestamp,
        lookback: Optional[pd.Timedelta] = None,
    ) -> pd.DataFrame:
        """
        Fetches data from MongoDB based on the timestamp and lookback period.
        """
        # Construct MongoDB query based on timestamp and lookback
        # ... (Implementation for MongoDB query)
        # Execute query and retrieve data
        # ... (Implementation for MongoDB data retrieval)
        # Convert data to pandas DataFrame
        # ... (Implementation for data conversion)
        return data_frame  # type: ignore
