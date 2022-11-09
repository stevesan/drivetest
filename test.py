
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# If you modify these scopes, delete token.json.
SCOPES = [
  'https://www.googleapis.com/auth/drive.readonly',
]

def download_to(service, file_id, local_destp):
  request = service.files().get_media(fileId=file_id)
  with open(local_destp, 'wb') as f:
    downloader = MediaIoBaseDownload(f, request)
    done = False
    while not done:
      status, done = downloader.next_chunk()
      print(f'Downloading @ {int(status.progress() * 100)}%')

def get_gapi_creds():
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

  # If there are no (valid) credentials available, let the user log in.
  # TODO also check that SCOPES == json['scopes']
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          'credentials.json', SCOPES)
      creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
      token.write(creds.to_json())
  return creds

def main():
  # Last part of the url
  folder_id = '1dwbYWBibR3VRiTr_V6Ed4dmr4fcg6krv'

  creds = get_gapi_creds()
  service = build('drive', 'v3', credentials=creds)
  results = service.files().list(
      q=f'"{folder_id}" in parents',
      fields="files(id, name)").execute()
  files = results.get('files', [])

  print(f'{len(files)} files:')
  for file in files:
      print(f'{file["name"]} id={file["id"]}')
      download_to(service, file['id'], file['name'])

if __name__ == '__main__':
    main()
