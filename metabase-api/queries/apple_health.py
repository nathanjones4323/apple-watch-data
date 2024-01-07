# Description: Metabase queries for the Apple Health Data

def add_apple_field_filters_to_sql(query: str) -> str:
    """Replaces generic `where 1=1` with Metabase field filters for the Strong App.

    Args:
        query (str): The SQL query to be modified.

    Returns:
        str: The modified SQL query with Strong App field filters.
    """

    return query.replace("where 1=1", "where 1=1\n    [[ and {{end_date}} ]]")


def query_calories_burned():
    query = """select 
    date_trunc({{date_granularity}}, end_date) as time_period
    , sum(active_energy_burned) as active_calories_burned
    , sum(basal_energy_burned) as resting_calories_burned
    , sum(active_energy_burned) + sum(basal_energy_burned) as total_calories_burned
from apple_health_raw
where 1=1
group by time_period
order by time_period desc
"""
    query = add_apple_field_filters_to_sql(query)
    return query.strip()
