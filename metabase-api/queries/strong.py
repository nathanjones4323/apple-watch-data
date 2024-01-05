def query_duration_by_workout_type():
    query = """
        select 
            workout_name
            , count(distinct workout_id) as number_of_workouts
            , avg(duration) / 60.0 as average_workout_length_minutes
            , percentile_cont(0.5) within group (order by duration) / 60.0 as median_workout_length_minutes
        from strong_app_raw
        where 1=1
            [[ and {{created_at}} ]]
        group by workout_name
        order by average_workout_length_minutes desc
        """
    return query.strip()


def query_sets_by_workout_type():
    query = """
        select 
            date_trunc({{date_granularity}}, created_at) as time_period
            , workout_name
            , count(*) as number_of_sets
        from strong_app_raw
        where 1=1
            [[ and {{created_at}} ]]
        group by time_period, workout_name
        order by time_period, number_of_sets desc
        """
    return query.strip()


def query_volume_by_exercise_type():
    query = """
        select 
            date_trunc({{date_granularity}}, created_at) as time_period
            , workout_name
            , exercise_name
            , count(*) as number_of_sets
        from strong_app_raw
        where 1=1
            [[ and {{created_at}} ]]
        group by time_period, workout_name, exercise_name
        order by time_period desc, number_of_sets desc
        """
    return query.strip()


def query_count_by_workout_type():
    query = """
        select 
            date_trunc({{date_granularity}}, created_at) as time_period
            , workout_name
            , count(distinct workout_id) as number_of_workout_days
        from strong_app_raw
        where 1=1
            [[ and {{created_at}} ]]
        group by time_period, workout_name
        order by time_period desc, number_of_workout_days desc
        """
    return query.strip()
