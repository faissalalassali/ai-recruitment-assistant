import os
import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    return build('gmail', 'v1', credentials=creds)

def search_and_download_cvs():
    service = get_gmail_service()
    
    output_dir = 'downloaded_cvs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Refined search query: must have an attachment, pdf/docx, and include job-related keywords
    # You can customize keywords like cv, resume, application, job, etc.
    query = 'has:attachment (filename:pdf OR filename:docx) (cv OR resume OR application OR job OR توظيف OR سيرة)'
    print(f"Searching for candidate emails with query:\n'{query}'...\n")
    
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No candidate emails found matching the criteria.')
        return

    print(f"Found {len(messages)} potential candidate email(s). Processing attachments...\n")

    for msg_info in messages:
        msg_id = msg_info['id']
        msg = service.users().messages().get(userId='me', id=msg_id).execute()
        
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        
        # Double check to skip invoices or receipts if any slip through
        if any(keyword in subject.lower() for keyword in ['invoice', 'receipt', 'charges', 'order', 'delivery', 'bill']):
            print(f"Skipping non-CV email based on subject: {subject}")
            continue

        print(f"Processing Email ID: {msg_id}")
        print(f"From: {sender}")
        print(f"Subject: {subject}")

        # Handle both single parts and multipart messages
        parts = [msg['payload']]
        if 'parts' in msg['payload']:
            parts = msg['payload']['parts']

        for part in parts:
            filename = part.get('filename')
            if not filename and 'parts' in part:
                # Handle nested multiparts if necessary
                pass
            
            if filename and (filename.endswith('.pdf') or filename.endswith('.docx')):
                attachment_id = part['body'].get('attachmentId')
                if attachment_id:
                    attachment = service.users().messages().attachments().get(
                        userId='me', messageId=msg_id, id=attachment_id
                    ).execute()
                    
                    file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                    
                    safe_filename = filename.replace('/', '_').replace('\\', '_')
                    file_path = os.path.join(output_dir, f"{msg_id}_{safe_filename}")
                    
                    with open(file_path, 'wb') as f:
                        f.write(file_data)
                    
                    print(f"-> Successfully downloaded CV: {safe_filename} and saved to {file_path}\n")

if __name__ == '__main__':
    search_and_download_cvs()