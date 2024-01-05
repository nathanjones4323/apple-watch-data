def query_calories_burned():
    query = """
        select 
            date_trunc('day', end_date) as time_period
            , sum(active_energy_burned) as active_calories_burned
            , sum(basal_energy_burned) as resting_calories_burned
            , sum(active_energy_burned) + sum(basal_energy_burned) as total_calories_burned
        from apple_health_raw
        where 1=1
        group by time_period
        order by time_period desc
        """
    return query
