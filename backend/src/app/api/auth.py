from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
import requests
import os
import httpx
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
import json

from app.db.database import get_db
from app.db.models import User as UserDB
from app.models.schemas import OAuthCode
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
async def auth_callback(code: str = None, state: str = None, db: Session = Depends(get_db)):
    """
    - Identify user from the authorization code provided
        1. If exists update the Token table with new access token and refresh token 
        2. If not, create a new user and then add in the access and corresponding refresh token to the token table in the DB
    - Generate a session token for the user and pass it back through a redirect
    - Redirect to the URL with the session stored in the query parameter 
    """
    # Check if the authorization code was provided
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code."
        )

    # Parse state parameter if provided
    redirect_url = "/"
    if state:
        try:
            state_dict = json.loads(state)
            redirect_url = state_dict.get('siteredirect', '/')
        except json.JSONDecodeError:
            # If state is invalid, use default redirect
            pass

    # Exchange code for tokens
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
            detail=f"Failed to obtain token from Google: {response.text}"
        )
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    
    # Get user info from Google
    user_info = get_google_user_info(access_token)
    print("check if access token is obtainining user info : \n", user_info)
    # Check if user exists in database
    from datetime import datetime
    from app.db.models import User, Token
    
    # Query for existing user by email
    existing_user = db.query(User).filter(User.email == user_info["email"]).first()
    print("check if User email is being queries properly in the database : \n", existing_user)
    
    if existing_user:
        # User exists, update tokens
        user_id = existing_user.id
        print("check if existing user is being queried in the database : \n", existing_user)
        # Check if token exists
        existing_token = db.query(Token).filter(Token.user_id == user_id).first()
        
        if existing_token:
            # Update existing token
            existing_token.access_token = access_token
            existing_token.refresh_token = refresh_token
            existing_token.created_at = datetime.utcnow().isoformat()
        else:
            # Create new token
            new_token = Token(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                token_authenticator="google",
                created_at=datetime.utcnow().isoformat()
            )
            print("Issue new tokens to the existing user: \n", new_token)
            db.add(new_token)
    else:
        # Create new user
        new_user = User(
            email=user_info["email"],
            username=user_info.get("name", user_info["email"].split("@")[0]),
            created_at=datetime.utcnow().isoformat()
        )
        print("check if a new User is being created in the database : \n", new_user)
        db.add(new_user)
        db.flush()  # Flush to get the new user ID
        
        # Create token for new user
        new_token = Token(
            user_id=new_user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            token_authenticator="google",
            created_at=datetime.utcnow().isoformat()
        )
        print("check if a Token is being issued to newly created user in the database : \n", new_user)
        db.add(new_token)
        user_id = new_user.id
    
    # Commit changes to database
    db.commit()
    
    # Create session token
    session_token = create_session_token(str(user_id))
    
    # Redirect to frontend with session token
    redirect_with_token = f"{redirect_url}?token={session_token}"

    print("check if redirect path is correct:", redirect_with_token)
    
    return RedirectResponse(url=redirect_with_token)

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
        user = UserDB(db).get_by_id(user_id)
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