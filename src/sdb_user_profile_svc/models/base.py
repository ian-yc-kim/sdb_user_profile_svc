from sqlalchemy import Column, PrimaryKeyConstraint, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from sdb_user_profile_svc.database.connection import create_db_engine

Base = declarative_base()

# Create engine using the new connection module
engine = create_db_engine()


def get_db() -> Session:
    """Get database session.
    
    Note: This function is overridden in tests via dependency injection.
    """
    session = scoped_session(sessionmaker(bind=engine))
    try:
        yield session
    finally:
        session.close()
