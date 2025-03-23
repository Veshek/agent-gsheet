from BaseAuthenticator import BaseAuthenticator

class GoogleAuthenticator(BaseAuthenticator):
    def authenticate(self):
        return "Google Authentication"