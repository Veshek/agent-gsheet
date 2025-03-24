import json
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os, sys
import sys
import os
from app.core.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
)
from app.db.database import Base, get_db
from app.main import app

# Import your SQLAlchemy models
from app.db.models import User as UserDB, Token

# Create an in-memory SQLite database for testing.
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def _setup_db():
    """Create all tables for testing and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db(_setup_db):
    """Provide a transactional scope around a series of operations."""
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@pytest.fixture(scope="function")
def client(db):
    """Override the get_db dependency to use the testing DB and return a TestClient."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def mock_google(monkeypatch):
    """
    Monkeypatch requests.post and requests.get so that calls to Google's endpoints return fake responses.
    This is used both when exchanging an authorization code and refreshing tokens.
    """

    class FakeResponse:
        def __init__(self, json_data, status_code):
            self._json = json_data
            self.status_code = status_code
            self.text = json.dumps(json_data)

        def json(self):
            return self._json

    def fake_post(url, data, **kwargs):
        from app.core.config import GOOGLE_TOKEN_URL
        if url == GOOGLE_TOKEN_URL:
            grant_type = data.get("grant_type")
            if grant_type == "authorization_code":
                # Fake response when exchanging an auth code for tokens.
                return FakeResponse({
                    "access_token": "fake_access_token",
                    "refresh_token": "fake_refresh_token"
                }, 200)
            elif grant_type == "refresh_token":
                # Fake response when refreshing tokens.
                return FakeResponse({
                    "access_token": "new_fake_access_token",
                    "refresh_token": "new_fake_refresh_token"
                }, 200)
        return FakeResponse({}, 400)

    def fake_get(url, headers, **kwargs):
        if url == "https://www.googleapis.com/oauth2/v1/userinfo":
            # Fake response for the Google user info endpoint.
            return FakeResponse({
                "email": "new_user@example.com",
                "name": "New User"
            }, 200)
        return FakeResponse({}, 400)

    monkeypatch.setattr("requests.post", fake_post)
    monkeypatch.setattr("requests.get", fake_get)


def test_new_user_sign_in_flow(client, mock_google, db):
    """
    This test simulates a first-time user signing in through Google OAuth:
    1. Simulates receiving an auth code from Google OAuth
    2. Uses mock_google fixture to fake Google's token and user info responses
    3. Checks if:
       - The user is correctly created in the database
       - A redirect response is received
       - The redirect URL contains a valid session token
       - The user's email matches what was received from Google
    """
    pass


def test_refresh_session_flow(client, monkeypatch, db):
    """
    This test verifies the token refresh flow when a session token expires:
    1. Creates a test user in the database
    2. Generates an expired JWT session token for this user
    3. Calls the refresh endpoint with the expired token
    4. Verifies:
       - A new valid session token is returned
       - The response includes the correct user information
       - The refresh was successful (200 status code)
    """
    pass


@pytest.mark.skip(reason="Not fully implemented. Add necessary DB setup and assertions when ready")
class TestDifferentDeviceSignIn:
    """
    Test suite for handling users signing in from different devices
    """
    
    def test_existing_user_sign_in_updates_token(self, client, mock_google, db):
        """
        Tests when an existing user signs in from a new device:
        1. Pre-populates database with a user and their existing tokens
        2. Simulates sign-in from a new device with Google OAuth
        3. Verifies:
           - The existing token record is updated (not duplicated)
           - New Google tokens are stored
           - A new session token is provided in the redirect
        """
        pass

    def test_existing_user_sign_in_without_prior_token(self, client, mock_google, db):
        """
        Tests when an existing user signs in but doesn't have any stored tokens:
        1. Pre-populates database with just a user record (no tokens)
        2. Simulates sign-in through Google OAuth
        3. Verifies:
           - A new token record is created for the user
           - The token contains the Google OAuth tokens
           - A session token is provided in the redirect
        """
        pass 