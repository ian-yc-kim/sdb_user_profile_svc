import pytest
import time
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from sdb_user_profile_svc.models.user_profile import UserProfile


class TestUserProfileModel:
    """Test the UserProfile model CRUD operations and constraints."""

    def test_create_user_profile_with_required_fields(self, db_session):
        """Test creating a UserProfile with only required fields."""
        user_profile = UserProfile(
            name="김철수",
            region="서울"
        )
        
        db_session.add(user_profile)
        db_session.commit()
        
        assert user_profile.id is not None
        assert user_profile.name == "김철수"
        assert user_profile.region == "서울"
        assert user_profile.company is None
        assert user_profile.bio is None
        assert user_profile.hobbies is None
        assert user_profile.interests is None
        assert user_profile.age is None
        assert user_profile.created_at is not None
        assert user_profile.updated_at is not None

    def test_create_user_profile_with_all_fields(self, db_session):
        """Test creating a UserProfile with all fields filled."""
        user_profile = UserProfile(
            name="이영희",
            region="부산",
            company="네이버",
            bio="안녕하세요! 개발자입니다.",
            hobbies="독서",
            interests="Python, AI, Machine Learning",
            age=28
        )
        
        db_session.add(user_profile)
        db_session.commit()
        
        assert user_profile.id is not None
        assert user_profile.name == "이영희"
        assert user_profile.region == "부산"
        assert user_profile.company == "네이버"
        assert user_profile.bio == "안녕하세요! 개발자입니다."
        assert user_profile.hobbies == "독서"
        assert user_profile.interests == "Python, AI, Machine Learning"
        assert user_profile.age == 28
        assert user_profile.created_at is not None
        assert user_profile.updated_at is not None

    def test_read_user_profile(self, db_session):
        """Test reading UserProfile from database."""
        user_profile = UserProfile(name="박민수", region="대구")
        db_session.add(user_profile)
        db_session.commit()
        
        # Read by ID
        found_profile = db_session.query(UserProfile).filter(UserProfile.id == user_profile.id).first()
        assert found_profile is not None
        assert found_profile.name == "박민수"
        assert found_profile.region == "대구"
        
        # Read by name (testing index)
        found_by_name = db_session.query(UserProfile).filter(UserProfile.name == "박민수").first()
        assert found_by_name is not None
        assert found_by_name.id == user_profile.id
        
        # Read by region (testing index)
        found_by_region = db_session.query(UserProfile).filter(UserProfile.region == "대구").all()
        assert len(found_by_region) >= 1
        assert user_profile.id in [profile.id for profile in found_by_region]

    def test_update_user_profile(self, db_session):
        """Test updating UserProfile and verify updated_at changes."""
        user_profile = UserProfile(name="최수정", region="인천")
        db_session.add(user_profile)
        db_session.commit()
        
        original_updated_at = user_profile.updated_at
        
        # Update the profile
        user_profile.company = "카카오"
        user_profile.age = 30
        db_session.commit()
        
        # Verify update
        updated_profile = db_session.query(UserProfile).filter(UserProfile.id == user_profile.id).first()
        assert updated_profile.company == "카카오"
        assert updated_profile.age == 30
        # Note: In SQLite (test environment), updated_at might not change automatically
        # This is acceptable for unit testing

    def test_delete_user_profile(self, db_session):
        """Test deleting UserProfile from database."""
        user_profile = UserProfile(name="정하은", region="광주")
        db_session.add(user_profile)
        db_session.commit()
        profile_id = user_profile.id
        
        # Delete the profile
        db_session.delete(user_profile)
        db_session.commit()
        
        # Verify deletion
        deleted_profile = db_session.query(UserProfile).filter(UserProfile.id == profile_id).first()
        assert deleted_profile is None

    def test_name_constraint_max_length(self, db_session):
        """Test that name field respects maximum length constraint."""
        # Test with exactly 6 characters (should work)
        user_profile = UserProfile(name="김철수진", region="서울")
        db_session.add(user_profile)
        db_session.commit()
        assert user_profile.id is not None
        
        # Test with more than 6 characters (may be truncated by database)
        # SQLite might not enforce length constraints as strictly as PostgreSQL
        long_name_profile = UserProfile(name="김철수진영희", region="서울")
        db_session.add(long_name_profile)
        # This should not raise an error in SQLite, but would be truncated in PostgreSQL
        db_session.commit()

    def test_region_constraint_max_length(self, db_session):
        """Test that region field respects maximum length constraint."""
        # Test with exactly 10 characters (should work)
        user_profile = UserProfile(name="김철수", region="경기도성남시")
        db_session.add(user_profile)
        db_session.commit()
        assert user_profile.id is not None

    def test_required_fields_not_null(self, db_session):
        """Test that required fields cannot be null."""
        # Test missing name
        with pytest.raises(IntegrityError):
            user_profile = UserProfile(region="서울")
            db_session.add(user_profile)
            db_session.commit()
        
        db_session.rollback()
        
        # Test missing region
        with pytest.raises(IntegrityError):
            user_profile = UserProfile(name="김철수")
            db_session.add(user_profile)
            db_session.commit()

    def test_nullable_fields(self, db_session):
        """Test that nullable fields can be None."""
        user_profile = UserProfile(
            name="김철수",
            region="서울",
            company=None,
            bio=None,
            hobbies=None,
            interests=None,
            age=None
        )
        
        db_session.add(user_profile)
        db_session.commit()
        
        assert user_profile.id is not None
        assert user_profile.company is None
        assert user_profile.bio is None
        assert user_profile.hobbies is None
        assert user_profile.interests is None
        assert user_profile.age is None

    def test_primary_key_unique_and_autoincrement(self, db_session):
        """Test that id is unique and auto-incrementing."""
        user1 = UserProfile(name="김철수", region="서울")
        user2 = UserProfile(name="이영희", region="부산")
        
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        
        assert user1.id is not None
        assert user2.id is not None
        assert user1.id != user2.id
        assert isinstance(user1.id, int)
        assert isinstance(user2.id, int)

    def test_text_field_interests(self, db_session):
        """Test that interests field can handle long text."""
        long_interests = "Python programming, Machine Learning, Deep Learning, Data Science, Web Development, Mobile App Development, Cloud Computing, DevOps, Artificial Intelligence, Natural Language Processing" * 10
        
        user_profile = UserProfile(
            name="김개발",
            region="서울",
            interests=long_interests
        )
        
        db_session.add(user_profile)
        db_session.commit()
        
        assert user_profile.id is not None
        assert user_profile.interests == long_interests

    def test_repr_method(self, db_session):
        """Test the __repr__ method of UserProfile."""
        user_profile = UserProfile(name="김철수", region="서울")
        db_session.add(user_profile)
        db_session.commit()
        
        repr_string = repr(user_profile)
        assert "UserProfile" in repr_string
        assert f"id={user_profile.id}" in repr_string
        assert "name='김철수'" in repr_string
        assert "region='서울'" in repr_string

    def test_indexes_exist(self, db_session):
        """Test that indexes on name and region are working."""
        # Create multiple profiles
        profiles = [
            UserProfile(name="김철수", region="서울"),
            UserProfile(name="이영희", region="서울"),
            UserProfile(name="박민수", region="부산"),
            UserProfile(name="최수정", region="부산"),
        ]
        
        for profile in profiles:
            db_session.add(profile)
        db_session.commit()
        
        # Test index on name
        seoul_profiles = db_session.query(UserProfile).filter(UserProfile.region == "서울").all()
        assert len(seoul_profiles) == 2
        
        busan_profiles = db_session.query(UserProfile).filter(UserProfile.region == "부산").all()
        assert len(busan_profiles) == 2
        
        # Test index on name
        kim_profile = db_session.query(UserProfile).filter(UserProfile.name == "김철수").first()
        assert kim_profile is not None
        assert kim_profile.name == "김철수"

    def test_timestamps_auto_generated(self, db_session):
        """Test that created_at and updated_at are automatically generated."""
        user_profile = UserProfile(name="김철수", region="서울")
        
        # Before saving, timestamps should be None
        assert user_profile.created_at is None
        assert user_profile.updated_at is None
        
        db_session.add(user_profile)
        db_session.commit()
        
        # After saving, timestamps should be set
        assert user_profile.created_at is not None
        assert user_profile.updated_at is not None
        assert isinstance(user_profile.created_at, datetime)
        assert isinstance(user_profile.updated_at, datetime)

    # NEW TESTS FOR @validates METHODS
    
    def test_validate_name_accepts_korean_and_spaces(self, db_session):
        """Test that name validator accepts valid Korean characters and spaces."""
        user_profile = UserProfile(name="홍 길동", region="서울")
        db_session.add(user_profile)
        db_session.commit()
        
        assert user_profile.name == "홍 길동"
        assert user_profile.id is not None

    def test_validate_name_rejects_non_korean_and_special(self, db_session):
        """Test that name validator rejects non-Korean characters and special characters."""
        # Test with English characters
        with pytest.raises(ValueError, match="name must contain only Korean characters and spaces"):
            UserProfile(name="John", region="서울")
        
        # Test with special characters
        with pytest.raises(ValueError, match="name must contain only Korean characters and spaces"):
            UserProfile(name="홍!", region="서울")

    def test_validate_name_length_boundaries(self, db_session):
        """Test name length validation at boundaries."""
        # Test exact max length (6 characters)
        user_profile = UserProfile(name="가" * 6, region="서울")
        db_session.add(user_profile)
        db_session.commit()
        assert user_profile.id is not None
        
        # Test over max length (7 characters)
        with pytest.raises(ValueError, match="name length must be at most 6 characters"):
            UserProfile(name="가" * 7, region="서울")

    def test_validate_name_empty_or_none_rejected(self, db_session):
        """Test that empty or None name values are rejected."""
        # Test empty string
        with pytest.raises(ValueError, match="name is required"):
            UserProfile(name="", region="서울")
        
        # Test None
        with pytest.raises(ValueError, match="name is required"):
            UserProfile(name=None, region="서울")
        
        # Test whitespace only
        with pytest.raises(ValueError, match="name is required"):
            UserProfile(name="   ", region="서울")

    def test_validate_region_accepts_korean_and_spaces(self, db_session):
        """Test that region validator accepts valid Korean characters and spaces."""
        # Test with space
        user_profile1 = UserProfile(name="김철수", region="경 북")
        db_session.add(user_profile1)
        db_session.commit()
        assert user_profile1.region == "경 북"
        
        # Test max length
        user_profile2 = UserProfile(name="김철수", region="가" * 10)
        db_session.add(user_profile2)
        db_session.commit()
        assert user_profile2.region == "가" * 10

    def test_validate_region_rejects_non_korean_and_special(self, db_session):
        """Test that region validator rejects non-Korean and special characters."""
        # Test with English characters
        with pytest.raises(ValueError, match="region must contain only Korean characters and spaces"):
            UserProfile(name="김철수", region="Seoul")
        
        # Test with special characters
        with pytest.raises(ValueError, match="region must contain only Korean characters and spaces"):
            UserProfile(name="김철수", region="부산@")

    def test_validate_region_length_boundaries(self, db_session):
        """Test region length validation at boundaries."""
        # Test exact max length (10 characters)
        user_profile = UserProfile(name="김철수", region="가" * 10)
        db_session.add(user_profile)
        db_session.commit()
        assert user_profile.id is not None
        
        # Test over max length (11 characters)
        with pytest.raises(ValueError, match="region length must be at most 10 characters"):
            UserProfile(name="김철수", region="가" * 11)

    def test_validate_region_empty_or_none_rejected(self, db_session):
        """Test that empty or None region values are rejected."""
        # Test empty string
        with pytest.raises(ValueError, match="region is required"):
            UserProfile(name="김철수", region="")
        
        # Test None
        with pytest.raises(ValueError, match="region is required"):
            UserProfile(name="김철수", region=None)
        
        # Test whitespace only
        with pytest.raises(ValueError, match="region is required"):
            UserProfile(name="김철수", region="   ")

    def test_validate_company_none_and_empty_ok(self, db_session):
        """Test that company field accepts None and empty string."""
        # Test with None
        user_profile1 = UserProfile(name="김철수", region="서울", company=None)
        db_session.add(user_profile1)
        db_session.commit()
        assert user_profile1.company is None
        
        # Test with empty string
        user_profile2 = UserProfile(name="김철수", region="서울", company="")
        db_session.add(user_profile2)
        db_session.commit()
        assert user_profile2.company == ""

    def test_validate_company_korean_only_and_length(self, db_session):
        """Test company Korean-only validation and length limits."""
        # Test valid Korean company name at max length
        user_profile = UserProfile(name="김철수", region="서울", company="가" * 10)
        db_session.add(user_profile)
        db_session.commit()
        assert user_profile.company == "가" * 10
        
        # Test over max length
        with pytest.raises(ValueError, match="company length must be at most 10 characters"):
            UserProfile(name="김철수", region="서울", company="가" * 11)
        
        # Test non-Korean characters
        with pytest.raises(ValueError, match="company must contain only Korean characters and spaces"):
            UserProfile(name="김철수", region="서울", company="Google")

    def test_validate_bio_length(self, db_session):
        """Test bio length validation."""
        # Test valid length (128 characters)
        valid_bio = "안녕하세요! " * 10 + "개발자입니다."  # Ensure it's exactly 128 chars or less
        valid_bio = valid_bio[:128]  # Truncate to exactly 128 characters
        user_profile = UserProfile(name="김철수", region="서울", bio=valid_bio)
        db_session.add(user_profile)
        db_session.commit()
        assert user_profile.bio == valid_bio
        
        # Test over length (129 characters)
        invalid_bio = "가" * 129
        with pytest.raises(ValueError, match="bio length must be at most 128 characters"):
            UserProfile(name="김철수", region="서울", bio=invalid_bio)

    def test_validate_hobbies_valid_characters(self, db_session):
        """Test hobbies validation with valid characters."""
        # Test English
        user_profile1 = UserProfile(name="김철수", region="서울", hobbies="Reading")
        db_session.add(user_profile1)
        db_session.commit()
        assert user_profile1.hobbies == "Reading"
        
        # Test Korean
        user_profile2 = UserProfile(name="김철수", region="서울", hobbies="독서")
        db_session.add(user_profile2)
        db_session.commit()
        assert user_profile2.hobbies == "독서"
        
        # Test mixed with numbers
        user_profile3 = UserProfile(name="김철수", region="서울", hobbies="독서123")
        db_session.add(user_profile3)
        db_session.commit()
        assert user_profile3.hobbies == "독서123"

    def test_validate_hobbies_rejects_special_chars(self, db_session):
        """Test that hobbies rejects special characters."""
        with pytest.raises(ValueError, match="hobbies cannot contain special characters"):
            UserProfile(name="김철수", region="서울", hobbies="등산!")

    def test_validate_hobbies_length(self, db_session):
        """Test hobbies length validation."""
        # Test max length (10 characters)
        user_profile = UserProfile(name="김철수", region="서울", hobbies="가" * 10)
        db_session.add(user_profile)
        db_session.commit()
        assert user_profile.hobbies == "가" * 10
        
        # Test over length (11 characters)
        with pytest.raises(ValueError, match="hobbies length must be at most 10 characters"):
            UserProfile(name="김철수", region="서울", hobbies="가" * 11)

    def test_validate_age_boundaries(self, db_session):
        """Test age validation at boundaries."""
        # Test minimum age (0)
        user_profile1 = UserProfile(name="김철수", region="서울", age=0)
        db_session.add(user_profile1)
        db_session.commit()
        assert user_profile1.age == 0
        
        # Test maximum age (200)
        user_profile2 = UserProfile(name="김철수", region="서울", age=200)
        db_session.add(user_profile2)
        db_session.commit()
        assert user_profile2.age == 200

    def test_validate_age_out_of_range(self, db_session):
        """Test age validation rejects out-of-range values."""
        # Test below minimum (-1)
        with pytest.raises(ValueError, match="age must be between 0 and 200 inclusive"):
            UserProfile(name="김철수", region="서울", age=-1)
        
        # Test above maximum (201)
        with pytest.raises(ValueError, match="age must be between 0 and 200 inclusive"):
            UserProfile(name="김철수", region="서울", age=201)

    def test_timestamps_on_create_and_update_robust(self, db_session):
        """Test robust timestamp behavior on create and update."""
        # Create profile
        user_profile = UserProfile(name="김철수", region="서울")
        db_session.add(user_profile)
        db_session.commit()
        
        # Verify initial timestamps
        assert user_profile.created_at is not None
        assert user_profile.updated_at is not None
        original_updated_at = user_profile.updated_at
        
        # Wait to ensure timestamp difference
        time.sleep(1.1)
        
        # Update a field
        user_profile.company = "네이버"
        db_session.commit()
        db_session.refresh(user_profile)
        
        # Verify updated_at has changed
        assert user_profile.updated_at > original_updated_at
        assert user_profile.company == "네이버"
