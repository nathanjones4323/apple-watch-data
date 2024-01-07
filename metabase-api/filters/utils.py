import uuid

from loguru import logger
from metabase_api import Metabase_API


def field_base_type_to_widget_type(base_type: str) -> str:
    """Converts a field base type to a widget type."""
    base_type_to_widget_type = {
        "type/BigInteger": "number",
        "type/Boolean": "category",
        "type/Date": "date/all-options",
        "type/DateTime": "date/all-options",
        "type/DateTimeWithLocalTZ": "date/all-options",
        "type/Decimal": "number",
        "type/Float": "number",
        "type/Integer": "number",
        "type/Text": "string/=",
    }
    return base_type_to_widget_type[base_type]


def get_field_mappings(mb: Metabase_API, table_field_tuples: list) -> list:
    """Gets the field mappings for a given list of table and field tuples."""
    field_mapping_list = []
    for table_name, field_name in table_field_tuples:
        # Get the field metadata
        table_metadata = mb.get_table_metadata(table_name=table_name)
        field_dictionary = [dictionary for dictionary in table_metadata["fields"]
                            if dictionary["name"] == field_name][0]
        # Extract the field metadata we want
        field_dictionary["field_id"] = field_dictionary["id"]
        field_dictionary["field_name"] = field_name
        field_dictionary["field_table_name"] = table_name
        field_dictionary["field_display_name"] = field_dictionary["display_name"]
        field_dictionary["field_base_type"] = field_dictionary["base_type"]
        # Add the field widget-type
        field_dictionary["field_widget_type"] = field_base_type_to_widget_type(
            field_dictionary["base_type"])

        # Add the field dictionary to the list
        field_mapping_list.append(field_dictionary)

    return field_mapping_list


def add_field_filters(mappings: list, my_custom_json: dict) -> dict:
    """Add template tag sub dictionaries under the `template-tags` key in `my_custom_json`

    `my_custom_json` is the dictionary that will be passed to `create_sql_question()` in the Metabase API post request.

    This is what adds field filters to the question and links the correct database fields to the question.

    Args:
        mappings (list): A list of field mapping dictionaries returned by `get_field_mappings()`
        my_custom_json (dict): A dictionary that will be passed to `create_sql_question()` in the Metabase API post request.

    Returns:
        dict: The updated `my_custom_json` dictionary.
    """
    # Create a dictionary of template tags
    template_tags = {}
    # Iterate over mappings and add template tags
    for mapping in mappings:
        template_tags[mapping["field_name"]] = {
            "type": "dimension",
            "name": mapping["field_name"],
            "id": str(uuid.uuid4()),
            "display-name": mapping["field_display_name"],
            "dimension": ["field", mapping["field_id"], None],
            "widget-type": mapping["field_widget_type"]
        }

    # Iterate over template_tags and update my_custom_json
    for field_name, field_data in template_tags.items():
        field_id = field_data['dimension'][1]
        field_display_name = field_data['display-name']
        field_widget_type = field_data['widget-type']

        # Update my_custom_json with the corresponding sub-dictionary
        my_custom_json['dataset_query']['native']['template-tags'][field_name] = {
            "type": "dimension",
            "name": field_name,
            "id": str(uuid.uuid4()),
            "display-name": field_display_name,
            "dimension": ["field", field_id, None],
            "widget-type": field_widget_type
        }

    return my_custom_json
