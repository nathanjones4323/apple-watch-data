import os
import time

from dotenv import load_dotenv
from loguru import logger

from db.utils import init_db_connection

# Load environment variables from the .env file
# os.path.dirname(__file__): Gives you the directory of your Python script.
# ..: Moves up one level to the parent directory.
# 'db': Enters the db directory.
# '.env': Specifies the .env file you want to access.
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'db', '.env')
try:
    load_dotenv(dotenv_path)
    logger.success("Loaded .env file")
except:
    logger.error("Could not load .env file")


def load_apple_health_data(transformed_data):
    try:
        conn = init_db_connection()
        # Write to Database
        transformed_data.to_sql(name="apple_health_raw", con=conn,
                                schema="public", if_exists="replace", index_label="id")
        # Close out DB connection
        conn.close()
        logger.success(
            f"Loaded {transformed_data.shape[0]} rows of Apple Health data to DB")
    except:
        logger.error("Could not load apple_health data to DB")


def load_strong_app_data(transformed_data):
    try:
        conn = init_db_connection()
        # Write to Database
        transformed_data.to_sql(name="strong_app_raw", con=conn,
                                schema="public", if_exists="replace", index_label="id")
        # Close out DB connection
        conn.close()
        logger.success(
            f"Loaded {transformed_data.shape[0]} rows of Strong App data to DB")
    except:
        logger.error("Could not load strong_app data to DB")


# Add a 10 second delay to allow the Metabase backend to start before trying to connect to it
logger.info("Waiting for Metabase backend to start...")
for i in range(10):
    time.sleep(1)
    i = 11 - i
    if i % 5 == 0:
        logger.info(
            f"Waiting for Metabase backend to start... {i} seconds remaining")
