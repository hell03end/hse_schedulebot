""" Sample of configuration file """

import logging
import os


# ===== Logging =====
LOGGING_LEVEL = logging.DEBUG
logging.basicConfig(
    level=LOGGING_LEVEL,
    format="[%(asctime)s] %(levelname)s "
           "[%(name)s.{%(filename)s}.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S"
)

# ===== PSQL =====
PG_CONN = {
    'host': "localhost",
    'port': 5433,
    'user': os.environ.get("PSQL_USER", "postgres"),
    'password': os.environ.get("PSQL_PASS"),
    'autorollback': True
}

# ===== Telegram =====
TOKENS = {
    'TEST': os.environ.get("TEST_BOT_TOKEN"),
    'PROD': os.environ.get("PROD_BOT_TOKEN")
}
ADMINS = (42928638, 56631662)  # hell03end, evstratbg

# ===== Paths =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERDATA_PATH = os.path.join(BASE_DIR, "backup", "userdata")
CONVERSATIONS_PATH = os.path.join(BASE_DIR, "backup", "conversations")

# ===== Other =====
WORKERS_COUNT = 10
