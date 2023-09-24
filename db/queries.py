import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from utils import init_db_connection

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.', 'db', '.env')
load_dotenv(dotenv_path)

# Create a connection to the database
