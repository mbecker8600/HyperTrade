from typing import List, Optional, Protocol, runtime_checkable

import pandas as pd
import torch

from hypertrade.libs.tsfd.sources.types import DataSource


@runtime_checkable
class Transform(Protocol):
    """
    A transform interface for DataFrame objects. Accepts a DataFrame,
    applies some transformation, and returns the transformed DataFrame.
    """

    def __call__(
        self, df: pd.DataFrame | torch.Tensor
    ) -> pd.DataFrame | torch.Tensor: ...


@runtime_checkable
class FitTransform(Protocol):
    """
    Protocol defining a 'fit' and 'transform' method for DataFrame objects.
    """

    def fit(self, datasource: DataSource) -> None: ...

    def transform(
        self, df: pd.DataFrame | torch.Tensor
    ) -> pd.DataFrame | torch.Tensor: ...

    def __call__(
        self, datasource: DataSource, df: pd.DataFrame | torch.Tensor
    ) -> pd.DataFrame | torch.Tensor:
        self.fit(datasource)
        return self.transform(df)


class Compose:
    """ """

    def __init__(
        self,
        transforms: List[Transform | FitTransform],
        datasource: Optional[DataSource] = None,
    ) -> None:
        self.transforms = transforms
        self.datasource = datasource

    def __call__(self, df: pd.DataFrame | torch.Tensor) -> pd.DataFrame | torch.Tensor:
        for t in self.transforms:
            # Each transform should adhere to the DataFrameTransform protocol
            if isinstance(t, FitTransform):
                if self.datasource is None:
                    raise ValueError("FitTransform requires a DataSource")
                df = t(self.datasource, df)
            elif isinstance(t, Transform):
                df = t(df)
            else:
                raise ValueError(f"Invalid transform type: {type(t)}")
        return df
