from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
import requests
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

router = APIRouter()

# Google OAuth Endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# OAuth 2.0 Scopes (including Google Drive access)
SCOPES = "openid email profile https://www.googleapis.com/auth/drive.readonly"

@router.get("/login")
def login():
    """
    Redirects the user to Google's OAuth 2.0 login page.
    """
    print(GOOGLE_REDIRECT_URI)
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = f"{GOOGLE_AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    return RedirectResponse(auth_url) #NOTE: seems to be a function that redirects to another url 

@router.get("/callback")
def auth_callback(code: str):
    """
    Handles Google's OAuth 2.0 callback and exchanges the auth code for an access token.
    """
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    token_info = response.json()

    if "access_token" not in token_info:
        raise HTTPException(status_code=400, detail="Failed to fetch access token")

    # Fetch user info
    user_info_response = requests.get(GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {token_info['access_token']}"})
    user_info = user_info_response.json()

    return {
        "message": "Authentication successful",
        "user": user_info,
        "tokens": token_info  # NOTE: These tokens are access tokens that google provides that validate that the user is in fact authenticated in the system
    }
