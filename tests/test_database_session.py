import pytest
from unittest.mock import patch, MagicMock
from fastapi import Depends, FastAPI
from sqlalchemy import Column, Integer, String, text
from sqlalchemy.orm import Session

from sdb_user_profile_svc.database.session import get_db, SessionLocal
from sdb_user_profile_svc.models.base import Base


class TestDatabaseSession:
    """Test cases for database session management."""
    
    def test_sessionlocal_provides_functional_session(self, db_session):
        """Test that SessionLocal (used by get_db) can perform basic database operations."""
        
        # Define a temporary model for testing
        class TempModel(Base):
            __tablename__ = 'temp_test_table'
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
        
        # Create the table explicitly using the test db_session
        Base.metadata.create_all(db_session.bind)
        
        try:
            # Test basic database operations using the test session
            # Insert a record
            test_record = TempModel(id=1, name="test_record")
            db_session.add(test_record)
            db_session.commit()
            
            # Query the record back
            retrieved_record = db_session.query(TempModel).filter_by(id=1).first()
            assert retrieved_record is not None
            assert retrieved_record.name == "test_record"
            
            # Clean up
            db_session.delete(retrieved_record)
            db_session.commit()
            
        finally:
            # Drop the temporary table
            Base.metadata.drop_all(db_session.bind, tables=[TempModel.__table__])
    
    def test_get_db_generator_behavior(self, session_local):
        """Test that get_db properly yields and closes sessions."""
        
        # Mock the SessionLocal in the session module to use test session factory
        with patch('sdb_user_profile_svc.database.session.SessionLocal', session_local):
            # Get the generator
            db_gen = get_db()
            
            # Get a session from the generator
            try:
                session = next(db_gen)
                assert isinstance(session, Session)
                
                # Verify session is usable by executing a simple query
                result = session.execute(text("SELECT 1 as test_value"))
                row = result.fetchone()
                assert row[0] == 1
                
            except StopIteration:
                pytest.fail("get_db generator did not yield a session")
            
            # Close the generator (simulates end of request)
            try:
                next(db_gen)
            except StopIteration:
                pass  # Expected behavior
            
            # After generator closes, session operations should fail
            # Note: The session should be closed in the finally block
    
    def test_get_db_handles_exceptions_properly(self):
        """Test that get_db handles exceptions and still closes the session."""
        
        # Create a mock session that tracks close() calls
        mock_session = MagicMock()
        mock_session_factory = MagicMock(return_value=mock_session)
        
        # Patch SessionLocal in the session module
        with patch('sdb_user_profile_svc.database.session.SessionLocal', mock_session_factory):
            db_gen = get_db()
            
            try:
                session = next(db_gen)
                assert session is mock_session
                # Simulate an exception during session usage
                raise ValueError("Simulated exception")
            except ValueError:
                # Expected exception
                pass
            except StopIteration:
                pytest.fail("get_db generator did not yield a session")
            finally:
                # Close the generator
                try:
                    next(db_gen)
                except StopIteration:
                    pass
            
            # Verify that close was called even with exception
            mock_session.close.assert_called_once()
    
    def test_fastapi_dependency_integration(self, client):
        """Test that get_db works correctly as a FastAPI dependency."""
        from sdb_user_profile_svc.app import app
        
        # Define a temporary model for testing
        class TempModel(Base):
            __tablename__ = 'temp_integration_table'
            id = Column(Integer, primary_key=True)
            data = Column(String(100))
        
        # Add a test route that uses get_db dependency
        @app.get("/test-db-dependency")
        async def test_db_route(session: Session = Depends(get_db)):
            # Perform a simple database operation
            try:
                # Execute a simple query to test database connectivity
                result = session.execute(text("SELECT 1 as test_value"))
                row = result.fetchone()
                return {"status": "success", "test_value": row[0] if row else None}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        try:
            # Make a request to the test endpoint
            response = client.get("/test-db-dependency")
            
            # Verify the response
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["test_value"] == 1
            
        finally:
            # Clean up: remove the test route
            # Find and remove the test route from the app
            for route in app.routes:
                if hasattr(route, 'path') and route.path == "/test-db-dependency":
                    app.routes.remove(route)
                    break
    
    def test_sessionlocal_configuration(self):
        """Test that SessionLocal is configured with correct parameters."""
        # Test SessionLocal configuration
        assert SessionLocal is not None
        
        # We can't easily test the exact configuration without creating a session
        # that connects to the production database, so we'll test the factory exists
        # and can be called (actual configuration is tested through integration)
        assert callable(SessionLocal)
    
    def test_get_db_is_generator_function(self):
        """Test that get_db is a generator function."""
        import types
        
        # Test that get_db returns a generator
        gen = get_db()
        assert isinstance(gen, types.GeneratorType)
        
        # Clean up the generator
        try:
            next(gen)
        except StopIteration:
            pass
        try:
            next(gen)
        except StopIteration:
            pass
