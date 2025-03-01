from fastapi import FastAPI
from app.api import auth

app = FastAPI()

# Include the auth router with a prefix so all auth endpoints are under /auth
app.include_router(auth.router, prefix="/auth", tags=["auth"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
