from app.models.Authenticator.GoogleAuthenticator import GoogleAuthenticator
from app.models.Authenticator.BaseAuthenticator import BaseAuthenticator
from app.models.ResourceType import ResourceType
from typing import Type, Dict

class ResourceFactory:

    _resource: Dict[str, Type[ResourceType]] = {
        "GOOGLE": ResourceType.GOOGLE,
    }

    _authenticators: Dict[Type[ResourceType], Type[BaseAuthenticator]] = {
        ResourceType.GOOGLE: GoogleAuthenticator,
    }
    
    @classmethod
    def create_authenticator(cls, db, auth_type: str) -> BaseAuthenticator:
        resource_type = cls._resource.get(auth_type.upper())
        authenticator_class = cls._authenticators.get(resource_type)
        if not authenticator_class:
            raise ValueError(f"Unknown authenticator type: {auth_type}")
        return authenticator_class(db, resource_type)