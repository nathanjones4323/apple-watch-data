import os

from dotenv import load_dotenv
from loguru import logger

from db.utils import init_db_connection

# Load environment variables from the .env file
### os.path.dirname(__file__): Gives you the directory of your Python script.
### ..: Moves up one level to the parent directory.
### 'db': Enters the db directory.
### '.env': Specifies the .env file you want to access.
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
        transformed_data.to_sql(name="apple_health_raw", con=conn, schema="public", if_exists="replace", index_label="id")
        # Close out DB connection
        conn.close()
    except:
        logger.error("Could not load apple_health data to DB")

def load_strong_app_data(transformed_data):
    try:
        conn = init_db_connection()
        # Write to Database
        transformed_data.to_sql(name="strong_app_raw", con=conn, schema="public", if_exists="replace", index_label="id")
        # Close out DB connection
        conn.close()
    except:
        logger.error("Could not load strong_app data to DB")