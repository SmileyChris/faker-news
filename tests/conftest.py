"""Pytest configuration and shared fixtures."""
import os

import pytest


@pytest.fixture(autouse=True)
def clear_env_vars():
    """Clear API key environment variables for each test."""
    env_vars = ["OPENAI_API_KEY", "DASHSCOPE_API_KEY", "OPENAI_BASE_URL", "DASHSCOPE_BASE_URL"]

    # Save original values
    original = {key: os.environ.get(key) for key in env_vars}

    # Clear them
    for key in env_vars:
        os.environ.pop(key, None)

    yield

    # Restore original values
    for key, value in original.items():
        if value is not None:
            os.environ[key] = value
        else:
            os.environ.pop(key, None)
