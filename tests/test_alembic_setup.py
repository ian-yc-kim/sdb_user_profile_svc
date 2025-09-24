import os
import logging
import tempfile
import shutil
from pathlib import Path
from typing import Generator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Column, Integer, String, inspect, text
from sqlalchemy.engine import Engine

from sdb_user_profile_svc.database.connection import create_db_engine
from sdb_user_profile_svc.models.base import Base


class TestAlembicSetup:
    """Comprehensive integration tests for Alembic setup and functionality."""
    
    def test_alembic_config_load_and_connect(self, tmp_path):
        """Test Alembic configuration loading and database connection.
        
        This test verifies that:
        1. Alembic configuration can be loaded from alembic.ini
        2. Database URL can be configured programmatically
        3. Database engine creation works with the configured URL
        4. Connection can be established successfully
        """
        try:
            # Load Alembic configuration from the existing alembic.ini
            config = Config("src/sdb_user_profile_svc/alembic/alembic.ini")
            assert config is not None, "Failed to load Alembic configuration"
            
            # Configure database URL for in-memory SQLite
            test_db_url = "sqlite:///:memory:"
            os.environ["DATABASE_URL"] = test_db_url
            config.set_main_option("sqlalchemy.url", test_db_url)
            
            # Test engine creation using create_db_engine function
            engine = create_db_engine(test_db_url)
            assert isinstance(engine, Engine), "create_db_engine should return a SQLAlchemy Engine"
            assert engine.dialect.name == "sqlite", "Engine should use SQLite dialect"
            
            # Test database connection
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1 as test_value")).fetchone()
                assert result[0] == 1, "Database connection test query should return 1"
                
            logging.info("Alembic configuration loaded and database connection established successfully")
            
        except Exception as e:
            logging.error(e, exc_info=True)
            raise
        finally:
            # Clean up environment variable
            if "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]
    
    def test_alembic_autogenerate_detection(self, tmp_path):
        """Test Alembic autogenerate functionality with model detection.
        
        This test verifies that:
        1. Alembic can detect new SQLAlchemy models
        2. Migration scripts are generated with correct DDL
        3. Generated migration files contain expected table creation commands
        """
        # Define a temporary model for autogenerate testing
        class DummyAutoModel(Base):
            __tablename__ = 'dummy_auto_table'
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            name = Column(String(100), nullable=False)
            description = Column(String(255), nullable=True)
        
        try:
            # Setup temporary directories and database
            temp_versions_dir = tmp_path / "versions"
            temp_versions_dir.mkdir()
            test_db_file = tmp_path / "autogen_test.db"
            test_db_url = f"sqlite:///{test_db_file}"
            
            # Configure Alembic
            config = Config("src/sdb_user_profile_svc/alembic/alembic.ini")
            config.set_main_option("sqlalchemy.url", test_db_url)
            config.set_main_option("version_locations", str(temp_versions_dir))
            
            # Set environment variable for env.py
            os.environ["DATABASE_URL"] = test_db_url
            
            # Generate migration with autogenerate
            command.revision(
                config, 
                autogenerate=True, 
                message="detect_dummy_auto_model"
            )
            
            # Verify migration script was generated
            migration_files = list(temp_versions_dir.glob("*.py"))
            assert len(migration_files) == 1, f"Expected 1 migration file, found {len(migration_files)}"
            
            migration_file = migration_files[0]
            with open(migration_file, 'r') as f:
                migration_content = f.read()
            
            # Verify migration contains expected DDL for the dummy model
            assert "dummy_auto_table" in migration_content, "Migration should contain dummy table name"
            assert "op.create_table" in migration_content, "Migration should contain create_table operation"
            assert "sa.Integer()" in migration_content, "Migration should contain Integer column type"
            assert "sa.String" in migration_content, "Migration should contain String column type"
            
            logging.info(f"Autogenerate successfully detected model and created migration: {migration_file.name}")
            
        except Exception as e:
            logging.error(e, exc_info=True)
            raise
        finally:
            # Clean up: remove the dummy model from Base.metadata
            if hasattr(DummyAutoModel, '__table__') and DummyAutoModel.__table__ in Base.metadata.tables.values():
                Base.metadata.remove(DummyAutoModel.__table__)
            
            # Clean up environment variable
            if "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]
    
    def test_alembic_upgrade_and_downgrade(self, tmp_path):
        """Test Alembic upgrade and downgrade operations.
        
        This test verifies that:
        1. Migration scripts can be generated programmatically
        2. Upgrade operation successfully applies migrations
        3. Database schema changes are reflected after upgrade
        4. Downgrade operation successfully reverts migrations
        5. Database schema is restored to original state after downgrade
        """
        # Define a temporary model for upgrade/downgrade testing
        class DummyMigrateModel(Base):
            __tablename__ = 'dummy_migrate_table'
            
            id = Column(Integer, primary_key=True, autoincrement=True)
            title = Column(String(150), nullable=False)
            status = Column(String(50), nullable=True, default="active")
        
        try:
            # Setup temporary directories and database
            temp_versions_dir = tmp_path / "versions"
            temp_versions_dir.mkdir()
            test_db_file = tmp_path / "migrate_test.db"
            test_db_url = f"sqlite:///{test_db_file}"
            
            # Configure Alembic
            config = Config("src/sdb_user_profile_svc/alembic/alembic.ini")
            config.set_main_option("sqlalchemy.url", test_db_url)
            config.set_main_option("version_locations", str(temp_versions_dir))
            
            # Set environment variable for env.py
            os.environ["DATABASE_URL"] = test_db_url
            
            # Generate migration for the dummy model
            command.revision(
                config,
                autogenerate=True,
                message="create_dummy_migrate_table"
            )
            
            # Verify migration file was created
            migration_files = list(temp_versions_dir.glob("*.py"))
            assert len(migration_files) == 1, "Should have exactly one migration file"
            
            # Create engine for database inspection
            engine = create_db_engine(test_db_url)
            inspector = inspect(engine)
            
            # Verify table doesn't exist before upgrade
            tables_before = inspector.get_table_names()
            assert "dummy_migrate_table" not in tables_before, "Table should not exist before upgrade"
            
            # Execute upgrade to head
            command.upgrade(config, "head")
            
            # Verify table exists after upgrade
            inspector = inspect(engine)  # Refresh inspector
            tables_after_upgrade = inspector.get_table_names()
            assert "dummy_migrate_table" in tables_after_upgrade, "Table should exist after upgrade"
            
            # Verify table structure
            columns = inspector.get_columns("dummy_migrate_table")
            column_names = [col['name'] for col in columns]
            assert "id" in column_names, "Table should have id column"
            assert "title" in column_names, "Table should have title column"
            assert "status" in column_names, "Table should have status column"
            
            logging.info("Upgrade operation successful - table created with expected structure")
            
            # Execute downgrade to base
            command.downgrade(config, "base")
            
            # Verify table no longer exists after downgrade
            inspector = inspect(engine)  # Refresh inspector
            tables_after_downgrade = inspector.get_table_names()
            assert "dummy_migrate_table" not in tables_after_downgrade, "Table should not exist after downgrade"
            
            logging.info("Downgrade operation successful - table removed")
            
        except Exception as e:
            logging.error(e, exc_info=True)
            raise
        finally:
            # Clean up: remove the dummy model from Base.metadata
            if hasattr(DummyMigrateModel, '__table__') and DummyMigrateModel.__table__ in Base.metadata.tables.values():
                Base.metadata.remove(DummyMigrateModel.__table__)
            
            # Clean up environment variable
            if "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]
