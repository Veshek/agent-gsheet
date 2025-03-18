from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
import requests
import os
import httpx
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse

from app.db.database import get_db
from app.models.schemas import OAuthCode
from app.models.user import User
from app.core.config import (
    JWT_SECRET_KEY, 
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_TOKEN_URL,
    GOOGLE_REDIRECT_URI
)

router = APIRouter()

def create_session_token(user_id: str) -> str:
    """Create a JWT session token"""
    expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"user_id": user_id, "exp": expire}
    return jwt.encode(data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def exchange_google_code(auth_code: str) -> dict:
    """Exchange Google auth code for tokens"""
    payload = {
        "code": auth_code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=payload)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to obtain token from Google"
        )
    return response.json()

def get_google_user_info(access_token: str) -> dict:
    """Get user info from Google"""
    response = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Failed to get user info")
    return response.json()

def refresh_google_token(refresh_token: str) -> dict:
    """Refresh Google access token"""
    payload = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Failed to refresh Google token")
    return response.json()

@router.get("/google")
async def auth_callback(code: str = None, state: str = None):
    """
    TODO: 
    - Identify user from the authorization code provided
        1. If exists update the Token table with new access token and refresh token 
        2. If not, create a new user and then add in the access and corresponding refresh token to the token table in the DB
    - Generate a session token for the user and pass it back through a redirect, and store it in the header or 
    as a Cookie 
        1. How to decide which to do. We figure out the easiest and simplest way to store it, we want to move fast 
    Redirect to the URL with the session stored in the query parameter 

    - We can use the UserDB directly now to get it up and running and later if we create a service class then we 
    can think about making the classes. It will get quite defocussed to do that at this point

    """
    # Check if the authorization code was provided
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code."
        )

    payload = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    response = requests.post(GOOGLE_TOKEN_URL, data=payload)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to obtain token from Google : {response}"
        )

    return response.json()

@router.post("/refresh")
def refresh_session(expired_token: str, db: Session = Depends(get_db)):
    """Refresh session using stored Google refresh token"""
    try:
        # Decode expired token without verification
        payload = jwt.decode(
            expired_token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": False}
        )
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token format")

        # Get user and check refresh token
        user = User(db).get_by_id(user_id)
        if not user or not user.google_refresh_token:
            raise HTTPException(status_code=401, detail="Invalid user or no refresh token")

        # Get new Google tokens
        new_tokens = refresh_google_token(user.google_refresh_token)
        
        # Update user's tokens
        user.update_tokens(new_tokens)
        
        # Create new session token
        session_token = create_session_token(user.id)
        
        return {
            "session_token": session_token,
            "user": user.to_dict()
        }

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token format")