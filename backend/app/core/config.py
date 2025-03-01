import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your_google_client_id")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your_google_client_secret")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "your_redirect_uri")
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
