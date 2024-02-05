# Description: Metabase queries for the Strong App Data specific to progressive overload and 5x5 program
from queries.strong.lifting import add_strong_field_filters_to_sql


def query_progressive_overload():
    query = """with reps_and_sets as (
  select
    date_trunc('day', created_at) as day_lift_performed,
    exercise_name,
    created_at,  -- include created_at in the group by clause
    min(weight) as lowest_working_set_weight_lbs,
    sum(reps) as number_of_reps,
    count(*) as number_of_sets,
    row_number() over (partition by exercise_name order by created_at desc) as row_num
  from strong_app_raw
  where 1=1
  group by day_lift_performed, exercise_name, created_at
)
, progressive_overload_data as (
  select 
    *,
    case when number_of_reps >= 25 and number_of_sets >= 5 then true else false end as increase_weight,
    case when exercise_name = 'Trap Bar Deadlift' then 10 else 5 end as increase_weight_amount
  from reps_and_sets
  where row_num = 1 -- select only the most recent day per exercise_name
)
select 
	day_lift_performed as last_lift_performed_at
	, exercise_name
	, number_of_sets
	, number_of_reps
	, lowest_working_set_weight_lbs as last_working_set_weight
	, increase_weight
	, case 
		when increase_weight is true then lowest_working_set_weight_lbs + increase_weight_amount
		else lowest_working_set_weight_lbs
	end as new_working_set_weight
from progressive_overload_data
order by day_lift_performed desc, exercise_name
"""
    query = add_strong_field_filters_to_sql(query)
    return query.strip()