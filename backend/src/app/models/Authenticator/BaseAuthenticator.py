from abc import ABC, abstractmethod
from typing import Dict, Type

class BaseAuthenticator(ABC):
    def __init__(self, db):
        self.db = db
    
    # What are the methods that need to be performed here: 

    # Generating Session Token using JWT 
    
    def create_session_token():
        """
        inputs: User_Id, AuthenticatorType, expiry Time
        outputs: JWT Session Token
        """


    def decode_session_token():
        """
        inputs: JWT Session Token 
        outputs: User Id, Authenticator Type, expiry Time
        """


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

    # We also have the issue of figuring out main Authenticator (TODO)
    @abstractmethod
    def authenticate(self):
        pass
