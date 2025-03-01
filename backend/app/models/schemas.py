from pydantic import BaseModel

class OAuthCode(BaseModel):
    code: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str
