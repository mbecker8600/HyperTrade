from hypertrade.libs.tsfd.schemas.news import headline_schema
from hypertrade.libs.tsfd.sources.types import DataSourceFormat


class HeadlineDataSourceFormat(DataSourceFormat):

    schema = headline_schema
