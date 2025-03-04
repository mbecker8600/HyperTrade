"""
Utilities for basic DataFrame transformations such as dropping columns.
"""

from typing import List

import pandas as pd
import torch

from hypertrade.libs.tsfd.transforms.interface import Transform


class DropFeature(Transform):
    """
    Drops one or more columns from a DataFrame.

    This transform removes columns by name. It supports multiple columns by passing
    a list of strings. It only operates on Pandas DataFrames, not tensors.

    Args:
        feature (str | List[str]): The column(s) to drop.

    Raises:
        ValueError: If the input data is a torch.Tensor instead of a DataFrame.

    Returns:
        pd.DataFrame: The DataFrame without the specified columns.
    """

    def __init__(self, feature: str | List[str]) -> None:
        self.feature = feature if isinstance(feature, list) else [feature]

    def __call__(self, df: pd.DataFrame | torch.Tensor) -> pd.DataFrame | torch.Tensor:
        if isinstance(df, torch.Tensor):
            raise ValueError(
                "Drop feature should only be applied to DataFrames, not tensors"
            )
        return df.drop(columns=self.feature, inplace=False)
