import re

import pandas as pd


def camel_to_snake(camel_case):
  # Check for an uppercase letter in the string
    if re.search(r'[A-Z]', camel_case):
        # Replace all uppercase letters with an underscore and lowercase letter
        snake_case = re.sub(r'([A-Z])', lambda x: '_' + x.group(0).lower(), camel_case)
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
    
    # Make endDate a column instead of the index
    pivot_df.reset_index(inplace=True)
    
    # rename columns
    pivot_df.columns = [camel_to_snake(col) for col in pivot_df.columns]
    
    return pivot_df


def transform_strong_data(data: pd.DataFrame) -> pd.DataFrame:
    """Tidies up data to prepare for loading into Postgres

    Args:
        df (pd.DataFrame): A pandas DataFrame

    Returns:
        pd.DataFrame: A modified pandas DataFrame with all column names converted to snake_case
    """
    
    # proper type to dates
    for col in ['Date']:
        data[col] = pd.to_datetime(data[col])
    
    # Convert Duration to seconds
    data['Duration'] = pd.to_timedelta(data['Duration']).dt.total_seconds().astype(int)

    # rename columns
    data.columns = [camel_to_snake(col) for col in data.columns]
    data.rename(columns={'date': 'created_at'}, inplace=True)

    # Add a column for workout_id. workout_id is the concatenation of the `date` and `workout_name` columns
    data['workout_id'] = data['created_at'].astype(str) + "_" + data['workout_name'].astype(str)

    return data