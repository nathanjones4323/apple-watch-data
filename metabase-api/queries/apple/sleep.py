# Description: Metabase queries for the Apple Health Data

def add_apple_sleep_field_filters_to_sql(query: str) -> str:
    """Replaces generic `where 1=1` with Metabase field filters for the Apple Health Activity Data.

    Args:
        query (str): The SQL query to be modified.

    Returns:
        str: The modified SQL query with Strong App field filters.
    """

    return query.replace("where 1=1", "where 1=1\n    [[ and {{creation_date}} ]]")


def query_sleep_hours():
    query = """select 
    date_trunc({{date_granularity}}, creation_date) as time_period
    , sum(total_time_asleep_seconds) / 3600.0 as hours_of_sleep
    , avg(total_time_asleep_seconds) / 3600.0 as average_hours_of_sleep
    , sum(time_in_bed_seconds) / 3600.0 as hours_of_time_in_bed
    , avg(time_in_bed_seconds) / 3600.0 as average_hours_of_time_in_bed
    , avg(rem_cycles) as average_rem_cycles
from apple_health_sleep_raw
where 1=1
group by time_period
order by time_period desc
"""
    query = add_apple_sleep_field_filters_to_sql(query)
    return query.strip()


def query_rem_cycles():
    query = """select 
    date_trunc({{date_granularity}}, creation_date) as time_period
    , sum(rems) as rem_cycles
    , avg(rem_cycles) as average_rem_cycles
from apple_health_sleep_raw
where 1=1
group by time_period
order by time_period desc
"""
    query = add_apple_sleep_field_filters_to_sql(query)
    return query.strip()
