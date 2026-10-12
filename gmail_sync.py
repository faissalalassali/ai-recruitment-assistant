import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Scopes required to read Gmail messages and attachments
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("Error: 'credentials.json' not found. Please place it in the project root directory.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return build('gmail', 'v1', credentials=creds)

def fetch_and_download_cvs(output_dir="downloaded_cvs"):
    service = authenticate_gmail()
    if not service:
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Search for messages with attachments and PDF/DOCX files
    query = "has:attachment filename:pdf"
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    if not messages:
        print("No emails with PDF attachments found.")
        return

    print(f"Found {len(messages)} messages. Processing attachments...")
    
    for msg in messages:
        msg_id = msg['id']
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        
        for part in message.get('payload', {}).get('parts', []):
            if part.get('filename'):
                filename = part['filename']
                if filename.lower().endswith(('.pdf', '.docx')):
                    if 'data' in part['body']:
                        data = part['body']['data']
                    else:
                        att_id = part['body'].get('attachmentId')
                        if att_id:
                            att = service.users().messages().attachments().get(
                                userId='me', messageId=msg_id, id=att_id
                            ).execute()
                            data = att['data']
                        else:
                            continue
                    
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                    file_path = os.path.join(output_dir, filename)
                    
                    with open(file_path, 'wb') as f:
                        f.write(file_data)
                    print(f"Downloaded CV: {filename}")

if __name__ == "__main__":
    fetch_and_download_cvs()