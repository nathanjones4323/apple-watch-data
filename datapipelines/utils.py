import os

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Connection


def init_db_connection() -> Connection:
    """Creates a SQLAlchemy connection object used to interact a postgres DB

    Returns:
        `sqlalchemy.engine.base.Connection`: SQLAlchemy connection object
    """
    engine = create_engine(
        url=f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}")
    conn = engine.connect()
    return conn