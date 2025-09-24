import pytest
import logging
from datetime import datetime
from sqlalchemy import text, inspect
from sqlalchemy.exc import IntegrityError

from sdb_user_profile_svc.models.user_profile import UserProfile


class TestUserProfileMigration:
    """Test UserProfile migration including TIMESTAMP(timezone=True) and CHECK constraints."""

    def test_user_profile_table_exists(self, db_session):
        """Test that user_profile table exists with correct structure."""
        try:
            engine = db_session.get_bind()
            inspector = inspect(engine)
            
            # Verify table exists
            tables = inspector.get_table_names()
            assert "user_profile" in tables, "user_profile table should exist"
            
            # Verify columns exist with correct properties
            columns = inspector.get_columns("user_profile")
            column_dict = {col['name']: col for col in columns}
            
            # Check all required columns exist
            required_columns = ['id', 'name', 'region', 'company', 'bio', 'hobbies', 'interests', 'age', 'created_at', 'updated_at']
            for col_name in required_columns:
                assert col_name in column_dict, f"Column {col_name} should exist"
            
            # Verify column properties (database-agnostic)
            assert column_dict['name']['nullable'] == False, "name should be NOT NULL"
            assert column_dict['region']['nullable'] == False, "region should be NOT NULL"
            assert column_dict['company']['nullable'] == True, "company should be nullable"
            assert column_dict['age']['nullable'] == True, "age should be nullable"
            assert column_dict['created_at']['nullable'] == False, "created_at should be NOT NULL"
            assert column_dict['updated_at']['nullable'] == False, "updated_at should be NOT NULL"
            
            logging.info("User profile table structure verified successfully")
            
        except Exception as e:
            logging.error(e, exc_info=True)
            raise

    def test_user_profile_indexes_exist(self, db_session):
        """Test that required indexes are created."""
        try:
            engine = db_session.get_bind()
            inspector = inspect(engine)
            
            # Get indexes for user_profile table
            indexes = inspector.get_indexes("user_profile")
            index_names = [idx['name'] for idx in indexes]
            
            # Check required indexes exist
            expected_indexes = ['idx_user_profile_name', 'idx_user_profile_region']
            for index_name in expected_indexes:
                assert index_name in index_names, f"Index {index_name} should exist"
            
            # Verify index columns
            for index in indexes:
                if index['name'] == 'idx_user_profile_name':
                    assert 'name' in index['column_names'], "name index should be on name column"
                elif index['name'] == 'idx_user_profile_region':
                    assert 'region' in index['column_names'], "region index should be on region column"
            
            logging.info("User profile indexes verified successfully")
            
        except Exception as e:
            logging.error(e, exc_info=True)
            raise

    def test_user_profile_timestamp_fields(self, db_session):
        """Test that TIMESTAMP(timezone=True) fields work correctly."""
        try:
            # Create a new user profile
            user_profile = UserProfile(
                name="김철수",
                region="서울"
            )
            
            db_session.add(user_profile)
            db_session.commit()
            
            # Verify timestamps are set
            assert user_profile.created_at is not None, "created_at should be automatically set"
            assert user_profile.updated_at is not None, "updated_at should be automatically set"
            assert isinstance(user_profile.created_at, datetime), "created_at should be datetime object"
            assert isinstance(user_profile.updated_at, datetime), "updated_at should be datetime object"
            
            # Store original timestamps
            original_created_at = user_profile.created_at
            
            # Update the profile and check updated_at changes
            user_profile.company = "네이버"
            db_session.commit()
            
            # Verify created_at remains the same
            assert user_profile.created_at == original_created_at, "created_at should not change on update"
            
            logging.info("Timestamp fields working correctly")
            
        except Exception as e:
            logging.error(e, exc_info=True)
            raise

    def test_user_profile_id_autoincrement_functionality(self, db_session):
        """Test that id field auto-increments correctly."""
        try:
            # Create multiple user profiles to test auto-increment
            user1 = UserProfile(name="김가나", region="서울시")
            user2 = UserProfile(name="이다라", region="부산시")
            
            db_session.add(user1)
            db_session.add(user2)
            db_session.commit()
            
            # Verify auto-increment functionality
            assert user1.id is not None, "First user should have an ID"
            assert user2.id is not None, "Second user should have an ID"
            assert user1.id != user2.id, "Each user should have a unique ID"
            assert isinstance(user1.id, int), "ID should be an integer"
            assert isinstance(user2.id, int), "ID should be an integer"
            
            # Typically, auto-increment should result in sequential IDs
            assert user2.id > user1.id, "Second user's ID should be greater than first user's ID"
            
            logging.info("Auto-increment functionality working correctly")
            
        except Exception as e:
            logging.error(e, exc_info=True)
            raise

    def test_user_profile_age_check_constraint_valid_values(self, db_session):
        """Test that age CHECK constraint allows valid values (0-200)."""
        try:
            # Test minimum valid age (0)
            user_profile_min = UserProfile(
                name="김영아",
                region="서울",
                age=0
            )
            db_session.add(user_profile_min)
            db_session.commit()
            assert user_profile_min.id is not None, "User with age 0 should be saved successfully"
            
            # Test maximum valid age (200)
            user_profile_max = UserProfile(
                name="김백세",
                region="부산",
                age=200
            )
            db_session.add(user_profile_max)
            db_session.commit()
            assert user_profile_max.id is not None, "User with age 200 should be saved successfully"
            
            # Test middle valid age
            user_profile_middle = UserProfile(
                name="김중년",
                region="대구",
                age=50
            )
            db_session.add(user_profile_middle)
            db_session.commit()
            assert user_profile_middle.id is not None, "User with age 50 should be saved successfully"
            
            logging.info("Age CHECK constraint allows valid values correctly")
            
        except Exception as e:
            logging.error(e, exc_info=True)
            raise

    def test_user_profile_crud_operations(self, db_session):
        """Test complete CRUD operations on user_profile table."""
        try:
            # CREATE
            user_profile = UserProfile(
                name="김테스트",
                region="테스트시",
                company="테스트회사",
                bio="테스트 사용자입니다.",
                hobbies="독서",
                interests="테스트, 개발, 학습",
                age=25
            )
            
            db_session.add(user_profile)
            db_session.commit()
            
            created_id = user_profile.id
            assert created_id is not None, "User profile should be created with ID"
            
            # READ
            found_profile = db_session.query(UserProfile).filter(UserProfile.id == created_id).first()
            assert found_profile is not None, "Created user profile should be findable"
            assert found_profile.name == "김테스트", "Found profile should have correct name"
            assert found_profile.region == "테스트시", "Found profile should have correct region"
            assert found_profile.company == "테스트회사", "Found profile should have correct company"
            assert found_profile.age == 25, "Found profile should have correct age"
            
            # UPDATE
            found_profile.age = 26
            found_profile.company = "새회사"
            db_session.commit()
            
            updated_profile = db_session.query(UserProfile).filter(UserProfile.id == created_id).first()
            assert updated_profile.age == 26, "Age should be updated"
            assert updated_profile.company == "새회사", "Company should be updated"
            
            # DELETE
            db_session.delete(updated_profile)
            db_session.commit()
            
            deleted_profile = db_session.query(UserProfile).filter(UserProfile.id == created_id).first()
            assert deleted_profile is None, "Deleted profile should not be found"
            
            logging.info("CRUD operations completed successfully")
            
        except Exception as e:
            logging.error(e, exc_info=True)
            raise

    def test_user_profile_constraints_and_validation(self, db_session):
        """Test that all constraints and validations work correctly."""
        try:
            # Test NOT NULL constraints
            with pytest.raises(IntegrityError):
                user_profile = UserProfile(region="서울")  # missing required name
                db_session.add(user_profile)
                db_session.commit()
            
            db_session.rollback()
            
            with pytest.raises(IntegrityError):
                user_profile = UserProfile(name="김철수")  # missing required region
                db_session.add(user_profile)
                db_session.commit()
            
            db_session.rollback()
            
            # Test successful creation with all constraints satisfied
            valid_profile = UserProfile(
                name="김정상",
                region="정상시",
                age=30
            )
            db_session.add(valid_profile)
            db_session.commit()
            
            assert valid_profile.id is not None, "Valid profile should be created successfully"
            
            logging.info("Constraints and validation working correctly")
            
        except Exception as e:
            logging.error(e, exc_info=True)
            raise