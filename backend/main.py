from fastapi import FastAPI
from auth import router as auth_router
from drive import router as drive_router

app = FastAPI()

# Include authentication and Google Drive routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(drive_router, prefix="/drive", tags=["Google Drive"])

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI Google OAuth Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
