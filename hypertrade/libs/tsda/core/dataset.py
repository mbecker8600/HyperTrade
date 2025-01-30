from abc import ABC, abstractmethod
from typing import List, Optional

import pandas as pd

from hypertrade.libs.tsda.core.source import Source


class Dataset(ABC):
    """
    Abstract base class for all data.
    """

    def __init__(self, source: Source) -> None:
        self.source = source

    @abstractmethod
    def fetch(
        self,
        timestamp: pd.Timestamp,
        lookback: Optional[pd.Timedelta] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Fetches data at the specified timestamp.

        Args:
            timestamp: The point in time for which to fetch data.
            assets: Optional list of symbols or Assets to fetch data for.
            lookback: Optional lookback period for fetching historical data.

        Returns:
            A pandas DataFrame containing the fetched data.
        """
        ...


class PriceDataset(Dataset):
    """
    Abstract base class for datasets that provide price data.
    """

    def __init__(self, source: Source) -> None:
        super().__init__(source)

    @abstractmethod
    def fetch_dataset_symbols(self) -> List[str]:
        """Fetches the list of equities in the dataset."""
        ...

    @abstractmethod
    def fetch_current_price(
        self,
        timestamp: pd.Timestamp,
        symbols: List[str],
    ) -> pd.Series:
        """
        Fetches the current price at the specified timestamp.

        Args:
            timestamp: The point in time for which to fetch data.
            assets: List of symbols or Assets to fetch data for.

        Returns:
            A pandas Series containing the current prices.
        """
        ...
