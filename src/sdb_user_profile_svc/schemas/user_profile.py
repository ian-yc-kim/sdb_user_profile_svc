"""Pydantic schemas for UserProfile API operations."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from ..utils.validation import is_korean_only, has_special_characters


class UserProfileCreate(BaseModel):
    """Schema for creating a new user profile."""
    name: str = Field(..., max_length=6)
    region: str = Field(..., max_length=10)
    company: Optional[str] = Field(None, max_length=10)
    bio: Optional[str] = Field(None, max_length=128)
    hobbies: Optional[str] = Field(None, max_length=10)
    interests: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=200)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("name is required")
        
        v = v.strip()
        if not v:
            raise ValueError("name is required")
            
        if not is_korean_only(v):
            raise ValueError("name must contain only Korean characters and spaces")
        
        return v

    @field_validator('region')
    @classmethod
    def validate_region(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("region is required")
        
        v = v.strip()
        if not v:
            raise ValueError("region is required")
            
        if not is_korean_only(v):
            raise ValueError("region must contain only Korean characters and spaces")
        
        return v

    @field_validator('company')
    @classmethod
    def validate_company(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return v
        
        v = v.strip()
        if not v:
            return None
            
        if not is_korean_only(v):
            raise ValueError("company must contain only Korean characters and spaces")
        
        return v

    @field_validator('hobbies')
    @classmethod
    def validate_hobbies(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return v
        
        v = v.strip()
        if not v:
            return None
            
        if has_special_characters(v):
            raise ValueError("hobbies cannot contain special characters")
        
        return v


class UserProfileRead(BaseModel):
    """Schema for reading user profile data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    region: str
    company: Optional[str]
    bio: Optional[str]
    hobbies: Optional[str]
    interests: Optional[str]
    age: Optional[int]
    created_at: datetime
    updated_at: datetime


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile data."""
    name: Optional[str] = Field(None, max_length=6)
    region: Optional[str] = Field(None, max_length=10)
    company: Optional[str] = Field(None, max_length=10)
    bio: Optional[str] = Field(None, max_length=128)
    hobbies: Optional[str] = Field(None, max_length=10)
    interests: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=200)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        
        if v == "" or v.strip() == "":
            raise ValueError("name cannot be empty if provided")
        
        v = v.strip()
        if not is_korean_only(v):
            raise ValueError("name must contain only Korean characters and spaces")
        
        return v

    @field_validator('region')
    @classmethod
    def validate_region(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        
        if v == "" or v.strip() == "":
            raise ValueError("region cannot be empty if provided")
        
        v = v.strip()
        if not is_korean_only(v):
            raise ValueError("region must contain only Korean characters and spaces")
        
        return v

    @field_validator('company')
    @classmethod
    def validate_company(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return v
        
        v = v.strip()
        if not v:
            return None
            
        if not is_korean_only(v):
            raise ValueError("company must contain only Korean characters and spaces")
        
        return v

    @field_validator('hobbies')
    @classmethod
    def validate_hobbies(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return v
        
        v = v.strip()
        if not v:
            return None
            
        if has_special_characters(v):
            raise ValueError("hobbies cannot contain special characters")
        
        return v
