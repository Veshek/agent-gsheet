from fastapi import Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session
import jwt

from app.db.database import get_db
from app.models.UserService import UserService
from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM

async def get_current_user(websocket: WebSocket, db: Session = Depends(get_db)) -> UserService:
    """Dependency to get the current user from the session token in WebSocket headers."""
    # Accept the WebSocket connection
    await websocket.accept()

    # Extract the token from the headers
    token = websocket.headers.get("Authorization")  # Expecting "Bearer YOUR_TOKEN"

    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token not provided")

    token = token.split(" ")[1]  # Extract the token part

    try:
        # Decode the token to get the user ID
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Retrieve the user from the database
        user = db.query(UserService).filter(UserService.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")