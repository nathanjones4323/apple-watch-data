import os

from init.auth import auth
from init.collections import create_collection
from init.questions.apple import apple_calories, apple_rem_cycles, apple_sleep_hours
from init.questions.five_by_five import five_by_five_progressive_overload
from init.questions.strong import (
    strong_count_by_workout_type,
    strong_sets_by_workout_type,
    strong_volume_by_exercise_type,
    strong_workout_duration_by_type,
)
from loguru import logger

# Load environment variables from the .env file
path = os.path.join(os.path.dirname(__file__), '..', 'init', '.env')

# Authenticate API Session
mb = auth()
# If mb is None then the Metabase questions have already been initialized
if mb:
    # Create Collection for Strong App
    create_collection(mb, collection_name="Strong App",
                      parent_collection_name="Root")

    # Create Collection for Apple Health
    create_collection(mb, collection_name="Apple Health",
                      parent_collection_name="Root")
    
    # Create Collection for 5x5 program
    create_collection(mb, collection_name="5x5 Program",
                      parent_collection_name="Root")

    # Create Questions

    # Inside the Strong App Collection
    strong_workout_duration_by_type(mb)
    strong_sets_by_workout_type(mb)
    strong_volume_by_exercise_type(mb)
    strong_count_by_workout_type(mb)

    # Inside the Apple Health Collection
    apple_calories(mb)
    apple_sleep_hours(mb)
    apple_rem_cycles(mb)

    # Inside the 5x5 Program Collection
    five_by_five_progressive_overload(mb)

    # Success message
    logger.success("Successfully initialized all metabase questions")
