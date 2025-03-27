import os
import json
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def main():
    # 1) Grab environment variables
    creds_json = os.environ.get("GDRIVE_SERVICE_ACCOUNT_JSON")
    folder_id = os.environ.get("GDRIVE_FOLDER_ID")
    if not creds_json or not folder_id:
        print("❌ Missing GDRIVE_SERVICE_ACCOUNT_JSON or GDRIVE_FOLDER_ID")
        sys.exit(1)

    # 2) Load the credentials
    creds_info = json.loads(creds_json)
    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_info(creds_info, scopes=scopes)

    # 3) Build the Drive client
    drive_service = build("drive", "v3", credentials=creds)

    # 4) The local file you want to upload
    local_csv = "bi_solar_dashboard_final_csv.csv"

    # 5) Check if file already exists in that folder (by name)
    query = f"name='{local_csv}' and '{folder_id}' in parents and trashed=false"
    resp = drive_service.files().list(q=query, fields="files(id)").execute()
    files = resp.get("files", [])

    media_body = MediaFileUpload(local_csv, mimetype="text/csv")

    if files:
        # Overwrite the existing file
        file_id = files[0]["id"]
        drive_service.files().update(fileId=file_id, media_body=media_body).execute()
        print(f"✅ Overwrote existing '{local_csv}' in folder {folder_id}")
    else:
        # Upload new file
        file_metadata = {
            "name": local_csv,
            "parents": [folder_id],
        }
        drive_service.files().create(
            body=file_metadata,
            media_body=media_body
        ).execute()
        print(f"✅ Uploaded new '{local_csv}' to folder {folder_id}")

if __name__ == "__main__":
    main()
