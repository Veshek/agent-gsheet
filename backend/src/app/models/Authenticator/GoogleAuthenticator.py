from app.models.Authenticator.BaseAuthenticator import BaseAuthenticator

class GoogleAuthenticator(BaseAuthenticator):
    def authenticate(self):
        return "Google Authentication"

    def exchange_code_for_token():
        """
        inputs: authcode,
        ouput: access token, user ? , user-email ? 
        """
        pass

    def get_accessToken_from_refreshToken():
        """
        inputs: user ? 
        output: access token
        """
        pass