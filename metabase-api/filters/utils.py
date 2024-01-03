from loguru import logger
from metabase_api import Metabase_API


def get_field_metadata(mb: Metabase_API, table_name: str, field_name: str) -> int:
    """Gets the field metadata for a given table and field name."""
    table_metadata = mb.get_table_metadata(table_name=table_name)
    field_dictionary = [dictionary for dictionary in table_metadata["fields"]
                        if dictionary["name"] == field_name][0]
    field_id = field_dictionary["id"]
    field_display_name = field_dictionary["display_name"]

    return field_id, field_display_name


def get_field_mappings(mb: Metabase_API, table_field_tuples: list) -> dict:
    """Gets the field mappings for a given list of table and field tuples."""
    field_mappings = {}
    for table_name, field_name in table_field_tuples:
        field_id, field_display_name = get_field_metadata(
            mb, table_name, field_name)
        field_mappings[field_display_name] = field_id

    return field_mappings
