import pandas as pd
import torch

from hypertrade.libs.tsfd.sources.types import DataSource
from hypertrade.libs.tsfd.transforms.interface import FitTransform

"""
Normalizing or scaling transforms that require dataset statistics (e.g., mean, std).
"""


class Normalize(FitTransform):
    """
    Applies mean-std normalization to a DataFrame.

    The fit step pulls `mean` and `std` from the given DataSource, then transform
    subtracts the mean and divides by the std.

    Usage example:
        normalizer = Normalize()
        normalizer.fit(your_datasource)
        transformed_df = normalizer.transform(your_dataframe)

    Raises:
        NotImplementedError: If the input is a torch.Tensor.

    Returns:
        pd.DataFrame: The normalized DataFrame.
    """

    def fit(self, datasource: DataSource) -> None:
        self.mean = datasource.mean
        self.std = datasource.std

    def transform(self, df: pd.DataFrame | torch.Tensor) -> pd.DataFrame | torch.Tensor:
        if isinstance(df, torch.Tensor):
            raise NotImplementedError("Torch tensors not yet supported for Normalize")
        normalized_df = (df - self.mean) / self.std
        return normalized_df
