from typing import List

import nasdaqdatalink
import pandas as pd
from loguru import logger

from hypertrade.libs.logging.setup import initialize_logging

# import hypertrade.libs.debugging  # donotcommit

DEFAULT_SYMBOLS = ["AAPL", "BA", "GE"]


def bulk_fetch(
    table: str = "SHARADAR/SEP",
    symbol: List[str] = DEFAULT_SYMBOLS,
    destFileRef: str = "/tmp/data/SEP_download.csv",
) -> None:

    logger.info("fetching from %s" % table)
    data: pd.DataFrame = nasdaqdatalink.get_table(table, ticker=symbol)
    logger.info("Data fetched from source. Beginning post processing")
    data.reset_index(inplace=True)
    data.drop("None", axis=1, inplace=True)
    data.set_index("date", inplace=True)

    # impute adjustments
    split_multiplier = data["closeadj"] / data["close"]
    data["open"] = data["open"] * split_multiplier
    data["high"] = data["high"] * split_multiplier
    data["low"] = data["low"] * split_multiplier
    data["close"] = data["closeadj"]
    data.drop("closeadj", axis=1, inplace=True)
    data.drop("closeunadj", axis=1, inplace=True)
    data = data.round(2)

    data.to_csv(
        path_or_buf=destFileRef,
    )


if __name__ == "__main__":
    """

    NOTE: in order to run you need to make sure you set the NASDAQ_DATA_LINK_API_KEY environment variable as
    the nasdaqdatalink uses this by default to authenticate.

    """
    initialize_logging()
    bulk_fetch(
        destFileRef="/workspaces/HyperTrade/hypertrade/libs/finance/data/tests/data/ohlvc/sample.csv"
    )
