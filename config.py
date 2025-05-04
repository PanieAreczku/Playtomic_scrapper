# padel_notifier/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / '.env')

PUSHOVER_API_TOKEN: str = os.getenv('PUSHOVER_API_TOKEN', '')
PUSHOVER_USER_KEY:  str = os.getenv('PUSHOVER_USER_KEY', '')
TENANT_ID:          str = os.getenv('TENANT_ID', '')
TIMEZONE:           str = os.getenv('TIMEZONE', 'Europe/Warsaw')