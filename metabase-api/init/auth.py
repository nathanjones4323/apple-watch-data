import os
import time

import pandas as pd
from dotenv import load_dotenv
from loguru import logger
from metabase_api import Metabase_API

from ...db.utils import init_metabase_db_connection


def is_initialized():
    try:
        conn = init_metabase_db_connection()
        logger.success("Connected to database")
        df = pd.read_sql("select * from report_card limit 1", conn)
        if df.empty:
            logger.warning(
                "Existing Metabase questions not found, initializing...")
            return False
        else:
            logger.warning("Existing Metabase questions found")
            return True
    except Exception as e:
        logger.error(f"Could not connect to database: {e}")
        return False


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

    # If Metabase questions not initialized then wait 5 minutes for user to completed admin creation through the Metabase UI
    if not is_initialized():
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
    except Exception as e:
        logger.error(f"Could not connect to Metabase API: {e}")

    return mb
