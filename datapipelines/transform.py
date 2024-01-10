import datetime
import re

import pandas as pd
from loguru import logger


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


def transform_apple_health_data(data: pd.DataFrame) -> pd.DataFrame:
    """Tidies up data to prepare for loading into Postgres

    Args:
        df (pd.DataFrame): A pandas DataFrame

    Returns:
        pd.DataFrame: A modified pandas DataFrame with all column names converted to snake_case
    """

    try:
        # proper type to dates
        date_cols = ['creationDate', 'startDate', 'endDate']
        data[date_cols] = data[date_cols].apply(pd.to_datetime)

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

        # pivot and resample. Might want to use index=['endDate', 'creationDate', 'startDate'] instead
        pivot_df = data.pivot_table(
            index=['endDate', 'creationDate', 'startDate', 'sourceName'], columns='type', values='value')

        # Make endDate a column instead of the index
        pivot_df.reset_index(inplace=True)

        # rename columns
        pivot_df.columns = [camel_to_snake(col) for col in pivot_df.columns]

        logger.success("Transformed Apple Health data")
        logger.debug(f"Transformed Apple Health dataframe: {pivot_df}")

        return pivot_df
    except Exception as e:
        logger.error(f"Could not transform Apple Health data: {e}")
        return data


def split_apple_health_data(data: pd.DataFrame) -> pd.DataFrame:
    """Splits Apple Health data into two separate dataframes: one for sleep data and one for everything else

    Args:
        data (pd.DataFrame): A pandas DataFrame returned from `transform_apple_health_data`

    Returns:
        pd.DataFrame, pd.DataFrame: Two pandas DataFrames: one for sleep data and one all other data
    """

    try:
        # Split data into two dataframes: one for workouts and one for everything else
        sleep_df = data[(data["sleep_analysis"].notnull()) & (
            data["source_name"].str.contains("Watch", regex=False))]
        activity_df = data[(data["sleep_analysis"].isnull())]

        # Feature engineering for sleep_df
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

        # Convert to seconds
        sleep_df['total_time_asleep'] = sleep_df['total_time_asleep'].dt.total_seconds()
        sleep_df['time_in_bed'] = sleep_df['time_in_bed'].dt.total_seconds()

        # Compute `restless_time`
        sleep_df['restless_time'] = sleep_df['time_in_bed'] - \
            sleep_df['total_time_asleep']

        # Rename columns to include _seconds indicating the value is in seconds
        sleep_df.rename(columns={'total_time_asleep': 'total_time_asleep_seconds',
                                 'time_in_bed': 'time_in_bed_seconds', 'restless_time': 'restless_time_seconds'}, inplace=True)

        # Make creation_date a column instead of the index
        sleep_df.reset_index(inplace=True)

        logger.success("Split Apple Health data")
        logger.debug(f"Sleep dataframe shape: {sleep_df.shape}")
        logger.debug(f"Sleep dataframe head: {sleep_df.head()}")
        logger.debug(f"Sleep dataframe dtypes: {sleep_df.dtypes}")
        logger.debug(f"Activity dataframe head: {activity_df}")
        logger.debug(f"Activity dataframe shape: {activity_df.shape}")
        logger.debug(f"Activity dataframe dtypes: {activity_df.dtypes}")

        return sleep_df, activity_df
    except Exception as e:
        logger.error(
            f"Could not split Apple Health data into Sleep and Activity Data: {e}")
        return None, None


def transform_strong_data(data: pd.DataFrame) -> pd.DataFrame:
    """Tidies up data to prepare for loading into Postgres

    Args:
        df (pd.DataFrame): A pandas DataFrame

    Returns:
        pd.DataFrame: A modified pandas DataFrame with all column names converted to snake_case
    """

    try:
        # proper type to dates
        for col in ['Date']:
            data[col] = pd.to_datetime(data[col])

        # Convert Duration to seconds
        data['Duration'] = pd.to_timedelta(
            data['Duration']).dt.total_seconds().astype(int)

        # rename columns
        data.columns = [camel_to_snake(col) for col in data.columns]
        data.rename(columns={'date': 'created_at'}, inplace=True)

        # Add a column for workout_id. workout_id is the concatenation of the `date` and `workout_name` columns
        data['workout_id'] = data['created_at'].astype(
            str) + "_" + data['workout_name'].astype(str)

        logger.success("Transformed Strong data")
        logger.debug(f"Strong dataframe shape: {data.shape}")
        logger.debug(f"Strong dataframe head: {data.head()}")
        logger.debug(f"Strong dataframe dtypes: {data.dtypes}")

        return data
    except Exception as e:
        logger.error(f"Could not transform Strong data: {e}")
        return data
