from sqlalchemy import Column, PrimaryKeyConstraint, String
from sqlalchemy.ext.declarative import declarative_base

# Import session management from centralized module
from sdb_user_profile_svc.database.session import SessionLocal, get_db

Base = declarative_base()

# Re-export for compatibility with existing imports
__all__ = ['Base', 'SessionLocal', 'get_db']
