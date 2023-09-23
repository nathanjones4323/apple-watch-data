import os
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
from loguru import logger

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
pivot_df.to_csv("apple_health_export.csv")

# Statistics
df = pivot_df.resample('M').agg({'BodyMass' : np.mean,
                                 'DistanceWalkingRunning' : sum})

# Averages by Time Period
averages_df = pivot_df.resample('M').agg(np.mean)

# Sums by Time Period
sums_df = pivot_df.resample('M').agg(sum)

# Max by Time Period
maxs_df = pivot_df.resample('M').agg(max)

import matplotlib.pyplot as plt
import seaborn as sns

sns.lineplot(data=averages_df, x=averages_df.index, y="ActiveEnergyBurned")
plt.show()

for i in np.sort(data["type"].unique()):
    print(i)