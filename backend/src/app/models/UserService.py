from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime, timedelta
from fastapi import HTTPException
import requests

from app.db.models import User as UserDB

class UserService:
    db = None

    def __init__(self, id:str, created_at, username:str, email:str):
        self.id=id
        self.created_at = created_at
        self.username=username
        self.email=email

    @staticmethod
    def create_user(email:str,username:str):
        user_model = UserDB(
            email=email,
            username=username
        )
        UserService.db.add(user_model)
        UserService.db.commit()
        UserService.db.refresh(user_model)
        return UserService._load_from_model(user_model)

    @classmethod
    def get_by_id(cls, user_id: str) -> 'UserService':
        """Get user by ID"""
        user_model = cls.db.query(UserDB).filter(UserDB.id == user_id).first()
        if user_model:
            return cls._load_from_model(user_model)
        return None
    
    @classmethod
    def get_by_email(cls, email: str) -> 'UserService':
        """Get user by email"""
        user_model = cls.db.query(UserDB).filter(UserDB.email == email).first()
        if user_model:
            return cls._load_from_model(user_model)
        return None

    @classmethod
    def _load_from_model(cls, user_model: UserDB) -> 'UserService':
        """Load user model data into class instance"""
        return cls(user_model.id,user_model.created_at,user_model.username,user_model.email)

    def to_dict(self) -> Dict:
        """Convert user instance to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username
        } 

    @staticmethod
    def set_Session(db:Session):
        UserService.db = db 