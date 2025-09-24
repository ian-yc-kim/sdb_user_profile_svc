import logging
from typing import Generator
from sqlalchemy.orm import Session, sessionmaker

from sdb_user_profile_svc.database.connection import create_db_engine

# Create engine using the connection module
engine = create_db_engine()

# Create SessionLocal factory with proper configuration
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session.
    
    Yields:
        Session: SQLAlchemy database session instance.
        
    Note: This function is overridden in tests via dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logging.error(e, exc_info=True)
        raise
    finally:
        db.close()
