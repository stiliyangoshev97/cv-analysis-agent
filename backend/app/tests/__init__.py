"""Test suite for CV Screening Agent backend.

This package contains unit and integration tests for all backend features.

Test Structure:
    - unit/: Fast, isolated tests with mocked dependencies
    - integration/: API endpoint tests with test database

Running Tests:
    # Run all tests
    pytest
    
    # Run with coverage
    pytest --cov=app --cov-report=html
    
    # Run only unit tests
    pytest app/tests/unit -v
    
    # Run only integration tests
    pytest app/tests/integration -v
    
    # Run specific marker
    pytest -m auth -v
    pytest -m cv -v
    pytest -m profile -v

Markers:
    - unit: Unit tests (fast, mocked)
    - integration: Integration tests (real database)
    - auth: Authentication tests
    - cv: CV feature tests
    - chat: Chat feature tests
    - profile: Profile feature tests
    - notification: Notification feature tests
    - slow: Slow tests (skipped by default)
"""
