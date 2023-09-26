import xml.etree.ElementTree as ET

import pandas as pd


def extract_apple_health_data(path) -> pd.DataFrame:
    # create element tree object 
    tree = ET.parse(path)

    # for every health record, extract the attributes into a dictionary (columns). Then create a list (rows).
    root = tree.getroot()
    record_list = [x.attrib for x in root.iter('Record')]

    # create DataFrame from a list (rows) of dictionaries (columns)
    data = pd.DataFrame(record_list)
    return data

def extract_strong_app_data(path) -> pd.DataFrame:
    data = pd.read_csv(path)
    return data