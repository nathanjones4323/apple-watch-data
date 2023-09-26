import os

import pandas as pd
from dotenv import load_dotenv
from loguru import logger

from db.utils import init_metabase_db_connection

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
try:
    load_dotenv(dotenv_path)
    logger.success("Loaded .env file")
except:
    logger.error("Could not load .env file")

def create_strong_questions(csv_path):
    try:
        # Read in CSV
        df = pd.read_csv(csv_path)
        df["id"] = df.index + 1
        conn = init_metabase_db_connection()
        # Write to Database
        df.to_sql(name="z_report_card_test", con=conn, schema="public", if_exists="replace", index=False)
        # Close out DB connection
        conn.close()
    except:
        logger.error("Could not create strong questions in metabase")

