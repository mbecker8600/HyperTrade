from typing import List, Optional

import pandas as pd
import torch

from hypertrade.libs.tsfd.transforms.interface import Transform

"""
Rolling feature transforms for computing moving statistics (e.g., rolling mean, rolling std).
"""


class RollingFeatures(Transform):
    """
    Computes rolling metrics for specified columns.

    This transform applies a rolling window to compute one or more metrics (e.g.,
    mean, std) for each specified column. It does not currently support tensors.

    Args:
        window (int): The size of the rolling window in time steps (rows).
        columns (Optional[List[str]]): The list of columns to transform.
        min_periods (int): Minimum number of observations in window required for a value.
        metric (str | List[str]): Which metric(s) to compute. Examples: 'mean', 'std'.

    Raises:
        NotImplementedError: If the input is a torch.Tensor.

    Returns:
        pd.DataFrame: The DataFrame with additional rolling metric columns.
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
