import re

import pandas as pd


def camel_to_snake(camel_case):
  # Check for an uppercase letter in the string
    if re.search(r'[A-Z]', camel_case):
        # Replace all uppercase letters with an underscore and lowercase letter
        snake_case = re.sub(r'([A-Z])', lambda x: '_' + x.group(0).lower(), camel_case)
        # Remove the first underscore only if it is the first character in the string
        snake_case = re.sub(r'^_', '', snake_case)
    else:
        snake_case = camel_case.lower()
    return snake_case


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Tidies up data to prepare for loading into Postgres

    Args:
        df (pd.DataFrame): A pandas DataFrame

    Returns:
        pd.DataFrame: A modified pandas DataFrame with all column names converted to snake_case
    """
    df.columns = [camel_to_snake(col) for col in df.columns]
    return df
