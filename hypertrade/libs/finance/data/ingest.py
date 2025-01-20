from typing import List
from loguru import logger
from urllib.request import urlopen
import os
import nasdaqdatalink
import pandas as pd

from hypertrade.libs.logging.setup import initialize_logging
import hypertrade.libs.debugging  # donotcommit


def bulk_fetch(
    table: str = "SHARADAR/SEP",
    symbol: List[str] = ["AAPL", "BA", "GE"],
    destFileRef: str = "/tmp/data/SEP_download.csv",
) -> None:

    logger.info("fetching from %s" % table)
    data: pd.DataFrame = nasdaqdatalink.get_table(
        table,
        ticker=symbol,
    )

    data.to_csv(
        path_or_buf=destFileRef,
    )


if __name__ == "__main__":
    """

    NOTE: in order to run you need to make sure you set the NASDAQ_DATA_LINK_API_KEY environment variable as
    the nasdaqdatalink uses this by default to authenticate.

    """
    initialize_logging()
    bulk_fetch()
