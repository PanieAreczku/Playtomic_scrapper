# padel_notifier/notification.py
import logging
import requests
from config import PUSHOVER_API_TOKEN

logger = logging.getLogger(__name__)

class PushoverClient:
    API_URL = 'https://api.pushover.net/1/messages.json'

    def __init__(self, user_key: str, api_token: str | None = None):
        self.user_key = user_key
        self.api_token = api_token or PUSHOVER_API_TOKEN

    def send(self, message: str, title: str = 'Court Availability') -> None:
        payload = {
            'token': self.api_token,
            'user': self.user_key,
            'message': message,
            'title': title,
        }
        resp = requests.post(self.API_URL, data=payload)
        if resp.ok:
            logger.info('Notification sent.')
        else:
            logger.error('Failed to send notification: %s - %s', resp.status_code, resp.text)