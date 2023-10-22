import time

from loguru import logger
from metabase_api import Metabase_API

for i in range(180):
    time.sleep(1)
    i = 180 - i
    if i % 10 == 0:
        logger.info(f"Waiting for Metabase to start... {i} seconds remaining")

# Have to use the container name as the host name because that is the name of the service in the docker-compose.yml file
mb = Metabase_API(domain="http://metabase:3000/",
                  email="nathanjones4323@gmail.com", password="450030778")

mb.create_collection("Strong App", parent_collection_name='Root')


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
            'native': {'query': query},
            'type': 'native'
        },
        "visualization_settings": visualization_settings
    }
    mb.create_card(question_name, db_id=db_id, collection_id=collection_id,
                   table_id=table_id, verbose=True, custom_json=my_custom_json)


def strong_workout_duration_by_type(mb: Metabase_API):
    query = """
        select 
            workout_name
            , count(distinct workout_id) as number_of_workouts
            , avg(duration) / 60.0 as average_workout_length_minutes
            , percentile_cont(0.5) within group (order by duration) / 60.0 as median_workout_length_minutes
        from strong_app_raw
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


strong_workout_duration_by_type(mb)
