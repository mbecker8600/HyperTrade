from abc import ABC, abstractmethod

import pandas as pd


class DataSourceFormatter(ABC):
    @abstractmethod
    def format(self, df: pd.DataFrame) -> pd.DataFrame: ...
