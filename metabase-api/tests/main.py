import os
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


def set_visualization_settings(show_values: bool = True, x_axis_title: str = None, y_axis_title: str = None, dimensions: list = None, metrics: list = None):
    """Sets the visualization settings for a Metabase question.

    Args:
        show_values (bool, optional): True to show the data points in a visual, False to hide them. Defaults to True.
        x_axis_title (str, optional): The title of the x-axis. Defaults to None, which will use the SQL column name.
        y_axis_title (str, optional): The title of the y-axis. Defaults to None, which will leave the y-axis untitled.
        dimensions (list, optional): The variables to group on / have on the x-axis (order matters). Defaults to None.
        metrics (list, optional): The variables to plot (order matters). Defaults to None.

    Returns:
        dict: A dictionary of the visualization settings to be passed to the `create_sql_question` function.
    """
    visualization_settings = {
        "graph.show_values": show_values,
        "graph.x_axis.title_text": x_axis_title,
        "graph.y_axis.title_text": y_axis_title,
        "graph.dimensions": dimensions,
        "graph.metrics": metrics
    }
    return visualization_settings


def create_sql_question(mb: Metabase_API, query: str, display: str = "table", question_name: str = "test_card", db_id: int = 2, collection_id: int = 2, table_id: int = 48, visualization_settings: dict = None):
    try:
        # Parse the table name from the query
        table_name = query.strip().split("from")[1].strip().split("\n")[0]
        # Parse the timestamp field name from the query
        timestamp_field_name = query.strip().split(
            "date_trunc({{date_granularity}}, ")[1].strip().split(")")[0]
        # Get the field mappings
        field_mappings = get_field_mappings(mb=mb, table_field_tuples=[
                                            (table_name, timestamp_field_name)])
        # Pull out field data from the field mappings
        field_id = field_mappings[0]["field_id"]
        field_name = field_mappings[0]["field_name"]
        field_display_name = field_mappings[0]["field_display_name"]

    except Exception as e:
        logger.error(f"Could not parse table name from query: {e}")
        logger.debug(f"Query: {query}")

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
                         "default": ["Week"]},
                    field_name:
                        {"type": "dimension",
                         "name": field_name,
                         "id": str(uuid.uuid4()),
                         "display-name": field_display_name,
                         "dimension": ["field", field_id, None],
                         "widget-type": "date/all-options"}
                }
            },
            'type': 'native',
        },
        "visualization_settings": visualization_settings
    }
    try:
        api_response = mb.create_card(question_name, db_id=db_id, collection_id=collection_id,
                                      table_id=table_id, custom_json=my_custom_json)
        logger.success(f"Successfully created question - {question_name}")
    except Exception as e:
        logger.error(f"Could not create question - {question_name}\n{e}")


def get_field_metadata(mb: Metabase_API, table_name: str, field_name: str) -> int:
    """Gets the field metadata for a given table and field name."""

    try:
        table_metadata = mb.get_table_metadata(table_name=table_name)
        logger.success(
            f"Successfully retrieved table metadata for {table_name}")
    except Exception as e:
        logger.error(
            f"Could not retrieve table metadata for {table_name}\n{e}")

    field_dictionary = [dictionary for dictionary in table_metadata["fields"]
                        if dictionary["name"] == field_name][0]
    field_id = field_dictionary["id"]
    field_display_name = field_dictionary["display_name"]

    return field_id, field_display_name


def get_field_mappings(mb: Metabase_API, table_field_tuples: list) -> dict:
    """Gets the field mappings for a given list of table and field tuples."""
    field_mapping_list = []
    field_mapping = {}
    for table_name, field_name in table_field_tuples:
        field_id, field_display_name = get_field_metadata(
            mb, table_name, field_name)
        field_mapping["field_id"] = field_id
        field_mapping["field_name"] = field_name
        field_mapping["field_table_name"] = table_name
        field_mapping["field_display_name"] = field_display_name
        field_mapping_list.append(field_mapping)

    return field_mapping_list


query = """
        select 
            date_trunc({{date_granularity}}, created_at) as time_period
            , workout_name
            , exercise_name
            , count(*) as number_of_sets
        from strong_app_raw
        where 1=1
            [[ and {{created_at}} ]]
        group by time_period, workout_name, exercise_name
        order by time_period desc, number_of_sets desc
        """
visualization_settings = set_visualization_settings(
    dimensions=["time_period", "workout_name", "exercise_name"],
    metrics=["time_period", "workout_name", "exercise_name"]
)
create_sql_question(mb, query=query, question_name="Test Card",
                    display="table", db_id=2, collection_id=2, table_id=40, visualization_settings=visualization_settings)
