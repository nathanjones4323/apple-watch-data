import uuid

from filters.utils import add_field_filters, get_field_mappings
from loguru import logger
from metabase_api import Metabase_API
from queries.apple_health import query_calories_burned
from queries.strong import (query_count_by_workout_type,
                            query_duration_by_workout_type,
                            query_sets_by_workout_type,
                            query_volume_by_exercise_type)


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


def create_sql_question(mb: Metabase_API, query: str, display: str = "table", question_name: str = "test_card", db_id: int = 2, collection_id: int = 2, table_id: int = 48, visualization_settings: dict = None, timestamp_field_name: str = "created_at"):
    try:
        # Parse the table name from the query
        table_name = query.split("from")[1].strip().split("\n")[0]
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

############################################
# Strong App Questions
############################################


def strong_workout_duration_by_type(mb: Metabase_API):
    query = query_duration_by_workout_type()
    visualization_settings = set_visualization_settings(
        x_axis_title="Workout Type",
        y_axis_title="Avg. Workout Duration (min)",
        dimensions=["workout_name"],
        metrics=["average_workout_length_minutes",
                 "median_workout_length_minutes"]
    )
    create_sql_question(mb, query=query, question_name="Workout Duration by Type",
                        display="bar", db_id=2, collection_id=2, table_id=48, visualization_settings=visualization_settings, timestamp_field_name="created_at")


def strong_sets_by_workout_type(mb: Metabase_API):
    query = query_sets_by_workout_type()
    visualization_settings = set_visualization_settings(
        x_axis_title="Time Period",
        y_axis_title="Number of Sets",
        dimensions=["time_period", "workout_name"],
        metrics=["number_of_sets"]
    )
    create_sql_timeseries_question(mb, query=query, question_name="Sets Over Time",
                                   display="line", db_id=2, collection_id=2, table_id=48, visualization_settings=visualization_settings)


def strong_volume_by_exercise_type(mb: Metabase_API):
    query = query_volume_by_exercise_type()
    visualization_settings = set_visualization_settings(
        dimensions=["time_period", "workout_name", "exercise_name"],
        metrics=["time_period", "workout_name", "exercise_name"]
    )
    create_sql_timeseries_question(mb, query=query, question_name="Exercises by Volume",
                                   display="table", db_id=2, collection_id=2, table_id=48, visualization_settings=visualization_settings)


def strong_count_by_workout_type(mb: Metabase_API):
    query = query_count_by_workout_type()
    visualization_settings = set_visualization_settings(
        x_axis_title="Time Period",
        y_axis_title="Number of Sets",
        dimensions=["time_period", "workout_name"],
        metrics=["number_of_workout_days"]
    )
    create_sql_timeseries_question(mb, query=query, question_name="Workouts Over Time",
                                   display="line", db_id=2, collection_id=2, table_id=48, visualization_settings=visualization_settings)


############################################
# Apple Health Questions
############################################
def apple_calories(mb: Metabase_API):
    query = query_calories_burned()
    visualization_settings = set_visualization_settings(
        x_axis_title="Time Period",
        y_axis_title="Calories Burned",
        dimensions=["time_period"],
        metrics=["total_calories_burned",
                 "active_calories_burned", "resting_calories_burned"]
    )
    create_sql_timeseries_question(mb, query=query, question_name="Calories Burned Over Time",
                                   display="line", db_id=2, collection_id=3, table_id=40, visualization_settings=visualization_settings)
