# Description: Metabase queries for the Strong App Data

def add_strong_field_filters_to_sql(query: str) -> str:
    """Replaces generic `where 1=1` with Metabase field filters for the Strong App.

    Args:
        query (str): The SQL query to be modified.

    Returns:
        str: The modified SQL query with Strong App field filters.
    """

    return query.replace("where 1=1", "where 1=1\n    [[ and {{created_at}} ]]\n    [[ and {{workout_name}} ]]\n    [[ and {{exercise_name}} ]]")
    # return query.replace("where 1=1", "where 1=1\n    [[ and {{created_at}} ]]\n    [[ and {{workout_name}} ]]\n    [[ and {{exercise_name}} ]]\n    [[ and reps >= {{min_reps}} ]]\n    [[ and reps <= {{max_reps}} ]]\n    [[ and weight >= {{min_weight}} ]]\n    [[ and weight <= {{max_weight}} ]]\n    [[ and set_order >= {{min_set_order}} ]]\n    [[ and set_order <= {{max_set_order}} ]]")


def query_duration_by_workout_type():
    query = """select
    workout_name
    , count(distinct workout_id) as number_of_workouts
    , avg(duration) / 60.0 as average_workout_length_minutes
    , percentile_cont(0.5) within group (order by duration) / 60.0 as median_workout_length_minutes
from strong_app_raw
where 1=1
group by workout_name
order by average_workout_length_minutes desc
"""
    query = add_strong_field_filters_to_sql(query)
    return query.strip()


def query_sets_by_workout_type():
    query = """select
    date_trunc({{date_granularity}}, created_at) as time_period
    , workout_name
    , count(*) as number_of_sets
from strong_app_raw
where 1=1
group by time_period, workout_name
order by time_period, number_of_sets desc
"""
    query = add_strong_field_filters_to_sql(query)
    return query.strip()


def query_sets_by_exercise_type():
    query = """select
    date_trunc({{date_granularity}}, created_at) as time_period
    , exercise_name
    , count(*) as number_of_sets
from strong_app_raw
where 1=1
group by time_period, exercise_name
order by time_period desc, number_of_sets desc
"""
    query = add_strong_field_filters_to_sql(query)
    return query.strip()


def query_count_by_workout_type():
    query = """select
    date_trunc({{date_granularity}}, created_at) as time_period
    , workout_name
    , count(distinct workout_id) as number_of_workout_days
from strong_app_raw
where 1=1
group by time_period, workout_name
order by time_period desc, number_of_workout_days desc
"""
    query = add_strong_field_filters_to_sql(query)
    return query.strip()
