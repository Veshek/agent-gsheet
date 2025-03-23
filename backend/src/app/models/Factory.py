from Authenticator.GoogleAuthenticator import GoogleAuthenticator
from Authenticator.BaseAuthenticator import BaseAuthenticator
from resource import ResourceType
from typing import Type, Dict

class ResourceFactory:
    _authenticators: Dict[str, Type[BaseAuthenticator]] = {
        "google": GoogleAuthenticator,
    }
    
    @classmethod
    def create_authenticator(cls, auth_type: str, db) -> BaseAuthenticator:
        authenticator_class = cls._authenticators.get(auth_type.lower())
        if not authenticator_class:
            raise ValueError(f"Unknown authenticator type: {auth_type}")
        return authenticator_class(db)