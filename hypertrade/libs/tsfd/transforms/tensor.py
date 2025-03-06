"""
Transforms for converting DataFrame data into PyTorch tensors, and optional flattening.
"""

import pandas as pd
import torch

from hypertrade.libs.tsfd.transforms.interface import Transform


class ToTensor(Transform):
    """
    Converts the input DataFrame into a PyTorch tensor.

    This transform expects a Pandas DataFrame and returns a torch.Tensor with
    the same numeric values.

    Raises:
        ValueError: If the input is already a torch.Tensor.

    Returns:
        torch.Tensor: A tensor containing the numeric data from the original DataFrame.
    """

    def __call__(self, df: pd.DataFrame | torch.Tensor) -> pd.DataFrame | torch.Tensor:
        if isinstance(df, torch.Tensor):
            raise ValueError(
                "Input is already a tensor when trying to call ToTensor transform"
            )
        return torch.Tensor(df.values)


class Flatten(Transform):
    """
    Flattens a torch.Tensor to a 1D array.

    This transform currently supports only PyTorch tensors and raises a NotImplementedError
    for DataFrames.

    Raises:
        NotImplementedError: If the input is a DataFrame.

    Returns:
        torch.Tensor: The flattened tensor.
    """

    def __call__(self, df: pd.DataFrame | torch.Tensor) -> pd.DataFrame | torch.Tensor:
        if isinstance(df, torch.Tensor):
            return df.flatten()
        raise NotImplementedError("Flatten not yet supported for DataFrames")
