import uuid

from loguru import logger
from metabase_api import Metabase_API


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
    my_custom_json = {
        'name': question_name,
        "display": display,
        'dataset_query': {
            'database': db_id,
            'native': {'query': query.strip()},
            'type': 'native'
        },
        "visualization_settings": visualization_settings
    }
    try:
        api_response = mb.create_card(question_name, db_id=db_id, collection_id=collection_id,
                                      table_id=table_id, custom_json=my_custom_json)
        logger.success(f"Successfully created question - {question_name}")
    except Exception as e:
        logger.error(f"Could not create question - {question_name}\n{e}")


def create_sql_timeseries_question(mb: Metabase_API, query: str, display: str = "table", question_name: str = "test_card", db_id: int = 2, collection_id: int = 2, table_id: int = 48, visualization_settings: dict = None, timestamp_column: str = "created_at"):

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
                    timestamp_column:
                        {"type": "dimension",
                         "name": timestamp_column,
                         "id": str(uuid.uuid4()),
                         "display-name": timestamp_column.replace("_", " ").title(),
                         "dimension": ["field", 457, None],
                         "widget-type": "date/all-options"}
                }
            },
            'type': 'native',
        },
        "visualization_settings": visualization_settings
    }
    logger.debug(f"my_custom_json: {my_custom_json}")
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
    query = """
        select 
            workout_name
            , count(distinct workout_id) as number_of_workouts
            , avg(duration) / 60.0 as average_workout_length_minutes
            , percentile_cont(0.5) within group (order by duration) / 60.0 as median_workout_length_minutes
        from strong_app_raw
        where 1=1
        group by workout_name
        order by average_workout_length_minutes desc
        """
    visualization_settings = set_visualization_settings(
        x_axis_title="Workout Type",
        y_axis_title="Avg. Workout Duration (min)",
        dimensions=["workout_name"],
        metrics=["average_workout_length_minutes",
                 "median_workout_length_minutes"]
    )
    create_sql_question(mb, query=query, question_name="Workout Duration by Type",
                        display="bar", db_id=2, collection_id=2, table_id=48, visualization_settings=visualization_settings)


def strong_sets(mb: Metabase_API):
    query = """
        select 
            date_trunc('day', created_at) as time_period
            , workout_name
            , count(*) as number_of_sets
        from strong_app_raw
        group by time_period, workout_name
        order by time_period, number_of_sets desc
        """
    visualization_settings = set_visualization_settings(
        x_axis_title="Time Period",
        y_axis_title="Number of Sets",
        dimensions=["time_period", "workout_name"],
        metrics=["number_of_sets"]
    )
    create_sql_question(mb, query=query, question_name="Sets Over Time",
                        display="line", db_id=2, collection_id=2, table_id=48, visualization_settings=visualization_settings)


def strong_exercises_by_volume(mb: Metabase_API):
    query = """
        select 
            date_trunc('day', created_at) as time_period
            , workout_name
            , exercise_name
            , count(*) as number_of_sets
        from strong_app_raw
        where 1=1	
        group by time_period, workout_name, exercise_name
        order by time_period desc, number_of_sets desc
        """
    visualization_settings = set_visualization_settings(
        dimensions=["time_period", "workout_name", "exercise_name"],
        metrics=["time_period", "workout_name", "exercise_name"]
    )
    create_sql_question(mb, query=query, question_name="Exercises by Volume",
                        display="table", db_id=2, collection_id=2, table_id=48, visualization_settings=visualization_settings)


def strong_workouts(mb: Metabase_API):
    query = """
        select 
            date_trunc('month', created_at) as time_period
            , workout_name
            , count(distinct workout_id) as number_of_workout_days
        from strong_app_raw
        group by time_period, workout_name
        order by time_period desc, number_of_workout_days desc
        """
    visualization_settings = set_visualization_settings(
        x_axis_title="Time Period",
        y_axis_title="Number of Sets",
        dimensions=["time_period", "workout_name"],
        metrics=["number_of_workout_days"]
    )
    create_sql_question(mb, query=query, question_name="Workouts Over Time",
                        display="line", db_id=2, collection_id=2, table_id=48, visualization_settings=visualization_settings)


############################################
# Apple Health Questions
############################################
def apple_calories(mb: Metabase_API):
    query = """
        select 
            date_trunc('day', end_date) as time_period
            , sum(active_energy_burned) as active_calories_burned
            , sum(basal_energy_burned) as resting_calories_burned
            , sum(active_energy_burned) + sum(basal_energy_burned) as total_calories_burned
        from apple_health_raw
        where 1=1
        group by time_period
        order by time_period desc
        """
    visualization_settings = set_visualization_settings(
        x_axis_title="Time Period",
        y_axis_title="Calories Burned",
        dimensions=["time_period"],
        metrics=["total_calories_burned",
                 "active_calories_burned", "resting_calories_burned"]
    )
    create_sql_question(mb, query=query, question_name="Calories Burned Over Time",
                        display="line", db_id=2, collection_id=3, table_id=40, visualization_settings=visualization_settings)

# def time_period_metric_template(metric_query: str, timestamp_column: str):
#     query = f"""
#         select
#             date_trunc({{{{date_granularity}}}}, {timestamp_column}) as time_period{metric_query}
#         where 1=1
#             and case
#             when
#                 lower(trim({{{{date_granularity}}}})) = 'quarter'
#             then
#                 {timestamp_column} between date_trunc({{{{date_granularity}}}}, now() - (3 * {{{{time_periods_ago}}}}::numeric || ' months')::interval)
#                 and (case when {{{{include_current_time_period}}}}::boolean='true' then now() else date_trunc({{{{date_granularity}}}}, now()) end)
#             else
#                 {timestamp_column} between date_trunc({{{{date_granularity}}}}, now() - ({{{{time_periods_ago}}}}::numeric || {{{{date_granularity}}}})::interval)
#                 and (case when {{{{include_current_time_period}}}}::boolean='true' then now() else date_trunc({{{{date_granularity}}}}, now()) end)
#             end
#         group by time_period
#         order by time_period desc
#         """
#     return query
