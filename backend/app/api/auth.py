from fastapi import APIRouter, HTTPException
import requests
from app.core.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, GOOGLE_TOKEN_URL
from app.models.schemas import OAuthCode, RefreshTokenRequest

router = APIRouter()

@router.post("/google", summary="Exchange Google OAuth code for tokens")
def google_auth(oauth_code: OAuthCode):
    """
    Accepts a Google authorization code and exchanges it for access and refresh tokens.
    """
    payload = {
        "code": oauth_code.code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to obtain token from Google")
    return response.json()

@router.post("/google/refresh", summary="Refresh Google OAuth token")
def refresh_token(refresh_request: RefreshTokenRequest):
    """
    Accepts a refresh token and uses it to obtain a new access token from Google.
    """
    payload = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": refresh_request.refresh_token,
        "grant_type": "refresh_token"
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to refresh token")
    return response.json()
