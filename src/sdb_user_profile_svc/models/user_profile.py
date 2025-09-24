from sqlalchemy import Column, Integer, String, Text, Index, func
import sqlalchemy.types
from sqlalchemy.orm import validates
from .base import Base
from sdb_user_profile_svc.utils.validation import is_korean_only, has_special_characters


class UserProfile(Base):
    __tablename__ = 'user_profile'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, index=True)
    name = Column(String(6), nullable=False)
    region = Column(String(10), nullable=False)
    company = Column(String(10), nullable=True)
    bio = Column(String(128), nullable=True)
    hobbies = Column(String(10), nullable=True)
    interests = Column(Text, nullable=True)
    age = Column(Integer, nullable=True)
    created_at = Column(sqlalchemy.types.TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(sqlalchemy.types.TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    @validates('name')
    def validate_name(self, key, value):
        """Validate name field: required, max 6 chars, Korean only."""
        if not value or value.strip() == "":
            raise ValueError("name is required")
        if len(value) > 6:
            raise ValueError("name length must be at most 6 characters")
        if not is_korean_only(value):
            raise ValueError("name must contain only Korean characters and spaces")
        return value

    @validates('region')
    def validate_region(self, key, value):
        """Validate region field: required, max 10 chars, Korean only."""
        if not value or value.strip() == "":
            raise ValueError("region is required")
        if len(value) > 10:
            raise ValueError("region length must be at most 10 characters")
        if not is_korean_only(value):
            raise ValueError("region must contain only Korean characters and spaces")
        return value

    @validates('company')
    def validate_company(self, key, value):
        """Validate company field: optional, max 10 chars, Korean only if provided."""
        if value is None:
            return value
        if len(value) > 10:
            raise ValueError("company length must be at most 10 characters")
        if not is_korean_only(value):
            raise ValueError("company must contain only Korean characters and spaces")
        return value

    @validates('bio')
    def validate_bio(self, key, value):
        """Validate bio field: optional, max 128 chars."""
        if value is not None and len(value) > 128:
            raise ValueError("bio length must be at most 128 characters")
        return value

    @validates('hobbies')
    def validate_hobbies(self, key, value):
        """Validate hobbies field: optional, max 10 chars, no special chars."""
        if value is None:
            return value
        if len(value) > 10:
            raise ValueError("hobbies length must be at most 10 characters")
        if has_special_characters(value):
            raise ValueError("hobbies cannot contain special characters")
        return value

    @validates('age')
    def validate_age(self, key, value):
        """Validate age field: optional, must be between 0-200 inclusive."""
        if value is not None and not (0 <= value <= 200):
            raise ValueError("age must be between 0 and 200 inclusive")
        return value

    def __repr__(self):
        return f"<UserProfile(id={self.id}, name='{self.name}', region='{self.region}')>"


# Define indexes for efficient lookup
Index('idx_user_profile_name', UserProfile.name)
Index('idx_user_profile_region', UserProfile.region)
