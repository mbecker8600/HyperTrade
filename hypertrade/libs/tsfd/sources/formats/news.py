from hypertrade.libs.tsfd.sources.formats.types import DataSourceFormat
from hypertrade.libs.tsfd.schemas.news import headline_schema


class HeadlineFormat(DataSourceFormat):

    schema = headline_schema
