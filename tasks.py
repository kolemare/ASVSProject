from invoke import task, Context
from cryptography.fernet import Fernet
import os


@task
def download(c):
    print("Starting download task...")
    if not isinstance(c, Context):
        print(f"Error: Expected Context, got {type(c)}")
        raise TypeError(f"Expected Context, got {type(c)}")
    print("Context verified.")
    google_drive_download()
    print("Download task completed.")


@task
def build(c):
    import subprocess
    print("Starting build task...")
    if not isinstance(c, Context):
        print(f"Error: Expected Context, got {type(c)}")
        raise TypeError(f"Expected Context, got {type(c)}")
    print("Context verified.")
    script_dir = os.path.dirname(os.path.realpath(__file__))
    compose_file = os.path.join(script_dir, 'docker-compose.yml')
    subprocess.run(['sudo', 'docker-compose', '-f', compose_file, 'build'], check=True)
    print("Docker images built successfully.")


def google_drive_download():
    print("Starting Google Drive download...")
    import os
    import io
    import zipfile
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    print("Importing modules completed.")
    script_dir = os.path.dirname(os.path.realpath(__file__))
    dataset_dir = os.path.join(script_dir, 'dataset')
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
    file_name = os.path.join(dataset_dir, 'weatherdata.zip')

    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    creds = None
    token_path = os.path.join(script_dir, 'token.json')
    credentials_path = os.path.join(script_dir, 'credentials.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    print("Authenticated successfully.")
    service = build('drive', 'v3', credentials=creds)

    file_id = '1RPQaeHixdGQ2_CmHxq4ierSqzlJMqnVz'
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False

    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")

    with open(file_name, 'wb') as f:
        fh.seek(0)
        f.write(fh.read())

    print("Extracting...")
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall(dataset_dir)

    os.remove(file_name)
    print("Extraction complete. The dataset is available in the 'dataset' folder.")