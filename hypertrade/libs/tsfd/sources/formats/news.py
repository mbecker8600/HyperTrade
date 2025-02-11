from hypertrade.libs.tsfd.schemas.news import headline_schema
from hypertrade.libs.tsfd.sources.types import DataSource, DataSourceFormat, Granularity


class HeadlineDataSourceFormat(DataSourceFormat):

    schema = headline_schema

    def __init__(self, datasource: DataSource):
        super().__init__(datasource)
        datasource.granularity = Granularity.MINUTE
