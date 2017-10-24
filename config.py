import os


USERDATA_PATH = r"backup/userdata"
CONVERSATIONS_PATH = r"backup/conversations"

PG_CONN = {
    'host': 'localhost',
    'port': 5432,
    'user': os.environ.get("POSTGRES_USER"),
    'password': os.environ.get("POSTGRES_PASSWORD"),
    'autorollback': True
}

TOKENS = {
    'TEST': os.environ.get("API_KEY_TELEGRAM_SCHEDULE_BOT")
}

DIMA = 42928638
BOGDAN = 56631662

ADMINS = (BOGDAN, DIMA)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
