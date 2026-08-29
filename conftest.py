"""Pytest fixtures for the 4time backend.

The SQLite/DEBUG env pinning happens even earlier, in the ``pytest_env_setup``
plugin (loaded via ``-p`` in pytest.ini), because pytest-django imports the
settings module before any conftest.py is executed.
"""
import pytest


@pytest.fixture(autouse=True)
def _enable_db_and_reset_throttles(db):
    """Give every test DB access and a clean throttle/cache slate.

    Throttling (AnonRateThrottle / PasswordResetThrottle) is backed by the
    process-wide LocMemCache; clearing it per test keeps rate limits from
    bleeding across tests and causing spurious 429s.
    """
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()
