import os
import importlib
import pytest
from pathlib import Path


class TestPackageStructure:
    """Test the foundational package structure for user profile service."""
    
    def test_directories_and_init_files_exist(self):
        """Test that required directories exist and contain __init__.py files."""
        base_path = Path("src/sdb_user_profile_svc")
        required_packages = ["database", "schemas", "models", "alembic"]
        
        for package in required_packages:
            package_dir = base_path / package
            init_file = package_dir / "__init__.py"
            
            # Assert directory exists and is a directory
            assert package_dir.exists(), f"Directory {package_dir} does not exist"
            assert package_dir.is_dir(), f"{package_dir} is not a directory"
            
            # Assert __init__.py exists in the directory
            assert init_file.exists(), f"__init__.py file does not exist in {package_dir}"
            assert init_file.is_file(), f"__init__.py in {package_dir} is not a file"
    
    def test_import_packages(self):
        """Test that all required packages can be imported without errors."""
        packages_to_import = [
            "sdb_user_profile_svc.database",
            "sdb_user_profile_svc.schemas",
            "sdb_user_profile_svc.alembic",
            "sdb_user_profile_svc.models"  # preexisting
        ]
        
        for package_name in packages_to_import:
            try:
                module = importlib.import_module(package_name)
                assert module is not None, f"Failed to import {package_name}"
            except ImportError as e:
                pytest.fail(f"Failed to import {package_name}: {e}")
    
    def test_env_example_exists_and_contains_examples(self):
        """Test that .env.example exists at repo root and contains environment variable examples."""
        env_example_path = Path(".env.example")
        
        # Assert .env.example exists and is a file
        assert env_example_path.exists(), ".env.example file does not exist at repo root"
        assert env_example_path.is_file(), ".env.example is not a file"
        
        # Read and verify content
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        # Assert file contains expected environment variable examples
        assert "DATABASE_URL=" in content, ".env.example should contain DATABASE_URL example"
        assert "postgresql://" in content, ".env.example should contain PostgreSQL example"
        assert "sqlite:///" in content, ".env.example should contain SQLite file example"
        assert "sqlite:///:memory:" in content, ".env.example should contain SQLite memory example"
        assert "SERVICE_PORT=" in content, ".env.example should contain SERVICE_PORT example"
        
        # Assert file is not empty
        assert len(content.strip()) > 0, ".env.example should not be empty"
