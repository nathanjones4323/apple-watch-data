from init.auth import auth
from init.collections import create_collection
from init.questions import (strong_sets, strong_top_exercises_by_volume,
                            strong_top_workouts,
                            strong_workout_duration_by_type)

# Authenticate API Session
mb = auth()

# Create Collection for Strong App
create_collection(mb, collection_name="Strong App",
                  parent_collection_name="Root")

# Create Questions

# Inside the Strong App Collection
strong_workout_duration_by_type(mb)
strong_sets(mb)
strong_top_exercises_by_volume(mb)
strong_top_workouts(mb)
