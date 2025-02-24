"""
Transformation interfaces and composition utilities for applying transforms to data.
"""

from typing import List, Optional, Protocol, runtime_checkable

import pandas as pd
import torch

from hypertrade.libs.tsfd.sources.types import DataSource


@runtime_checkable
class Transform(Protocol):
    """
    Basic transform interface for DataFrame or torch.Tensor.

    A transform should implement a __call__ method that receives and returns
    the transformed data. For example, it might drop columns, convert types, or
    apply domain-specific transformations.

    Example:
        class SomeTransform:
            def __call__(self, df):
                # do something
                return df
    """

    def __call__(
        self, df: pd.DataFrame | torch.Tensor
    ) -> pd.DataFrame | torch.Tensor: ...


@runtime_checkable
class FitTransform(Protocol):
    """
    Transform interface that requires a data source to compute parameters (fit) before transforming.

    This protocol is used for transforms that need external data (e.g., mean, std) before
    calling transform. A typical pattern is:
        fit(datasource) -> transform(data).

    Example:
        class MyFitTransform:
            def fit(self, datasource):
                # compute mean/stats from the datasource
            def transform(self, df):
                # apply your logic
                return df
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
    """
    Chains multiple transforms (Transform or FitTransform) into a single operation.

    All transforms are applied in sequence to the data. FitTransforms require a DataSource
    to compute any necessary parameters before transforming.

    Args:
        transforms: A list of Transform or FitTransform objects.
        datasource: The DataSource used to fit any FitTransform objects.

    Example:
        transforms = Compose([
            SomePreprocessingTransform(),
            YourFitTransform()
        ], datasource=some_datasource)
        result = transforms(some_dataframe)
    """

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
