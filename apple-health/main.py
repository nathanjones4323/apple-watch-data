from loguru import logger

from extract import extract_apple_health_data, extract_strong_app_data
from load import load_apple_health_data, load_strong_app_data
from transform import transform_apple_health_data, transform_strong_data

# Create a new logger
logger.add("logs/log_{time}.log", rotation="500 MB", compression="zip")
logger.debug(f"Starting {__file__}")

# Extract data
apple_data = extract_apple_health_data(path="/Users/nathanjones/Downloads/health_exports/apple_health_export/export.xml")
strong_data = extract_strong_app_data(path="/Users/nathanjones/Downloads/health_exports/strong_export/strong.csv")

# Transform data
apple_health_df = transform_apple_health_data(apple_data)
strong_df = transform_strong_data(strong_data)

# Load data
load_apple_health_data(apple_health_df)
load_strong_app_data(strong_data)