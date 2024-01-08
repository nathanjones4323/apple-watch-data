import datetime
import re
import xml.etree.ElementTree as ET

import pandas as pd


def camel_to_snake(camel_case):
  # Check for an uppercase letter in the string
    if re.search(r'[A-Z]', camel_case):
        # Replace all uppercase letters with an underscore and lowercase letter
        snake_case = re.sub(r'([A-Z])', lambda x: '_' +
                            x.group(0).lower(), camel_case)
        # Remove the first underscore only if it is the first character in the string
        snake_case = re.sub(r'^_', '', snake_case)
        # Remove any whitespaces
        snake_case = re.sub(r'\s', '', snake_case)
    else:
        snake_case = camel_case.lower()
        # Remove any whitespaces
        snake_case = re.sub(r'\s', '', snake_case)
    return snake_case


# create element tree object
tree = ET.parse("./data/apple_health_export/export.xml")

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
data['type'] = data['type'].str.replace(
    'HKDataTypeSleepDurationGoal', 'SleepDurationGoal')

# pivot and resample
pivot_df = data.pivot_table(
    index=['endDate', 'creationDate', 'startDate', 'sourceName'], columns='type', values='value')
pivot_df.columns
# Make endDate a column instead of the index
pivot_df.reset_index(inplace=True)

# rename columns
pivot_df.columns = [camel_to_snake(col) for col in pivot_df.columns]
pivot_df.shape
sleep_df = pivot_df[(pivot_df["sleep_analysis"].notnull()) & (
    pivot_df["source_name"].str.contains("Watch", regex=False))]
activity_df = pivot_df[(pivot_df["sleep_analysis"].isnull())]

sleep_df = pivot_df[pivot_df["sleep_analysis"].notnull()]
sleep_df = sleep_df[['creation_date', 'start_date', 'end_date',
                     'sleep_analysis', 'apple_sleeping_wrist_temperature', 'sleep_duration_goal', 'source_name']]

# calulate time between date(s)
sleep_df['time_asleep'] = sleep_df['end_date'] - sleep_df['start_date']

# records are grouped by creation date, so lets used that to sum up the values we need here
# total time asleep as a sum of the asleep time
# awake and bed times are max's and min's
# sleep count is the number of times the Apple Watch detected movement
# rem is the number of sleep cycles over 90 minutes (divded by 90 if they were longer than 1 cycle)
sleep_df = sleep_df.groupby('creation_date').agg(total_time_asleep=('time_asleep', 'sum'),
                                                 bed_time=(
    'start_date', 'min'),
    awake_time=(
    'end_date', 'max'),
    sleep_counts=(
    'creation_date', 'count'),
    rem_cycles=pd.NamedAgg(column='time_asleep', aggfunc=lambda x: (x // datetime.timedelta(minutes=90)).sum()))

# Time in Bed will be different to Apple's reported figure -
# as Apple uses the time you place your iPhone down as an additional
# datapoint, which of course, is incorrect if you try to maintain
# some device separation in the evenings.
# For now - we will just use Apple Watch data here
sleep_df['time_in_bed'] = sleep_df['awake_time'] - sleep_df['bed_time']
sleep_df['restless_time'] = sleep_df['time_in_bed'] - \
    sleep_df['total_time_asleep']

# Convert to seconds
sleep_df['total_time_asleep'] = sleep_df['total_time_asleep'].dt.total_seconds()
sleep_df['time_in_bed'] = sleep_df['time_in_bed'].dt.total_seconds()
sleep_df['restless_time'] = sleep_df['restless_time'].dt.total_seconds()

# Rename columns to include _seconds indicating the value is in seconds
sleep_df.rename(columns={'total_time_asleep': 'total_time_asleep_seconds',
                         'time_in_bed': 'time_in_bed_seconds', 'restless_time': 'restless_time_seconds'}, inplace=True)
