from typing import Sequence

import requests


class PlunkClient:
    BASE_URL: str = 'https://api.useplunk.com'
    SEND_EMAIL_URL = f'{BASE_URL}/v1/send'
    key: str

    def __init__(self, key: str):
        self.key = key

    def send_email(self, receipients: Sequence[str], subject: str, message: str):
        data = {
            'to': receipients,
            'subject': subject,
            'body': message,
        }

        response = requests.post(
            self.SEND_EMAIL_URL,
            headers={'Authorization': f'Bearer {self.key}'},
            json=data,
        )

        return response.json()['success']
