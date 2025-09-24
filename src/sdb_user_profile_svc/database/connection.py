import logging
from typing import Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.pool import QueuePool, NullPool, StaticPool


def create_db_engine(url: Optional[str] = None) -> Engine:
    """
    Create and configure a SQLAlchemy engine based on the database URL.
    
    Args:
        url: Optional database URL. If None, uses DATABASE_URL from config.
        
    Returns:
        Configured SQLAlchemy Engine instance.
        
    Raises:
        Exception: Re-raises any exception that occurs during engine creation.
    """
    try:
        # Import DATABASE_URL inside function for testability
        if url is None:
            from sdb_user_profile_svc.config import DATABASE_URL
            db_url = DATABASE_URL
        else:
            db_url = url
        
        # Parse the database URL to determine dialect
        parsed_url = make_url(db_url)
        dialect = parsed_url.get_backend_name()
        
        if dialect == "postgresql":
            # PostgreSQL configuration with connection pooling
            engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
                pool_pre_ping=True
            )
        elif dialect == "sqlite":
            # SQLite configuration without connection pooling
            if parsed_url.database == ":memory:":
                # In-memory SQLite with StaticPool for multi-threading compatibility
                engine = create_engine(
                    db_url,
                    poolclass=StaticPool,
                    connect_args={"check_same_thread": False}
                )
            else:
                # File-based SQLite with NullPool to avoid pooling
                engine = create_engine(
                    db_url,
                    poolclass=NullPool,
                    connect_args={"check_same_thread": False}
                )
        else:
            # Fallback for other dialects without specific pooling configuration
            engine = create_engine(db_url)
            
        return engine
        
    except Exception as e:
        logging.error(e, exc_info=True)
        raise
