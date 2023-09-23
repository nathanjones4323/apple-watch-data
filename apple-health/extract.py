import os
import time
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import Connection, create_engine
from transform import transform_data
from utils import init_db_connection

# Create a new logger
logger.add("logs/log_{time}.log", rotation="500 MB", compression="zip")
logger.debug(f"Starting {__file__}")

### Read in data
# create element tree object 
tree = ET.parse('/Users/nathanjones/Downloads/apple_health_export/export.xml')

# for every health record, extract the attributes into a dictionary (columns). Then create a list (rows).
root = tree.getroot()
record_list = [x.attrib for x in root.iter('Record')]

# create DataFrame from a list (rows) of dictionaries (columns)
data = pd.DataFrame(record_list)

# proper type to dates
for col in ['creationDate', 'startDate', 'endDate']:
    data[col] = pd.to_datetime(data[col])

# value is numeric, NaN if fails
data['value'] = pd.to_numeric(data['value'], errors='coerce')

# some records do not measure anything, just count occurences
# filling with 1.0 (= one time) makes it easier to aggregate
data['value'] = data['value'].fillna(1.0)

# shorter observation names: use vectorized replace function
data['type'] = data['type'].str.replace('HKQuantityTypeIdentifier', '')
data['type'] = data['type'].str.replace('HKCategoryTypeIdentifier', '')

# pivot and resample
pivot_df = data.pivot_table(index='endDate', columns='type', values='value')

# Load environment variables from the .env file
### os.path.dirname(__file__): Gives you the directory of your Python script.
### ..: Moves up one level to the parent directory.
### 'db': Enters the db directory.
### '.env': Specifies the .env file you want to access.
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'db', '.env')
load_dotenv(dotenv_path)

# Write to Database
conn = init_db_connection()
transformed_data = transform_data(pivot_df)
pivot_df.to_sql(name="apple_health_raw", con=conn, schema="public", if_exists="replace")
# Close out DB connection
conn.close()
