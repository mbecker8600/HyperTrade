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

## Contributing

Contributions are welcome! See the CONTRIBUTING.md file (if one exists or when
one is created).
