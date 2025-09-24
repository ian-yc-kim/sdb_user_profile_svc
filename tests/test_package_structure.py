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
    
    def test_env_example_exists_and_empty(self):
        """Test that .env.example exists at repo root and is empty."""
        env_example_path = Path(".env.example")
        
        # Assert .env.example exists and is a file
        assert env_example_path.exists(), ".env.example file does not exist at repo root"
        assert env_example_path.is_file(), ".env.example is not a file"
        
        # Assert file is empty or contains only whitespace
        with open(env_example_path, 'r') as f:
            content = f.read().strip()
            assert content == "", ".env.example should be empty or contain only whitespace"
