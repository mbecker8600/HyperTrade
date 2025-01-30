# Example usage
from hypertrade.libs.tsda.core.factory import DataSourceFactory


if __name__ == "__main__":
    # Create a CSV data source
    csv_source = DataSourceFactory.create_source("csv", filepath="data/ohlcv_data.csv")

    # Create an OHLCV dataset
    ohlcv_dataset = OHLCVDataset(source=csv_source)

    # Fetch OHLCV data for a specific timestamp and assets
    timestamp = pd.Timestamp("2023-10-26 09:30:00", tz="America/New_York")
    assets = ["AAPL", "MSFT"]
    ohlcv_data = ohlcv_dataset.fetch(timestamp, assets)
    print("OHLCV Data:")
    print(ohlcv_data)

    # Fetch current price for a specific timestamp and assets
    current_price = ohlcv_dataset.fetch_current_price(timestamp, assets)
    print("\nCurrent Price (OHLCV):")
    print(current_price)

    # Create a MongoDB data source
    mongo_source = DataSourceFactory.create_source(
        "mongodb",
        connection_string="mongodb://localhost:27017/",  # Example connection string
        database_name="financial_data",
        collection_name="tick_data",
    )

    # Create a tick dataset
    tick_dataset = TickDataset(source=mongo_source)

    # Fetch tick data for a specific timestamp and assets
    tick_data = tick_dataset.fetch(timestamp, assets)
    print("\nTick Data:")
    print(tick_data)

    # Fetch current price from tick data
    current_price_tick = tick_dataset.fetch_current_price(timestamp, assets)
    print("\nCurrent Price (Tick):")
    print(current_price_tick)

    # Create a macroeconomic dataset
    macro_source = DataSourceFactory.create_source(
        "csv", filepath="data/macro_data.csv"
    )
    macro_dataset = MacroeconomicDataset(source=macro_source)
    macro_data = macro_dataset.fetch(
        timestamp, indicators=["GDP", "Inflation"], region="US"
    )
    print("\nMacroeconomic Data:")
    print(macro_data)

    # Create a news dataset
    news_source = DataSourceFactory.create_source(
        "mongodb",  # Example: News data from MongoDB
        connection_string="mongodb://localhost:27017/",
        database_name="financial_data",
        collection_name="news_data",
    )
    news_dataset = NewsDataset(source=news_source)
    news_data = news_dataset.fetch(timestamp, keywords=["technology", "stocks"])
    print("\nNews Data:")
    print(news_data)
