import os

from .plunk.client import PlunkClient

plunk_client = PlunkClient(
    os.getenv('PLUNK_KEY', ''), os.getenv('PLUNK_LOG_ONLY', 'False') == 'True'
)
