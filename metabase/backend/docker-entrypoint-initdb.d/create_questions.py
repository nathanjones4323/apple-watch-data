import os

import pandas as pd
from dotenv import load_dotenv
from loguru import logger

from db.utils import init_metabase_db_connection

dotenv_path = os.path.join(os.path.dirname(__file__), '...', '.env')
logger.debug(f"dotenv_path: {dotenv_path}")
try:
    load_dotenv(dotenv_path)
    logger.success("Loaded .env file")
except:
    logger.error("Could not load .env file")

def create_strong_questions(csv_path):
    try:
        # Read in CSV
        df = pd.read_csv(csv_path)
    except:
        logger.error("Could not read Strong data from CSV")
    try:
        conn = init_metabase_db_connection()
    except:
        logger.error("Could not connect to metabase DB")
    try:
        df["id"] = df.index + 1
        # Write to Database
        df.to_sql(name="z_report_card_test", con=conn, schema="public", if_exists="replace", index=False)
        logger.success("Created Strong questions in metabase")
        # Close out DB connection
        conn.close()
    except:
        logger.error("Could not create strong questions in metabase")

create_strong_questions("./metabase/init/strong_questions.csv")