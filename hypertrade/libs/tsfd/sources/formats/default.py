from hypertrade.libs.tsfd.schemas.default import default_schema
from hypertrade.libs.tsfd.sources.types import DataSourceFormat


class DefaultDataSourceFormat(DataSourceFormat):

    schema = default_schema
