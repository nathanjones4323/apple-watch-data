import os

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
    logger.debug(f"my_custom_json: {my_custom_json}")
    try:
        api_response = mb.create_card(question_name, db_id=db_id, collection_id=collection_id,
                                      table_id=table_id, custom_json=my_custom_json)
        logger.success(f"Successfully created question - {question_name}")
    except Exception as e:
        logger.error(f"Could not create question - {question_name}\n{e}")


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
create_sql_question(mb, query=query, question_name="Test Card",
                    display="table", db_id=2, collection_id=2, table_id=48, visualization_settings=visualization_settings)


# Example cURL for adding filters to a question
# curl 'http://localhost:3000/api/card/15' \
#   -X 'PUT' \
#   -H 'Accept: application/json' \
#   -H 'Accept-Language: en-US,en;q=0.9' \
#   -H 'Connection: keep-alive' \
#   -H 'Content-Type: application/json' \
#   -H 'Cookie: metabase.DEVICE=9e6dd686-cb71-4d70-83db-94378b85841f; metabase.TIMEOUT=alive; _ga=GA1.1.1934716577.1697854711; _gid=GA1.1.2070902220.1697854711; metabase.SESSION=05406d75-24aa-483e-a62c-ff09333fbbe6' \
#   -H 'Origin: http://localhost:3000' \
#   -H 'Referer: http://localhost:3000/question/15-test-card' \
#   -H 'Sec-Fetch-Dest: empty' \
#   -H 'Sec-Fetch-Mode: cors' \
#   -H 'Sec-Fetch-Site: same-origin' \
#   -H 'Sec-GPC: 1' \
#   -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36' \
#   -H 'sec-ch-ua: "Chromium";v="118", "Brave";v="118", "Not=A?Brand";v="99"' \
#   -H 'sec-ch-ua-mobile: ?0' \
#   -H 'sec-ch-ua-platform: "macOS"' \
#   --data-raw $'{"name":"Test Card","cache_ttl":null,"dataset":false,"dataset_query":{"type":"native","native":{"template-tags":{"start_date":{"type":"text","name":"start_date","id":"b140beed-a498-4ffe-8352-8294f74afe4d","display-name":"Start Date","default":"month","required":true},"end_date":{"type":"text","name":"end_date","id":"834b0b37-bec8-4189-8ae2-4ed563d24ecc","display-name":"End Date","required":true,"default":"true"}},"query":"select \\n    date_trunc(\'day\', created_at) as time_period\\n    , workout_name\\n    , exercise_name\\n    , count(*) as number_of_sets\\nfrom strong_app_raw\\nwhere 1=1\\n    [[ and {{start_date}} ]]\\n    [[ and {{end_date}} ]]\\ngroup by time_period, workout_name, exercise_name\\norder by time_period desc, number_of_sets desc"},"database":2},"display":"table","description":null,"visualization_settings":{"graph.show_values":true,"graph.x_axis.title_text":null,"graph.y_axis.title_text":null,"graph.dimensions":["time_period","workout_name","exercise_name"],"graph.metrics":["time_period","workout_name","exercise_name"]},"parameters":[{"id":"b140beed-a498-4ffe-8352-8294f74afe4d","type":"category","target":["variable",["template-tag","start_date"]],"name":"Start Date","slug":"start_date","default":"month"},{"id":"834b0b37-bec8-4189-8ae2-4ed563d24ecc","type":"category","target":["variable",["template-tag","end_date"]],"name":"End Date","slug":"end_date","default":"true"}],"parameter_mappings":[],"archived":false,"enable_embedding":false,"embedding_params":null,"collection_id":2,"collection_position":null,"collection_preview":true,"result_metadata":null}' \
#   --compressed

# Example of adding filters to a question via the API
# json = {
#     "parameters":[
#         {"id":"b140beed-a498-4ffe-8352-8294f74afe4d",
#          "type":"category",
#          "target":["variable",["template-tag","start_date"]],
#          "name":"Start Date",
#          "slug":"start_date",
#          "default":"month"},
#          {"id":"834b0b37-bec8-4189-8ae2-4ed563d24ecc",
#           "type":"category",
#           "target":["variable",["template-tag","end_date"]],
#           "name":"End Date",
#           "slug":"end_date",
#           "default":"true"}
#          ]
# }
# mb.put(endpoint="/api/card/15", json=json)
