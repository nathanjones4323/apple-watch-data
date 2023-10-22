from loguru import logger
from metabase_api import Metabase_API


def create_collection(mb: Metabase_API, collection_name: str, parent_collection_name: str = "Root"):
    try:
        mb.create_collection(
            collection_name, parent_collection_name=parent_collection_name)
        logger.success(
            f"Created collection - '{collection_name}' under '{parent_collection_name}' collection")
    except:
        logger.error(f"Could not create collection - '{collection_name}'")
