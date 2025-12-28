"""Test configuration and fixtures."""

import pytest


@pytest.fixture
def sample_file_content():
    """Sample file content for tests."""
    return "Hello, World!\nThis is a test file.\n"


@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for tests."""
    return tmp_path
