from abc import ABC
from typing import ClassVar

import pandera as pa


class DataSourceFormat(ABC):

    schema: ClassVar[pa.DataFrameSchema]
