import os

from init.auth import auth
from init.collections import create_collection
from init.questions import (apple_calories, strong_exercises_by_volume,
                            strong_sets, strong_workout_duration_by_type,
                            strong_workouts)
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

    # Create Questions

    # Inside the Strong App Collection
    strong_workout_duration_by_type(mb)
    strong_sets(mb)
    strong_exercises_by_volume(mb)
    strong_workouts(mb)

    # Inside the Apple Health Collection
    apple_calories(mb)

    # Success message
    logger.success("Successfully initialized all metabase questions")
