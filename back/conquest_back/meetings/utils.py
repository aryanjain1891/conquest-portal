import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz
import uuid
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        '/home/app/web/meetings/credentials.json', scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
    return service


def create_google_meet_event(event_summary, start_time, end_time):
    service = get_calendar_service()
    print(start_time.isoformat())

    event = {
        'summary': event_summary,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        # 'conferenceData': {
        #     'createRequest': {
        #         'requestId': str(uuid.uuid4()),
        #         'conferenceSolutionKey': {
        #             'type': 'hangoutsMeet'
        #         }
        #     }
        # },
    }

    try:
        event = service.events().insert(
            calendarId='88bd99c6f35ca0064d75b5c26cbc151c39154c6b58c1c7036c1909f9da62cd72@group.calendar.google.com',
            body=event,
            conferenceDataVersion=1,
            # sendUpdates='all'
        ).execute()

        return event.get('hangoutLink')

    except HttpError as error:
        print(f'Error creating Google Meet event: {error.content}')
        return None

