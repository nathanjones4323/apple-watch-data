import pandas as pd


# Function to convert column names to snake_case
def snake_case(column_name):
    words = column_name.split()
    return '_'.join(words).lower()


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Tidies up data to prepare for loading into Postgres

    Args:
        df (pd.DataFrame): A pandas DataFrame

    Returns:
        pd.DataFrame: A modified pandas DataFrame with all column names converted to snake_case
    """
    df.columns = [snake_case(col) for col in df.columns]
    return df
