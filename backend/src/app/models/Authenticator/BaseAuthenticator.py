from abc import ABC, abstractmethod
from typing import Dict, Type
from app.models.ResourceType import ResourceType
from datetime import datetime, timedelta
import jwt

from app.core.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS,
)

class BaseAuthenticator(ABC):
    def __init__(self, db, resource_type: ResourceType = None):
        self.db = db
        self.resource_type = resource_type
    # What are the methods that need to be performed here: 

    # Generating Session Token using JWT 
    def create_session_token(self, user_id: int, expiry_time: datetime):
        """
        Inputs: User_Id, AuthenticatorType, expiry Time
        Outputs: JWT Session Token
        """
        # Prepare the payload for the JWT
        payload = {
            "user_id": user_id,
            "authenticator_type": self.resource_type.name,
            "exp": expiry_time  # Expiry time as a datetime object
        }
        
        # Create the JWT token
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token

    def decode_session_token(token: str):
        """
        inputs: JWT Session Token 
        outputs: User Id, Authenticator Type, expiry Time

        raises jwt.ExpiredSignatureError if the token is expired 
        raises jwt.InvalidTokeError if the token is invalid
        """
        # Decode the JWT token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return {
            "user_id": payload["user_id"],
            "authenticator_type": payload["authenticator_type"]
        }


    # Exchanging AuthCode for AccessToken
    # TODO -> override
    @abstractmethod
    def exchange_code_for_token():
        """
        inputs: authcode,
        ouput: access token, user ? , user-email ? 
        """

    # Getting new AccessTokens using Refresh Token
    # TODO -> override 
    @abstractmethod
    def get_accessToken_from_refreshToken():
        """
        inputs: user ? 
        output: access token
        """

