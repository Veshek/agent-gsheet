import json
from datetime import datetime, timedelta, timezone
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
from app.models.UserService import UserService
from app.models.Authenticator.BaseAuthenticator import BaseAuthenticator as baseAuth 
from app.models.ResourceType import ResourceType
from app.models.Factory import ResourceFactory as factory 

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
        Base.metadata.create_all(bind=engine)
        UserService.set_Session(db_session)
        yield db_session
    finally:
        db_session.close()
        Base.metadata.drop_all(bind=engine)


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

def test_session_token_encode_decode_valid(db):
    """
    Creates a session token taking in user as input, Authenticator Type, and expiry time.
    """
    user_id = 1  # Example user ID
    authenticator_type = ResourceType.GOOGLE  # Example authenticator type
    expiry_time = datetime.now(tz=timezone.utc) + timedelta(hours=1)  # Set expiry time to 1 hour from now
    authenticator = factory.create_authenticator(db,"google")
    print(expiry_time)
    print(type(expiry_time))
    # Create the session token
    token = authenticator.create_session_token(user_id, expiry_time)

    # Check that the token is not None
    assert token is not None

    # Optionally, you can decode the token to verify its contents
    decoded_data = baseAuth.decode_session_token(token)
    assert decoded_data['user_id'] == user_id
    assert decoded_data['authenticator_type'] == authenticator_type.value

def test_expired_session_token_encode_decode(db):
    """
    Creates a session token taking in user as input, Authenticator Type, and expiry time.
    """
    user_id = 1  # Example user ID
    authenticator_type = ResourceType.GOOGLE  # Example authenticator type
    expiry_time = datetime.now(tz=timezone.utc) + timedelta(hours=-1)  # Set expiry time to 1 hour from now
    authenticator = factory.create_authenticator(db,"google")
    print(expiry_time)
    print(type(expiry_time))
    # Create the session token
    token = authenticator.create_session_token(user_id, expiry_time)

    # Optionally, you can decode the token to verify its contents
    with pytest.raises(jwt.ExpiredSignatureError) as expired_token:
        baseAuth.decode_session_token(token)
    assert str(expired_token.value) == "Signature has expired"

def test_invalid_session_token_encode_decode(db):
    token= "invalid"
    with pytest.raises(jwt.InvalidTokenError) as invalid_token:
        baseAuth.decode_session_token(token)
    assert str(invalid_token.value) == "Not enough segments"

