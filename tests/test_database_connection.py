import pytest
from sqlalchemy.pool import QueuePool, StaticPool, NullPool
from sqlalchemy import Engine

from sdb_user_profile_svc.database.connection import create_db_engine


class TestDatabaseConnection:
    """Test cases for database connection module."""
    
    def test_postgresql_engine_pooling_configuration(self, monkeypatch):
        """Test that PostgreSQL engine is configured with expected pooling parameters."""
        # Mock DATABASE_URL to use PostgreSQL
        postgresql_url = "postgresql+psycopg2://user:pass@localhost:5432/testdb"
        monkeypatch.setattr("sdb_user_profile_svc.config.DATABASE_URL", postgresql_url)
        
        # Create engine using mocked config
        engine = create_db_engine()
        
        # Verify engine properties
        assert isinstance(engine, Engine)
        assert engine.dialect.name == "postgresql"
        assert isinstance(engine.pool, QueuePool)
        assert engine.pool.size() == 10
        assert engine.pool._max_overflow == 20
        assert engine.pool._recycle == 3600
        
    def test_sqlite_inmemory_engine_configuration(self, monkeypatch):
        """Test that SQLite in-memory engine is configured without queue-pooling and with threading compatibility."""
        # Mock DATABASE_URL to use SQLite in-memory
        sqlite_url = "sqlite:///:memory:"
        monkeypatch.setattr("sdb_user_profile_svc.config.DATABASE_URL", sqlite_url)
        
        # Create engine using mocked config
        engine = create_db_engine()
        
        # Verify engine properties
        assert isinstance(engine, Engine)
        assert engine.dialect.name == "sqlite"
        assert isinstance(engine.pool, StaticPool)
        # Verify it's not QueuePool (different pooling strategy)
        assert not isinstance(engine.pool, QueuePool)
        
    def test_sqlite_file_engine_configuration(self):
        """Test that file-based SQLite engine uses NullPool."""
        # Test with file-based SQLite URL
        sqlite_file_url = "sqlite:///./test.db"
        engine = create_db_engine(sqlite_file_url)
        
        # Verify engine properties
        assert isinstance(engine, Engine)
        assert engine.dialect.name == "sqlite"
        assert isinstance(engine.pool, NullPool)
        # Verify it's not QueuePool (no pooling)
        assert not isinstance(engine.pool, QueuePool)
        
    def test_robust_engine_creation_multiple_urls(self):
        """Test that engine creation works robustly with different valid database URLs."""
        # Test SQLite file-based URL
        engine1 = create_db_engine("sqlite:///./test.db")
        assert isinstance(engine1, Engine)
        assert engine1.dialect.name == "sqlite"
        
        # Test PostgreSQL URL
        engine2 = create_db_engine("postgresql+psycopg2://user:pass@localhost:5432/anotherdb")
        assert isinstance(engine2, Engine)
        assert engine2.dialect.name == "postgresql"
        
        # Test SQLite in-memory URL
        engine3 = create_db_engine("sqlite:///:memory:")
        assert isinstance(engine3, Engine)
        assert engine3.dialect.name == "sqlite"
        
        # No exceptions should be raised during engine creation
        # All engines should be properly configured instances
        
    def test_postgresql_engine_with_explicit_url(self):
        """Test PostgreSQL engine creation with explicitly provided URL."""
        postgresql_url = "postgresql+psycopg2://testuser:testpass@localhost:5432/testdb"
        engine = create_db_engine(postgresql_url)
        
        # Verify engine properties
        assert isinstance(engine, Engine)
        assert engine.dialect.name == "postgresql"
        assert isinstance(engine.pool, QueuePool)
        assert engine.pool.size() == 10
        assert engine.pool._max_overflow == 20
        assert engine.pool._recycle == 3600
