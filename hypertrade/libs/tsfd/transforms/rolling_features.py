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
        groupby_level (Optional[int | str]): The level to group by for multi-index DataFrames.

    Raises:
        NotImplementedError: If the input is a torch.Tensor.

    Returns:
        pd.DataFrame: The DataFrame with additional rolling metric columns.
    """

    def __init__(
        self,
        window: int = 5,
        columns: Optional[List[str]] = None,
        metric: str | List[str] = "mean",
        groupby_level: Optional[int | str] = None,
    ) -> None:
        self.window = window
        self.columns = columns
        self.metric: List[str] = metric if isinstance(metric, list) else [metric]
        self.groupby_level = groupby_level

    def __call__(self, df: pd.DataFrame | torch.Tensor) -> pd.DataFrame | torch.Tensor:
        if isinstance(df, torch.Tensor):
            raise NotImplementedError("RollingFeatures does not support torch.Tensor")

        if len(df) < self.window:
            raise ValueError(
                f"Window of {self.window} exceeds dataset length {len(df)}"
            )

        # If columns are not specified, apply to all columns
        columns: List[str] = (
            self.columns if self.columns is not None else list(df.columns)
        )

        if self.groupby_level is not None and isinstance(df.index, pd.MultiIndex):

            def apply_rolling(sub_df: pd.DataFrame) -> pd.DataFrame:
                for col in columns:
                    if col in sub_df.columns:
                        roll = sub_df[col].rolling(
                            window=self.window, min_periods=self.window
                        )
                        for metric in self.metric:
                            sub_df[f"{col}_rolling_{metric}_{self.window}"] = getattr(
                                roll, metric
                            )()
                return sub_df.tail(1)

            df = df.groupby(level=self.groupby_level, group_keys=False).apply(
                apply_rolling
            )
        else:
            df = df.copy()
            for col in columns:
                if col in df.columns:
                    roll = df[col].rolling(window=self.window, min_periods=self.window)
                    for metric in self.metric:
                        df[f"{col}_rolling_{metric}_{self.window}"] = getattr(
                            roll, metric
                        )()

            # Keep only the latest row
            df = df.tail(1)

        return df
