import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            
            flow.redirect_uri = 'http://localhost:8080/'
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            print("Please open the following link in your browser to sign in:")
            print("-" * 60)
            print(auth_url)
            print("-" * 60)
            
            code = input("Enter the authorization code here after granting permissions: ").strip()
            flow.fetch_token(code=code)
            creds = flow.credentials
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)

        results = service.users().messages().list(userId='me', maxResults=5).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No messages found.')
        else:
            print('Connected successfully! Found the following messages:')
            for message in messages:
                print(f"- Message ID: {message['id']}")

    except Exception as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()