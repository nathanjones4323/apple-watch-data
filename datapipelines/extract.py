import xml.etree.ElementTree as ET

import pandas as pd
from loguru import logger


def extract_apple_health_data(path) -> pd.DataFrame:
    # create element tree object
    tree = ET.parse(path)

    # for every health record, extract the attributes into a dictionary (columns). Then create a list (rows).
    root = tree.getroot()
    record_list = [x.attrib for x in root.iter('Record')]

    # create DataFrame from a list (rows) of dictionaries (columns)
    try:
        data = pd.DataFrame(record_list)
        logger.success("Created DataFrame from Apple Health XML file")
        logger.debug(f"Shape of DataFrame: {data.shape}")
        logger.debug(f"Data: {data}")
    except Exception as e:
        logger.error(f"Could not create DataFrame from Apple Health data: {e}")
    return data


def extract_strong_app_data(path) -> pd.DataFrame:
    try:
        data = pd.read_csv(path)
        logger.success("Created DataFrame from Strong CSV file")
        logger.debug(f"Shape of DataFrame: {data.shape}")
        logger.debug(f"Data: {data}")
    except Exception as e:
        logger.error(f"Could not read Strong CSV file: {e}")
    return data
