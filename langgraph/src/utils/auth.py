# import os
# import pickle
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build

# # Scopes to access Google Sheets and Drive
# SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# def authenticate_google():
#     creds = None
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)
    
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
        
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)

#     return build('sheets', 'v4', credentials=creds), build('drive', 'v3', credentials=creds)

# def list_sheets(drive_service):
#     results = drive_service.files().list(
#         q="mimeType='application/vnd.google-apps.spreadsheet'",
#         pageSize=10,
#         fields="nextPageToken, files(id, name)"
#     ).execute()
#     sheets = results.get('files', [])
    
#     if not sheets:
#         print("No Google Sheets found.")
#     else:
#         print("Sheets:")
#         for sheet in sheets:
#             print(f"{sheet['name']} (ID: {sheet['id']})")
    
#     return sheets
