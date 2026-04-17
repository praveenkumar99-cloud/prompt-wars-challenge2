import datetime
from googleapiclient.discovery import build
from auth import get_credentials

def get_today_events():
    """Fetches today's events from Google Calendar."""
    creds = get_credentials()
    if not creds:
        return []
        
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Get start/end of today in UTC
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        tonight = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat() + 'Z'
        
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              timeMax=tonight, maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        return events_result.get('items', [])
    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        return []

def create_draft_event(summary, description, date_str=None):
    """Creates a draft event on Google Calendar based on summary instructions."""
    creds = get_credentials()
    if not creds:
        return None
        
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        if not date_str:
            # Default to tomorrow
            dt = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        else:
            # Simplistic parsing or use tomorrow if parsing fails
            dt = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            
        start_time = dt.isoformat() + 'Z'
        end_time = (dt + datetime.timedelta(hours=1)).isoformat() + 'Z'
        
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
        }
        
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return created_event
    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return None
