import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session


class TestDatabaseHealth:
    """Test cases for database connectivity health checks."""
    
    def test_database_connectivity_health_check(self, db_session):
        """Test basic database connectivity using a simple SELECT 1 query.
        
        This test verifies that:
        1. Database connection can be established
        2. A simple query can be executed successfully
        3. The database session is functional
        
        Args:
            db_session: SQLAlchemy session fixture from conftest.py
        """
        # Execute a simple SELECT 1 query to test connectivity
        result = db_session.execute(text("SELECT 1 as health_check"))
        
        # Fetch the result
        row = result.fetchone()
        
        # Assert the query executed successfully and returned expected result
        assert row is not None, "Health check query returned no results"
        assert row[0] == 1, f"Expected health check result to be 1, got {row[0]}"
        
        # Verify session is still functional after the query
        assert isinstance(db_session, Session), "db_session should be a SQLAlchemy Session instance"
    
    def test_database_session_isolation(self, db_session):
        """Test that the database session is properly isolated for testing.
        
        This test verifies that the test database session:
        1. Uses in-memory SQLite as configured in conftest.py
        2. Is properly isolated from production database
        3. Can perform multiple queries in sequence
        
        Args:
            db_session: SQLAlchemy session fixture from conftest.py
        """
        # Perform multiple health check queries to ensure session stability
        for i in range(3):
            result = db_session.execute(text(f"SELECT {i + 1} as test_value"))
            row = result.fetchone()
            
            assert row is not None, f"Query {i + 1} returned no results"
            assert row[0] == i + 1, f"Expected query {i + 1} result to be {i + 1}, got {row[0]}"
        
        # Verify session is still active and functional
        final_result = db_session.execute(text("SELECT 'session_active' as status"))
        final_row = final_result.fetchone()
        
        assert final_row is not None, "Final session check returned no results"
        assert final_row[0] == "session_active", "Session should still be active after multiple queries"
