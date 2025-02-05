# Time-series Finacial Dataset (tsfd)

The tsfd library provides unified interfaces for fetching and processing different types of data (e.g., OHLCV, tick, macro, news). It uses a “Source” (CSV, MongoDB, etc.) to retrieve raw data, then processes it into useful formats via specialized Datasets.

## Package structure

dataset_access_library/
├── core/
│ ├── dataset.py
│ ├── source.py
│ └── factory.py
├── mixins/
│ ├── ohlcv.py
│ └── tick.py
├── datasets/
│ ├── ohlcv_dataset.py
│ ├── tick_dataset.py
│ ├── macro_dataset.py
│ └── news_dataset.py
└── utils/
└── helpers.py # Example utility module

## Usage

0. Ingest data from a source to put it into a canonical format.
1. Create a data source (e.g., CSVSource).
2. Pass the source to a Dataset (e.g., OHLCVDataset).
3. Call dataset methods (fetch, fetch_current_price, etc.) to retrieve data.
