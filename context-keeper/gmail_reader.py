from googleapiclient.discovery import build
from auth import get_credentials

def get_unread_emails(max_results=5):
    """Fetches subject lines and snippets from unread emails in Gmail."""
    creds = get_credentials()
    if not creds:
        return []
        
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Call the Gmail API
        results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        unread_emails = []
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['Subject', 'From']).execute()
            headers = msg_data.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            snippet = msg_data.get('snippet', '')
            
            unread_emails.append({
                'subject': subject,
                'from': sender,
                'snippet': snippet
            })
            
        return unread_emails
    except Exception as e:
        print(f"Error fetching Gmail: {e}")
        return []
