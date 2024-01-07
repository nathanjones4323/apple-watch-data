import os
import re
import uuid

from dotenv import load_dotenv
from loguru import logger
from metabase_api import Metabase_API

dotenv_path = "./metabase/.env"
try:
    load_dotenv(dotenv_path)
    logger.success("Loaded .env file")
except:
    logger.error("Could not load .env file")

try:
    # Have to use the container name as the host name because that is the name of the service in the docker-compose.yml file
    mb = Metabase_API(domain="http://localhost:3000/",
                      email=os.getenv("MB_ADMIN_EMAIL"), password=os.getenv("MB_ADMIN_PASSWORD"))
    logger.success("Connected to Metabase API")
except Exception as e:
    logger.error(f"Could not connect to Metabase API: {e}")


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


def create_sql_timeseries_question(mb: Metabase_API, query: str, display: str = "table", question_name: str = "test_card", db_id: int = 2, collection_id: int = 2, table_id: int = 48, visualization_settings: dict = None):
    try:
        # Parse the table name from the query
        table_name = query.split("from")[1].strip().split("\n")[0]
        timestamp_field_name = query.split(
            "date_trunc({{date_granularity}}, ")[1].strip().split(")")[0]
        # Get the field mappings
        field_mappings = get_field_mappings(mb=mb, table_field_tuples=[
                                            (table_name, timestamp_field_name)])

    except Exception as e:
        logger.error(f"Could not parse table name from query: {e}")
        logger.debug(f"Query: {query}")

    # Create the payload for the Metabase API post request
    my_custom_json = {
        'name': question_name,
        "display": display,
        'dataset_query': {
            'database': db_id,
            'native': {
                'query': query.strip(),
                'template-tags': {
                    "date_granularity":
                        {"type": "text",
                         "name": "date_granularity",
                         "id": str(uuid.uuid4()),
                         "display-name": "Date Granularity",
                         "required": True,
                         "default": ["Week"]}
                }
            },
            'type': 'native',
        },
        "visualization_settings": visualization_settings
    }
    # Add the field filters to the payload (template-tags)
    my_custom_json = add_field_filters(
        mappings=field_mappings, my_custom_json=my_custom_json)

    try:
        api_response = mb.create_card(question_name, db_id=db_id, collection_id=collection_id,
                                      table_id=table_id, custom_json=my_custom_json)
        logger.success(f"Successfully created question - {question_name}")
    except Exception as e:
        logger.error(f"Could not create question - {question_name}\n{e}")


def set_visualization_settings(show_values: bool = True, x_axis_title: str = None, y_axis_title: str = None, dimensions: list = None, metrics: list = None):
    """Sets the visualization settings for a Metabase question.

    Args:
        show_values (bool, optional): True to show the data points in a visual, False to hide them. Defaults to True.
        x_axis_title (str, optional): The title of the x-axis. Defaults to None, which will use the SQL column name.
        y_axis_title (str, optional): The title of the y-axis. Defaults to None, which will leave the y-axis untitled.
        dimensions (list, optional): The variables to group on / have on the x-axis (order matters). Defaults to None.
        metrics (list, optional): The variables to plot (order matters). Defaults to None.

    Returns:
        dict: A dictionary of the visualization settings to be passed to the `create_sql_question` and `create_sql_timeseries_question` functions.
    """
    visualization_settings = {
        "graph.show_values": show_values,
        "graph.x_axis.title_text": x_axis_title,
        "graph.y_axis.title_text": y_axis_title,
        "graph.dimensions": dimensions,
        "graph.metrics": metrics
    }
    return visualization_settings


def add_strong_field_filters_to_sql(query: str) -> str:
    """Replaces generic `where 1=1` with Metabase field filters for the Strong App.

    Args:
        query (str): The SQL query to be modified.

    Returns:
        str: The modified SQL query with Strong App field filters.
    """

    return query.replace("where 1=1", "where 1=1\n    [[ and {{created_at}} ]]\n    [[ and {{workout_name}} ]]\n    [[ and {{exercise_name}} }} ]]\n    [[ and reps >= {{min_reps}} ]]\n    [[ and reps <= {{max_reps}} ]]\n    [[ and weight >= {{min_weight}} ]]\n    [[ and weight <= {{max_weight}} ]]\n    [[ and set_order >= {{min_set_order}} ]]\n    [[ and set_order <= {{max_set_order}} ]]")


def query_duration_by_workout_type():
    query = """select 
    date_trunc({{date_granularity}}, created_at) as time_period
    , workout_name
    , count(*) as number_of_sets
from strong_app_raw
where 1=1
group by time_period, workout_name
order by time_period, number_of_sets desc
        """
    query = add_strong_field_filters_to_sql(query)
    return query.strip()


query = query_duration_by_workout_type()
print(query)

table_name = query.split("from")[1].strip().split("\n")[0]

# Extract filter references
filter_references = re.findall(r"\{\{(\w+)\}\}", query)

# Remove `date_granularity` from the list of filter references
filter_references.remove("date_granularity")

# Create a list of tuples of the table name and the filter reference
table_filter_tuples = [(table_name, filter_reference)
                       for filter_reference in filter_references]

# Get the field mappings
field_mappings = get_field_mappings(
    mb=mb, table_field_tuples=table_filter_tuples)

visualization_settings = set_visualization_settings(
    x_axis_title="Time Period",
    y_axis_title="Number of Sets",
    dimensions=["time_period", "workout_name"],
    metrics=["number_of_sets"]
)
create_sql_timeseries_question(mb, query=query, question_name="Sets Over Time",
                               display="line", db_id=2, collection_id=2, table_id=48, visualization_settings=visualization_settings)
