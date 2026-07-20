"""Early pytest plugin: pin the test run to SQLite + DEBUG.

Loaded via ``-p pytest_env_setup`` (see pytest.ini) so these env vars are set
*before* pytest-django imports the settings module — earlier than any
conftest.py. Keeps the suite off MySQL and lets the password-reset endpoint
surface the DEBUG-only uid/token that the reset tests consume.
"""
import os

os.environ.setdefault("DB_ENGINE", "sqlite")
os.environ.setdefault("DJANGO_DEBUG", "1")
