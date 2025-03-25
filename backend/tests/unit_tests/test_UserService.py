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
from app.models.UserService import UserService

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

def test_create_user(db):
    """Test creating a user and check the database entry."""
    user_service = UserService.create_user(username="testuser", email="test@example.com")
    
    # Check if the user object is created correctly
    assert user_service.id is not None  # Check if ID is generated
    assert user_service.username == "testuser"
    assert user_service.email == "test@example.com"

    # Check the database for the new user entry
    user_in_db = db.query(UserDB).filter(UserDB.id == user_service.id).first()
    assert user_in_db is not None  # User should exist in the database
    assert user_in_db.username == "testuser"
    assert user_in_db.email == "test@example.com"

def test_get_by_id(db):
    """Test retrieving a user by ID and check the database entry."""
    new_user = UserDB(username="testuser", email="test@example.com")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    user = UserService.get_by_id(new_user.id)
    
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"

    # Check the database for the user entry
    user_in_db = db.query(UserDB).filter(UserDB.id == new_user.id).first()
    assert user_in_db is not None  # User should exist in the database
    assert user_in_db.username == "testuser"
    assert user_in_db.email == "test@example.com"

def test_get_user_by_email(db):
    """Test retrieving a user by email and check the database entry."""
    new_user = UserDB(username="testuser", email="test@example.com")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    user = UserService.get_by_email("test@example.com")
    
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"

    # Check the database for the user entry
    user_in_db = db.query(UserDB).filter(UserDB.email == "test@example.com").first()
    assert user_in_db is not None  # User should exist in the database
    assert user_in_db.username == "testuser"
    assert user_in_db.email == "test@example.com"

def test_get_user_by_id_not_exists(db):
    """Test retrieving a user by ID that does not exist."""
    user = db.query(UserDB).filter(UserDB.id == 9999).first()  # Assuming 9999 does not exist
    assert user is None  # Should return None if user does not exist

def test_get_user_by_email_not_exists(db):
    """Test retrieving a user by email that does not exist."""
    user = db.query(UserDB).filter(UserDB.email == "nonexistent@example.com").first()  # Assuming this email does not exist
    assert user is None  # Should return None if user does not exist