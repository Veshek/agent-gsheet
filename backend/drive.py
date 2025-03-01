from fastapi import APIRouter, HTTPException
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

router = APIRouter()

@router.get("/files")
def list_drive_files(access_token: str):
    """
    Lists the user's Google Drive files using the provided access token.
    """
    if not access_token:
        raise HTTPException(status_code=400, detail="Access token is required")

    try:
        creds = Credentials(token=access_token)
        drive_service = build('drive', 'v3', credentials=creds)

        results = drive_service.files().list(pageSize=10, fields="files(id, name)").execute()
        files = results.get('files', [])

        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
