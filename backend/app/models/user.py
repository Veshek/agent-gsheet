from sqlalchemy.orm import Session
from typing import Optional, Dict
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
import requests

from app.db.models import User as UserModel
from app.core.config import (
    JWT_SECRET_KEY, 
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_TOKEN_URL,
    GOOGLE_REDIRECT_URI
)

class User:
    def __init__(self, db: Session):
        self.db = db
        self.id: Optional[str] = None
        self.email: Optional[str] = None
        self.google_access_token: Optional[str] = None
        self.google_refresh_token: Optional[str] = None

    def create(self, user_info: Dict, tokens: Dict) -> None:
        """Create a new user"""
        user_model = UserModel(
            id=user_info.get('id'),  # or generate a unique ID
            email=user_info['email'],
            google_access_token=tokens['access_token'],
            google_refresh_token=tokens.get('refresh_token')
        )
        self.db.add(user_model)
        self.db.commit()
        self.db.refresh(user_model)
        self._load_from_model(user_model)
    
    def create_session_token(self) -> str:
        """Create a JWT session token"""
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {"user_id": self.id, "exp": expire}
        return jwt.encode(data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    def get_by_id(self, user_id: str) -> Optional['User']:
        """Get user by ID"""
        user_model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if user_model:
            self._load_from_model(user_model)
            return self
        return None
    
    def get_by_email(self, email: str) -> Optional['User']:
        """Get user by email"""
        user_model = self.db.query(UserModel).filter(UserModel.email == email).first()
        if user_model:
            self._load_from_model(user_model)
            return self
        return None

    def handle_google_auth(self, auth_code: str) -> Dict:
        """Handle the complete Google OAuth flow"""
        # Exchange code for tokens
        tokens = self._exchange_google_code(auth_code)
        
        # Get user info from Google
        user_info = self._get_google_user_info(tokens['access_token'])
        
        # Create or update user
        self._handle_oauth_user(user_info, tokens)
        
        # Create session token
        session_token = self.create_session_token()
        
        return {
            "session_token": session_token,
            "user": self.to_dict()
        }

    def refresh_session(self, expired_token: str) -> Dict:
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
            if not self.get_by_id(user_id) or not self.google_refresh_token:
                raise HTTPException(status_code=401, detail="Invalid user or no refresh token")

            # Get new Google tokens
            new_tokens = self._refresh_google_token()
            
            # Update tokens in database
            self._update_tokens(new_tokens)
            
            # Create new session token
            session_token = self.create_session_token()
            
            return {
                "session_token": session_token,
                "user": self.to_dict()
            }

        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token format")

    def _exchange_google_code(self, auth_code: str) -> Dict:
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

    def _get_google_user_info(self, access_token: str) -> Dict:
        """Get user info from Google"""
        response = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Failed to get user info")
        return response.json()

    def _handle_oauth_user(self, user_info: Dict, tokens: Dict) -> None:
        """Create or update user with OAuth information"""
        existing_user = self.get_by_email(user_info['email'])
        
        if existing_user:
            self._update_tokens(tokens)
        else:
            self._create_new_user(user_info, tokens)


    def update_tokens(self, tokens: Dict) -> None:
        """Update user's OAuth tokens"""
        user_model = self.db.query(UserModel).filter(UserModel.id == self.id).first()
        if user_model:
            user_model.google_access_token = tokens['access_token']
            if 'refresh_token' in tokens:
                user_model.google_refresh_token = tokens['refresh_token']
            self.db.commit()
            self.db.refresh(user_model)
            self._load_from_model(user_model)

    def _refresh_google_token(self) -> Dict:
        """Refresh Google access token"""
        payload = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "refresh_token": self.google_refresh_token,
            "grant_type": "refresh_token"
        }
        response = requests.post(GOOGLE_TOKEN_URL, data=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Failed to refresh Google token")
        return response.json()

    def _load_from_model(self, user_model: UserModel) -> None:
        """Load user model data into class instance"""
        self.id = user_model.id
        self.email = user_model.email
        self.google_access_token = user_model.google_access_token
        self.google_refresh_token = user_model.google_refresh_token

    def to_dict(self) -> Dict:
        """Convert user instance to dictionary"""
        return {
            "id": self.id,
            "email": self.email
        } 