# Time-series Financial Dataset (tsfd)

The tsfd library provides unified interfaces for fetching and processing
different types of data (e.g., OHLCV, tick, macro, news). It uses a “Source”
(CSV, MongoDB, etc.) to retrieve raw data, then processes it into useful formats
via specialized Datasets.

## Key Features

- **Unified Interface**: Access diverse financial data through a consistent API.
- **Modular Design**: Easily switch between different data sources (e.g., CSV
  files, databases) and dataset types (e.g., OHLCV, tick).
- **Data Processing**: Transform raw data into readily usable formats for
  analysis and modeling.
- **Extensible**: Add new data sources and datasets as needed.
- **Pythonic Implementation:** Seamless integration with popular Python
  libraries like Pandas, NumPy, and PyTorch.

## Installation

```bash
pip install tsfd
```

## Usage

0. **Data Ingestion (Optional)**: Ingest your data into a format compatible with
   your chosen Source. (e.g., CSV, Database)
1. **Create a Source**: Instantiate a Source object corresponding to your data's
   location (e.g., CSVSource, DatabaseSource). This handles raw data access.
   Specify any necessary parameters like file paths or database credentials.
2. **Create a Dataset**: Instantiate a Dataset object (e.g., OHLCVDataset,
   TickDataset), passing the Source object as an argument. The Dataset defines
   how the raw data is processed and presented.
3. Call dataset methods (fetch, fetch_current_price, etc.) to retrieve data.

## Available Datasets

- **OHLCVDataset**: Provides methods to fetch OHLCV data
- _(More datasets can be added - TickDataset, MacroDataset, NewsDataset, etc.)_

## Available Sources

- **CSVSource**: Reads data from CSV files. Requires a filepath parameter upon
  instantiation.
- _(More sources can be added - DatabaseSource, APISource, etc.)_

## Custom Data Source and Dataset Example

### Custom Data Source

```python
from hypertrade.libs.tsfd.sources.types import DataSource, Granularity
import pandas as pd
from pandas._libs.tslibs.nattype import NaTType
from typing import Optional

class CustomDataSource(DataSource):
    def __init__(self, data: pd.DataFrame, granularity: Granularity = Granularity.DAILY):
        super().__init__(granularity)
        self.data = data

    def _fetch(
        self,
        timestamp: Optional[pd.Timestamp | NaTType | slice | int] = None,
    ) -> pd.DataFrame:
        if timestamp is None:
            return self.data
        if isinstance(timestamp, slice):
            return self.data.loc[timestamp.start:timestamp.stop]
        if isinstance(timestamp, int):
            timestamp = self.data.index[timestamp]
        return self.data.loc[timestamp]

    def __len__(self) -> int:
        return len(self.data)
```

### Custom Dataset

```python
from hypertrade.libs.tsfd.datasets.types import TimeSeriesDataset
from hypertrade.libs.tsfd.sources.types import DataSource
import pandas as pd
from pandas._libs.tslibs.nattype import NaTType
from typing import Optional

class CustomDataset(TimeSeriesDataset):
    def __init__(self, data_source: DataSource, name: Optional[str] = None):
        super().__init__(data_source, name)

    def _load_data(self, idx: pd.Timestamp | NaTType | slice | int) -> pd.DataFrame:
        return self.data_source.fetch(timestamp=idx)
```

### Custom Dataset & Datasource Usage

```python
import pandas as pd
from hypertrade.libs.tsfd.sources.types import Granularity

# Create a sample DataFrame
data = pd.DataFrame({
    "value": [1, 2, 3, 4, 5],
}, index=pd.date_range("2023-01-01", periods=5, freq="D"))

# Create a custom data source
custom_data_source = CustomDataSource(data, granularity=Granularity.DAILY)

# Create a custom dataset
custom_dataset = CustomDataset(custom_data_source, name="custom_dataset")

# Fetch data from the dataset
print(custom_dataset[pd.Timestamp("2023-01-03")])
```

## Contributing

Contributions are welcome! See the CONTRIBUTING.md file (if one exists or when
one is created).
