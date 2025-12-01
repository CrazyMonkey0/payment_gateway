"""
Pytest configuration and shared fixtures for the payment_gateway project.

This module provides:
- Test database fixtures
- Mocking of Redis/external services for tests
- Custom Django settings override for testing
"""

import os
import pytest
from django.conf import settings
from django.test import override_settings


@pytest.fixture(scope='session')
def django_db_setup():
    """
    Override Django database settings for testing.
    
    In tests, we use SQLite in-memory database instead of production database.
    """
    settings.DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }


@pytest.fixture(scope='function')
def disable_ssl_redirect():
    """
    Fixture to disable SSL redirect in tests.
    
    Allows testing without HTTPS requirements.
    """
    return override_settings(
        SECURE_SSL_REDIRECT=False,
        SESSION_COOKIE_SECURE=False,
        CSRF_COOKIE_SECURE=False,
    )


@pytest.fixture(scope='session')
def django_session_settings():
    """
    Override session backend for testing.
    
    In tests, we use database-backed sessions instead of Redis
    to avoid dependency on running Redis service.
    """
    return override_settings(
        SESSION_ENGINE='django.contrib.sessions.backends.db',
        SECURE_SSL_REDIRECT=False,
        SESSION_COOKIE_SECURE=False,
        CSRF_COOKIE_SECURE=False,
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'unique-snowflake',
            }
        },
    )


@pytest.fixture(autouse=True)
def use_test_session_settings(django_session_settings):
    """
    Automatically apply test session settings to all tests.
    
    This fixture is auto-used to ensure all tests run with database sessions
    and in-memory cache instead of Redis, and with SSL redirect disabled.
    """
    with django_session_settings:
        yield

