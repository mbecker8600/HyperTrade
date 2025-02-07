from hypertrade.libs.tsfd.sources.formats.types import DataSourceFormat
from hypertrade.libs.tsfd.schemas.macro import global_macro_schema


class GlobalMacroFormat(DataSourceFormat):

    schema = global_macro_schema
