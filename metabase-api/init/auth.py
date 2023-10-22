import os
import time

from dotenv import load_dotenv
from loguru import logger
from metabase_api import Metabase_API


def auth():
    """Authenticates with the Metabase API.

    Returns:
        Metabase_API: An instance of the Metabase_API class.
    """
    # Load environment variables from the .env file
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    try:
        load_dotenv(dotenv_path)
        logger.success("Loaded .env file")
    except:
        logger.error("Could not load .env file")

    for i in range(300):
        time.sleep(1)
        i = 300 - i
        if i % 25 == 0:
            logger.info(
                f"Waiting for Metabase to start... {i} seconds remaining")

    try:
        # Have to use the container name as the host name because that is the name of the service in the docker-compose.yml file
        mb = Metabase_API(domain="http://metabase:3000/",
                          email=os.getenv("MB_ADMIN_EMAIL"), password=os.getenv("MB_ADMIN_PASSWORD"))
        logger.success("Connected to Metabase API")
    except:
        logger.error("Could connect to Metabase API")

    return mb
