from logging import getLogger
from typing import Sequence

import requests

logger = getLogger('plunk')


class PlunkClient:
    BASE_URL: str = 'https://api.useplunk.com'
    SEND_EMAIL_URL = f'{BASE_URL}/v1/send'
    key: str
    log_only: bool

    def __init__(self, key: str, log_only: bool):
        self.key = key
        self.log_only = log_only

        if self.log_only:
            logger.info('Plunk client initialized in log only mode')

    def send_email(self, receipients: Sequence[str], subject: str, message: str):
        data = {
            'to': receipients,
            'subject': subject,
            'body': message,
        }

        if self.log_only:
            logger.info(message)
        else:
            response = requests.post(
                self.SEND_EMAIL_URL,
                headers={'Authorization': f'Bearer {self.key}'},
                json=data,
            )

            return response.json()['success']
