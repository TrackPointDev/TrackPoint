import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from secret_manager import access_secret_version_json

cache = {}

base_dir = os.path.dirname(__file__)
cred_path = os.path.join(base_dir, 'credentials.json')


def authenticate_service():
    project_id = "trackpointdb"
    secret_id = "credentials_json"
    version_id = "latest"
    credentials_json = access_secret_version_json(project_id, secret_id, version_id)

    """Authenticate the service account with Google Sheets API.
    See docs: https://developers.google.com/sheets/api/quickstart/python"""

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly"
    ]

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                credentials_json, scopes
            )
            creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())

    return creds
