import os
from typing import List

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


class GoogleAPIClient(object):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        project_id: str,
        scopes: List[str],
        redirect_uri: str,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.project_id = project_id
        self.scopes = scopes
        self.redirect_uri = redirect_uri

        credentials = {
            'web': {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'project_id': self.project_id,
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token',
            }
        }

        self.flow = Flow.from_client_config(
            credentials,
            scopes=self.scopes,
            redirect_uri=self.redirect_uri,
        )

    def get_oauth_authorization_url(self) -> str:
        url, state = self.flow.authorization_url(
            access_type='offline', include_granted_scopes='false', prompt='consent'
        )
        return url

    def get_oauth_credentials(self, code):
        self.flow.fetch_token(code=code)
        creds = self.flow.credentials

        return {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'scopes': self.scopes,
        }

    def get_user_profile(self, token, refresh_token):
        creds = Credentials.from_authorized_user_info(
            {
                'token': token,
                'scopes': self.scopes,
                'refresh_token': refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            }
        )

        user_info_service = build('oauth2', 'v2', credentials=creds)
        user_info = user_info_service.userinfo().get().execute()

        return user_info

    def add_calendar_event(self, token, refresh_token, calendar_id, event):
        creds = Credentials.from_authorized_user_info(
            {
                'token': token,
                'scopes': self.scopes,
                'refresh_token': refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            }
        )

        calendar_service = build('calendar', 'v3', credentials=creds)
        event = (
            calendar_service.events()
            .insert(calendarId=calendar_id, body=event)
            .execute()
        )
        return event
