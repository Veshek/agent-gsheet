from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import auth
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # This will create the tables only if they don't exist
    yield

app = FastAPI(lifespan=lifespan)

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://zp1v56uxy8rdx5ypatb0ockcb9tr6a-oci3--5173--31ca1d38.local-credentialless.webcontainer-api.io"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the auth router with a prefix so all auth endpoints are under /auth
app.include_router(auth.router, prefix="/auth", tags=["auth"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
