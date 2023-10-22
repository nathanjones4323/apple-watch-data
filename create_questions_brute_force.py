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

print(f"dotenv_path: {dotenv_path}")
print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER')}")
print(f"POSTGRES_PASSWORD: {os.getenv('POSTGRES_PASSWORD')}")
print(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT')}")
print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB')}")
print(f"MB_DB_USER: {os.getenv('MB_DB_USER')}")
print(f"MB_DB_PASS: {os.getenv('MB_DB_PASS')}")
print(f"MB_DB_HOST: {os.getenv('MB_DB_HOST')}")
print(f"MB_DB_PORT: {os.getenv('MB_DB_PORT')}")
print(f"MB_DB_DBNAME: {os.getenv('MB_DB_DBNAME')}")
print(f"DB URL: postgresql://{os.getenv('MB_DB_USER')}:{os.getenv('MB_DB_PASS')}@{os.getenv('MB_DB_HOST')}:{os.getenv('MB_DB_PORT')}/{os.getenv('MB_DB_DBNAME')}")


# def create_strong_questions(csv_path):
#     try:
#         # Read in CSV
#         df = pd.read_csv(csv_path)
#     except:
#         logger.error("Could not read Strong data from CSV")
#     try:
#         conn = init_metabase_db_connection()
#     except:
#         logger.error("Could not connect to metabase DB")
#     try:
#         df["id"] = df.index + 1
#         # Write to Database
#         df.to_sql(name="z_report_card_test", con=conn,
#                   schema="public", if_exists="replace", index=False)
#         logger.success("Created Strong questions in metabase")
#         # Close out DB connection
#         conn.close()
#     except:
#         logger.error("Could not create strong questions in metabase")


# create_strong_questions("./metabase/init/strong_questions.csv")
