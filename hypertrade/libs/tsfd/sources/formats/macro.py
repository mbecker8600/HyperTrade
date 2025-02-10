from hypertrade.libs.tsfd.schemas.macro import global_macro_schema
from hypertrade.libs.tsfd.sources.types import DataSourceFormat


class GlobalMacroFormat(DataSourceFormat):

    schema = global_macro_schema
