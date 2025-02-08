from hypertrade.libs.tsfd.schemas.news import headline_schema
from hypertrade.libs.tsfd.sources.formats.types import DataSourceFormat


class HeadlineFormat(DataSourceFormat):

    schema = headline_schema
