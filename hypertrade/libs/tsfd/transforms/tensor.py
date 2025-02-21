import pandas as pd
import torch

from hypertrade.libs.tsfd.transforms.interface import Transform


class ToTensor(Transform):
    """
    Converts the input DataFrame into a PyTorch tensor.

    Usage:
        >>> import pandas as pd
        >>> from hypertrade.libs.tsfd.transforms.tensor import ToTensor
        >>> df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        >>> tensorizer = ToTensor()
        >>> tensor = tensorizer(df)

    Raises:
        ValueError: If the input is already
        a tensor when trying to call ToTensor transform.

    """

    def __call__(self, df: pd.DataFrame | torch.Tensor) -> pd.DataFrame | torch.Tensor:
        if isinstance(df, torch.Tensor):
            raise ValueError(
                "Input is already a tensor when trying to call ToTensor transform"
            )
        return torch.Tensor(df.values)


class Flatten(Transform):
    """
    Flattens the input DataFrame or tensor into a 1D array."""

    def __call__(self, df: pd.DataFrame | torch.Tensor) -> pd.DataFrame | torch.Tensor:
        if isinstance(df, torch.Tensor):
            return df.flatten()
        raise NotImplementedError("Flatten not yet supported for DataFrames")
