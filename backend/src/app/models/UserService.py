from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime, timedelta
from fastapi import HTTPException
import requests

from app.db.models import User as UserDB

class UserService:
    def __init__(self, db: Session, email:str):
        self.db = db
        user_model = UserDB(
            email=email
        )
        self.db.add(user_model)
        self.db.commit()
        self.db.refresh(user_model)
        self._load_from_model(user_model)

    def get_by_id(self, user_id: str) -> 'UserService':
        """Get user by ID"""
        user_model = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if user_model:
            self._load_from_model(user_model)
            return self
        return None
    
    def get_by_email(self, email: str) -> 'UserService':
        """Get user by email"""
        user_model = self.db.query(UserDB).filter(UserDB.email == email).first()
        if user_model:
            self._load_from_model(user_model)
            return self
        return None

    def _load_from_model(self, user_model: UserDB) -> None:
        """Load user model data into class instance"""
        self.id = user_model.id
        self.email = user_model.email

    def to_dict(self) -> Dict:
        """Convert user instance to dictionary"""
        return {
            "id": self.id,
            "email": self.email
        } 