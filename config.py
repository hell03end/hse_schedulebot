import os


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

ADMIN_ID = 42928638
ADMINS = (ADMIN_ID)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
