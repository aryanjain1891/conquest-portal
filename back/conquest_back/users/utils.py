from googleapiclient.discovery import build
from googleapiclient.http import  MediaFileUpload
from google.oauth2 import service_account
import base64,io
from PIL import Image

SCOPES = ["https://www.googleapis.com/auth/drive"]
PARENT_FOLDER_ID = "1VezkdzoMI-8N2N7onrsm32PEfqacgw7z"

def authenicate():
  creds = service_account.Credentials.from_service_account_file(r'/home/app/web/users/credentials.json',scopes=SCOPES)
  return creds

def upload_photo(data_url,username):
  creds = authenicate()
  service = build('drive', 'v3', credentials=creds)

  data_url_parts = data_url.split(',')
  encoded_data = data_url_parts[1]
  mimetype = data_url_parts[0].split(':')[1].split(';')[0]
  filename = f'{username}.{mimetype.split("/")[-1]}'  # Extract extension
  file_metadata = {'name': filename, 'mimeType': mimetype,'parents':[PARENT_FOLDER_ID]}

  img = Image.open(io.BytesIO(base64.decodebytes(bytes(encoded_data, "utf-8"))))
  img.save(f'{username}.{mimetype.split("/")[-1]}')
  img.close()

  media = MediaFileUpload(
        rf'/home/app/web/{username}.{mimetype.split("/")[-1]}', resumable=True
    )

  file = (service.files().create(body=file_metadata, media_body=media,fields="id").execute())
  print(file.get("id"))

  permission = service.permissions().create(fileId=file.get('id'), body={'role': 'reader', 'type': 'anyone'}).execute()
  link = service.files().get(
    fileId = file.get('id'),
    fields = 'webViewLink'
  ).execute()
  shareable_link = link.get("webViewLink")
  filename=f'{username}.{mimetype.split("/")[-1]}'
  return (shareable_link,filename)