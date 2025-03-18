import os
from dotenv import load_dotenv

def reload_env():
    # Clear relevant environment variables
    env_vars = [
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "GOOGLE_REDIRECT_URI",
        "JWT_SECRET_KEY",
        "JWT_ALGORITHM",
        "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
        "JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    ]
    
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]
    
    # Reload environment variables from .env
    load_dotenv(override=True)

# Initial load of environment variables
reload_env()

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your_google_client_id")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your_google_client_secret")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "your_redirect_uri")
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_secret_key_here")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 60))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", 7))