import pandas as pd
import torch

from hypertrade.libs.tsfd.sources.types import DataSource
from hypertrade.libs.tsfd.transforms.interface import FitTransform


class Normalize(FitTransform):
    """
    Applies mean-std normalization to each column in the DataFrame. The class is
    initialized with a mean and standard deviation, then subtracts the mean from
    each value and divides by the standard deviation.

    Usage:
        >>> import pandas as pd
        >>> from hypertrade.libs.tsfd.transforms.scale import Normalize
        >>> df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        >>> normalizer = Normalize(mean=df.mean(), std=df.std())
        >>> transformed_df = normalizer(df)
    """

    def fit(self, datasource: DataSource) -> None:
        self.mean = datasource.mean
        self.std = datasource.std

    def transform(self, df: pd.DataFrame | torch.Tensor) -> pd.DataFrame | torch.Tensor:
        if isinstance(df, torch.Tensor):
            raise NotImplementedError("Torch tensors not yet supported for Normalize")
        normalized_df = (df - self.mean) / self.std
        return normalized_df
