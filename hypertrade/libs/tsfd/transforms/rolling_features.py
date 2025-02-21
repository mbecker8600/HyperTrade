from typing import List, Optional

import pandas as pd
import torch

from hypertrade.libs.tsfd.transforms.interface import Transform


class RollingFeatures(Transform):
    """
    Compute rolling metrics (e.g., moving average) for specified columns.

    Args:
        window (int): Window size for the rolling calculation.
        columns (list[str]): Columns to apply the rolling metric to.
        min_periods (int): Minimum number of observations required.
        metric (str): Which metric to apply ('mean', 'std', etc.).
    """

    def __init__(
        self,
        window: int = 5,
        columns: Optional[List[str]] = None,
        min_periods: int = 1,
        metric: str | List[str] = "mean",
    ) -> None:
        self.window = window
        self.columns = columns
        self.min_periods = min_periods
        self.metric: List[str] = metric if isinstance(metric, list) else [metric]

    def __call__(self, df: pd.DataFrame | torch.Tensor) -> pd.DataFrame | torch.Tensor:
        if isinstance(df, torch.Tensor):
            raise NotImplementedError("RollingFeatures does not support torch.Tensor")

        # If columns are not specified, apply to all columns
        if self.columns is None:
            self.columns = df.columns

        df = df.copy()
        for col in self.columns:
            if col in df.columns:
                roll = df[col].rolling(window=self.window, min_periods=self.min_periods)
                for metric in self.metric:
                    df[f"{col}_rolling_{self.metric}_{self.window}"] = getattr(
                        roll, metric
                    )()
        return df
