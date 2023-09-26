import os

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Connection


def init_db_connection() -> Connection:
    """Creates a SQLAlchemy connection object used to interact with a PostgreSQL DB

    Returns:
        `sqlalchemy.engine.base.Connection`: SQLAlchemy connection object
    """
    # Have to use 'db' as the host name because that is the name of the service in the docker-compose.yml file
    url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    try:
        engine = create_engine(url)
        conn = engine.connect()
        return conn
    except Exception as e:
        logger.error(f"Could not connect to DB: {str(e)}")

def init_metabase_db_connection() -> Connection:
    """Creates a SQLAlchemy connection object used to interact a postgres DB

    Returns:
        `sqlalchemy.engine.base.Connection`: SQLAlchemy connection object
    """
    engine = create_engine(
        url=f"postgresql://{os.getenv('MB_DB_USER')}:{os.getenv('MB_DB_PASS')}@{os.getenv('MB_DB_HOST')}:{os.getenv('MB_DB_PORT')}/{os.getenv('MB_DB_DBNAME')}")
    conn = engine.connect()
    return conn