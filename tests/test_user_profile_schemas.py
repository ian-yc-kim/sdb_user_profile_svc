import pytest
from datetime import datetime
from pydantic import ValidationError
from sdb_user_profile_svc.schemas.user_profile import (
    UserProfileCreate, 
    UserProfileRead, 
    UserProfileUpdate
)
from sdb_user_profile_svc.models.user_profile import UserProfile


class TestUserProfileCreateSchema:
    """Test UserProfileCreate Pydantic schema validation."""

    def test_create_schema_rejects_non_korean_name(self):
        """Test that UserProfileCreate rejects non-Korean name."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="John",
                region="서울"
            )
        assert "name must contain only Korean characters and spaces" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="김철수@",
                region="서울"
            )
        assert "name must contain only Korean characters and spaces" in str(exc_info.value)

    def test_create_schema_rejects_non_korean_region(self):
        """Test that UserProfileCreate rejects non-Korean region."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="김철수",
                region="Seoul"
            )
        assert "region must contain only Korean characters and spaces" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="김철수",
                region="서울@"
            )
        assert "region must contain only Korean characters and spaces" in str(exc_info.value)

    def test_create_schema_rejects_non_korean_company(self):
        """Test that UserProfileCreate rejects non-Korean company when provided."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="김철수",
                region="서울",
                company="Google"
            )
        assert "company must contain only Korean characters and spaces" in str(exc_info.value)

        # Should work with Korean company
        schema = UserProfileCreate(
            name="김철수",
            region="서울",
            company="네이버"
        )
        assert schema.company == "네이버"

        # Should work with None company
        schema2 = UserProfileCreate(
            name="김철수",
            region="서울",
            company=None
        )
        assert schema2.company is None

    def test_create_schema_rejects_overlength_fields(self):
        """Test that UserProfileCreate rejects fields exceeding length limits."""
        # Test name too long (> 6 characters)
        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="김철수진영희민수",  # 8 Korean characters
                region="서울"
            )
        assert "String should have at most 6 characters" in str(exc_info.value)

        # Test region too long (> 10 characters)
        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="김철수",
                region="경기도성남시분당구정자동"  # 12 Korean characters
            )
        assert "String should have at most 10 characters" in str(exc_info.value)

        # Test company too long (> 10 characters)
        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="김철수",
                region="서울",
                company="삼성전자주식회사한국지사"  # 12 Korean characters
            )
        assert "String should have at most 10 characters" in str(exc_info.value)

        # Test bio too long (> 128 characters)
        long_bio = "a" * 129
        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="김철수",
                region="서울",
                bio=long_bio
            )
        assert "String should have at most 128 characters" in str(exc_info.value)

        # Test hobbies too long (> 10 characters)
        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="김철수",
                region="서울",
                hobbies="독서음악영화운동게임"  # 11 Korean characters
            )
        assert "String should have at most 10 characters" in str(exc_info.value)

    def test_create_schema_rejects_age_out_of_range(self):
        """Test that UserProfileCreate rejects age outside 0-200 range."""
        # Test negative age
        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="김철수",
                region="서울",
                age=-1
            )
        assert "Input should be greater than or equal to 0" in str(exc_info.value)

        # Test age over 200
        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="김철수",
                region="서울",
                age=201
            )
        assert "Input should be less than or equal to 200" in str(exc_info.value)

    def test_create_schema_rejects_hobbies_with_special_characters(self):
        """Test that UserProfileCreate rejects hobbies with special characters."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="김철수",
                region="서울",
                hobbies="독서@음악"
            )
        assert "hobbies cannot contain special characters" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="김철수",
                region="서울",
                hobbies="독서!영화"
            )
        assert "hobbies cannot contain special characters" in str(exc_info.value)

    def test_create_schema_accepts_valid_data(self):
        """Test that UserProfileCreate accepts valid data."""
        schema = UserProfileCreate(
            name="김철수",
            region="서울특별시",
            company="네이버",
            bio="안녕하세요! 저는 개발자입니다.",
            hobbies="독서 음악",
            interests="Python, FastAPI, PostgreSQL",
            age=30
        )
        
        assert schema.name == "김철수"
        assert schema.region == "서울특별시"
        assert schema.company == "네이버"
        assert schema.bio == "안녕하세요! 저는 개발자입니다."
        assert schema.hobbies == "독서 음악"
        assert schema.interests == "Python, FastAPI, PostgreSQL"
        assert schema.age == 30

    def test_create_schema_accepts_minimal_required_fields(self):
        """Test that UserProfileCreate accepts only required fields."""
        schema = UserProfileCreate(
            name="김철수",
            region="서울"
        )
        
        assert schema.name == "김철수"
        assert schema.region == "서울"
        assert schema.company is None
        assert schema.bio is None
        assert schema.hobbies is None
        assert schema.interests is None
        assert schema.age is None

    def test_create_schema_rejects_empty_required_fields(self):
        """Test that UserProfileCreate rejects empty required fields."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="",
                region="서울"
            )
        assert "name is required" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            UserProfileCreate(
                name="김철수",
                region=""
            )
        assert "region is required" in str(exc_info.value)


class TestUserProfileReadSchema:
    """Test UserProfileRead Pydantic schema."""

    def test_read_schema_from_attributes_works(self, db_session):
        """Test that UserProfileRead can be created from ORM instance."""
        # Create and save a UserProfile to the database
        user_profile = UserProfile(
            name="김철수",
            region="서울",
            company="네이버",
            bio="안녕하세요! 개발자입니다.",
            hobbies="독서 음악",
            interests="Python, FastAPI",
            age=30
        )
        
        db_session.add(user_profile)
        db_session.commit()
        
        # Create UserProfileRead from the ORM instance
        read_schema = UserProfileRead.model_validate(user_profile)
        
        # Verify all fields are correctly populated
        assert read_schema.id == user_profile.id
        assert read_schema.name == "김철수"
        assert read_schema.region == "서울"
        assert read_schema.company == "네이버"
        assert read_schema.bio == "안녕하세요! 개발자입니다."
        assert read_schema.hobbies == "독서 음악"
        assert read_schema.interests == "Python, FastAPI"
        assert read_schema.age == 30
        assert isinstance(read_schema.created_at, datetime)
        assert isinstance(read_schema.updated_at, datetime)

    def test_read_schema_model_dump_works(self, db_session):
        """Test that UserProfileRead can be dumped to dict."""
        user_profile = UserProfile(
            name="이영희",
            region="부산",
            age=25
        )
        
        db_session.add(user_profile)
        db_session.commit()
        
        read_schema = UserProfileRead.model_validate(user_profile)
        data = read_schema.model_dump()
        
        assert isinstance(data, dict)
        assert data["id"] == user_profile.id
        assert data["name"] == "이영희"
        assert data["region"] == "부산"
        assert data["company"] is None
        assert data["bio"] is None
        assert data["hobbies"] is None
        assert data["interests"] is None
        assert data["age"] == 25
        assert "created_at" in data
        assert "updated_at" in data


class TestUserProfileUpdateSchema:
    """Test UserProfileUpdate Pydantic schema validation."""

    def test_update_schema_accepts_partial_valid_fields(self):
        """Test that UserProfileUpdate accepts partial valid fields."""
        # Test updating only name
        schema = UserProfileUpdate(name="김철수")
        assert schema.name == "김철수"
        assert schema.region is None
        assert schema.company is None
        
        # Test updating only region
        schema2 = UserProfileUpdate(region="부산")
        assert schema2.name is None
        assert schema2.region == "부산"
        
        # Test updating multiple fields
        schema3 = UserProfileUpdate(
            name="박민수",
            region="대구",
            age=35
        )
        assert schema3.name == "박민수"
        assert schema3.region == "대구"
        assert schema3.age == 35
        assert schema3.company is None

    def test_update_schema_rejects_invalid_name(self):
        """Test that UserProfileUpdate rejects invalid name."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(name="John")
        assert "name must contain only Korean characters and spaces" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(name="")
        assert "name cannot be empty if provided" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(name="   ")
        assert "name cannot be empty if provided" in str(exc_info.value)

    def test_update_schema_rejects_invalid_region(self):
        """Test that UserProfileUpdate rejects invalid region."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(region="Seoul")
        assert "region must contain only Korean characters and spaces" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(region="")
        assert "region cannot be empty if provided" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(region="   ")
        assert "region cannot be empty if provided" in str(exc_info.value)

    def test_update_schema_rejects_invalid_company(self):
        """Test that UserProfileUpdate rejects invalid company."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(company="Google")
        assert "company must contain only Korean characters and spaces" in str(exc_info.value)

        # Should work with Korean company
        schema = UserProfileUpdate(company="네이버")
        assert schema.company == "네이버"

    def test_update_schema_rejects_overlength_fields(self):
        """Test that UserProfileUpdate rejects overlength fields."""
        # Test name too long
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(name="김철수진영희민수")
        assert "String should have at most 6 characters" in str(exc_info.value)

        # Test region too long
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(region="경기도성남시분당구정자동")
        assert "String should have at most 10 characters" in str(exc_info.value)

        # Test company too long
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(company="삼성전자주식회사한국지사")
        assert "String should have at most 10 characters" in str(exc_info.value)

        # Test bio too long
        long_bio = "a" * 129
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(bio=long_bio)
        assert "String should have at most 128 characters" in str(exc_info.value)

        # Test hobbies too long
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(hobbies="독서음악영화운동게임")
        assert "String should have at most 10 characters" in str(exc_info.value)

    def test_update_schema_rejects_age_out_of_range(self):
        """Test that UserProfileUpdate rejects age out of range."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(age=-1)
        assert "Input should be greater than or equal to 0" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(age=201)
        assert "Input should be less than or equal to 200" in str(exc_info.value)

    def test_update_schema_rejects_hobbies_with_special_characters(self):
        """Test that UserProfileUpdate rejects hobbies with special characters."""
        with pytest.raises(ValidationError) as exc_info:
            UserProfileUpdate(hobbies="독서@음악")
        assert "hobbies cannot contain special characters" in str(exc_info.value)

    def test_update_schema_accepts_all_none_values(self):
        """Test that UserProfileUpdate accepts all None values."""
        schema = UserProfileUpdate()
        assert schema.name is None
        assert schema.region is None
        assert schema.company is None
        assert schema.bio is None
        assert schema.hobbies is None
        assert schema.interests is None
        assert schema.age is None

    def test_update_schema_accepts_valid_partial_update(self):
        """Test that UserProfileUpdate accepts valid partial update."""
        schema = UserProfileUpdate(
            name="김철수",
            company="카카오",
            age=32
        )
        
        assert schema.name == "김철수"
        assert schema.region is None  # Not provided
        assert schema.company == "카카오"
        assert schema.bio is None  # Not provided
        assert schema.hobbies is None  # Not provided
        assert schema.interests is None  # Not provided
        assert schema.age == 32

    def test_update_schema_boundary_values(self):
        """Test UserProfileUpdate with boundary values."""
        # Test age boundaries
        schema1 = UserProfileUpdate(age=0)
        assert schema1.age == 0
        
        schema2 = UserProfileUpdate(age=200)
        assert schema2.age == 200
        
        # Test exact length limits
        schema3 = UserProfileUpdate(
            name="김철수진",  # Exactly at limit
            region="경기도성남시분",  # Exactly at limit
            company="삼성전자주식",  # Exactly at limit
            bio="a" * 128,  # Exactly 128 characters
            hobbies="독서음악영화운동"  # Exactly 10 characters
        )
        assert len(schema3.name) <= 6
        assert len(schema3.region) <= 10
        assert len(schema3.company) <= 10
        assert len(schema3.bio) == 128
        assert len(schema3.hobbies) <= 10
