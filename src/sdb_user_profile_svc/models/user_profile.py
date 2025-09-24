from sqlalchemy import Column, Integer, String, Text, DateTime, Index, func
from .base import Base


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
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<UserProfile(id={self.id}, name='{self.name}', region='{self.region}')>"


# Define indexes for efficient lookup
Index('idx_user_profile_name', UserProfile.name)
Index('idx_user_profile_region', UserProfile.region)
