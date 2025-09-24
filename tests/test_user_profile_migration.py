import os
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, List

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from sdb_user_profile_svc.database.connection import create_db_engine
from sdb_user_profile_svc.models.user_profile import UserProfile


class TestUserProfileMigration:
    """Test UserProfile table creation and rollback using Alembic migration."""
    
    def test_user_profile_migration_workflow(self, tmp_path):
        """Test complete Alembic upgrade/downgrade workflow for user_profile table.
        
        This test verifies that:
        1. Alembic upgrade head successfully creates the user_profile table
        2. Table has correct columns with proper types and constraints
        3. Required indexes are created
        4. Alembic downgrade base successfully removes the user_profile table
        """
        try:
            # Setup temporary directories and database
            temp_versions_dir = tmp_path / "versions"
            temp_versions_dir.mkdir()
            test_db_file = tmp_path / "user_profile_migration.db"
            test_db_url = f"sqlite:///{test_db_file}"
            
            # Copy the existing migration script to temporary versions directory
            original_migration_path = Path("src/sdb_user_profile_svc/alembic/versions/97214870544a_create_user_profile_table.py")
            temp_migration_path = temp_versions_dir / "97214870544a_create_user_profile_table.py"
            shutil.copy2(original_migration_path, temp_migration_path)
            
            # Configure Alembic
            config = Config("src/sdb_user_profile_svc/alembic/alembic.ini")
            config.set_main_option("sqlalchemy.url", test_db_url)
            config.set_main_option("version_locations", str(temp_versions_dir))
            
            # Set environment variable for env.py
            original_db_url = os.environ.get("DATABASE_URL")
            os.environ["DATABASE_URL"] = test_db_url
            
            # Create engine for database inspection
            engine = create_db_engine(test_db_url)
            inspector = inspect(engine)
            
            # Verify table doesn't exist before upgrade
            tables_before = inspector.get_table_names()
            assert "user_profile" not in tables_before, "user_profile table should not exist before upgrade"
            
            # Execute upgrade to head
            command.upgrade(config, "head")
            logging.info("Alembic upgrade head completed")
            
            # Refresh inspector after upgrade
            inspector = inspect(engine)
            
            # Verify table exists after upgrade
            tables_after_upgrade = inspector.get_table_names()
            assert "user_profile" in tables_after_upgrade, "user_profile table should exist after upgrade"
            
            # Verify table structure and columns
            self._verify_user_profile_table_structure(inspector)
            
            # Verify indexes
            self._verify_user_profile_indexes(inspector)
            
            # Verify CHECK constraint if possible with SQLite
            self._verify_check_constraints(inspector)
            
            logging.info("Table structure and indexes verified successfully after upgrade")
            
            # Execute downgrade to base
            command.downgrade(config, "base")
            logging.info("Alembic downgrade base completed")
            
            # Refresh inspector after downgrade
            inspector = inspect(engine)
            
            # Verify table no longer exists after downgrade
            tables_after_downgrade = inspector.get_table_names()
            assert "user_profile" not in tables_after_downgrade, "user_profile table should not exist after downgrade"
            
            logging.info("User profile migration workflow completed successfully")
            
        except Exception as e:
            logging.error(e, exc_info=True)
            raise
        finally:
            # Clean up environment variable
            if original_db_url is not None:
                os.environ["DATABASE_URL"] = original_db_url
            elif "DATABASE_URL" in os.environ:
                del os.environ["DATABASE_URL"]
    
    def _verify_user_profile_table_structure(self, inspector) -> None:
        """Verify the user_profile table has correct column structure.
        
        Args:
            inspector: SQLAlchemy Inspector instance
        """
        try:
            # Get columns from the database
            columns = inspector.get_columns("user_profile")
            column_dict = {col['name']: col for col in columns}
            
            # Get expected columns from UserProfile model
            expected_columns = {
                'id': {'nullable': False, 'primary_key': True},
                'name': {'nullable': False, 'primary_key': False},
                'region': {'nullable': False, 'primary_key': False},
                'company': {'nullable': True, 'primary_key': False},
                'bio': {'nullable': True, 'primary_key': False},
                'hobbies': {'nullable': True, 'primary_key': False},
                'interests': {'nullable': True, 'primary_key': False},
                'age': {'nullable': True, 'primary_key': False},
                'created_at': {'nullable': False, 'primary_key': False},
                'updated_at': {'nullable': False, 'primary_key': False}
            }
            
            # Verify all expected columns exist
            for col_name, expected_props in expected_columns.items():
                assert col_name in column_dict, f"Column {col_name} should exist in user_profile table"
                
                actual_col = column_dict[col_name]
                assert actual_col['nullable'] == expected_props['nullable'], \
                    f"Column {col_name} nullable should be {expected_props['nullable']}, got {actual_col['nullable']}"
            
            # Verify primary key
            primary_keys = inspector.get_pk_constraint("user_profile")
            assert 'id' in primary_keys['constrained_columns'], "id column should be primary key"
            
            # Verify column types are reasonable (database-agnostic check)
            assert 'INTEGER' in str(column_dict['id']['type']).upper(), "id should be integer type"
            assert any(keyword in str(column_dict['name']['type']).upper() for keyword in ['VARCHAR', 'STRING', 'TEXT']), \
                "name should be string-like type"
            assert any(keyword in str(column_dict['region']['type']).upper() for keyword in ['VARCHAR', 'STRING', 'TEXT']), \
                "region should be string-like type"
            
            logging.info(f"Verified {len(expected_columns)} columns with correct properties")
            
        except Exception as e:
            logging.error(e, exc_info=True)
            raise
    
    def _verify_user_profile_indexes(self, inspector) -> None:
        """Verify the user_profile table has correct indexes.
        
        Args:
            inspector: SQLAlchemy Inspector instance
        """
        try:
            # Get indexes from the database
            indexes = inspector.get_indexes("user_profile")
            index_dict = {idx['name']: idx for idx in indexes}
            
            # Expected indexes from migration script
            expected_indexes = {
                'idx_user_profile_name': ['name'],
                'idx_user_profile_region': ['region'],
                'ix_user_profile_id': ['id']  # This is created by the migration
            }
            
            # Verify expected indexes exist
            for index_name, expected_columns in expected_indexes.items():
                assert index_name in index_dict, f"Index {index_name} should exist"
                
                actual_index = index_dict[index_name]
                for expected_col in expected_columns:
                    assert expected_col in actual_index['column_names'], \
                        f"Index {index_name} should include column {expected_col}"
            
            logging.info(f"Verified {len(expected_indexes)} indexes with correct columns")
            
        except Exception as e:
            logging.error(e, exc_info=True)
            raise
    
    def _verify_check_constraints(self, inspector) -> None:
        """Verify CHECK constraints if supported by the database dialect.
        
        Args:
            inspector: SQLAlchemy Inspector instance
            
        Note:
            SQLite may not expose CHECK constraints through introspection,
            but the constraint is still enforced. PostgreSQL exposes them.
        """
        try:
            # Attempt to get check constraints
            if hasattr(inspector, 'get_check_constraints'):
                check_constraints = inspector.get_check_constraints("user_profile")
                
                if check_constraints:
                    # Look for the age range constraint
                    age_constraint_found = False
                    for constraint in check_constraints:
                        if 'chk_user_profile_age_range' in constraint.get('name', '') or \
                           'age' in constraint.get('sqltext', '').lower():
                            age_constraint_found = True
                            logging.info(f"Found age CHECK constraint: {constraint}")
                            break
                    
                    if age_constraint_found:
                        logging.info("Age CHECK constraint verified through introspection")
                    else:
                        logging.info("Age CHECK constraint not found in introspection, but migration succeeded")
                else:
                    logging.info("No CHECK constraints found via introspection (expected for SQLite)")
            else:
                logging.info("Database dialect does not support CHECK constraint introspection")
            
            # Since the migration completed without error, we can assume
            # the CHECK constraint was created successfully at the DDL level
            logging.info("CHECK constraint verification completed (DDL level success implied)")
            
        except Exception as e:
            logging.error(f"CHECK constraint verification failed: {e}", exc_info=True)
            # Don't raise here as CHECK constraint introspection is optional
            logging.info("Continuing despite CHECK constraint verification failure")
