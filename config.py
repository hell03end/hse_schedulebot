""" Sample of configuration file """

import logging
import os

# from playhouse.pool import PostgresqlDatabase
from playhouse.pool import SqliteExtDatabase

LOG_LEVEL = logging.INFO
logging.basicConfig(
    level=LOG_LEVEL,
    format="[%(asctime)s] %(levelname)s "
           "[%(name)s.{%(filename)s}.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S"
)

# db = PostgresqlDatabase(
#     database="hse_schedule_db",
#     host="localhost",
#     port=5432,
#     user=os.environ.get("PSQL_USER", "postgres"),
#     password=os.environ.get("PSQL_PASS", "pass123"),
#     autorollback=True
# )

db = SqliteExtDatabase(
    database="test.db",  # :memory:
    pragmas=(
        ('journal_mode', 'wal'),  # Use WAL-mode (you should always use this!).
        ('foreign_keys', 1)  # Enforce foreign-key constraints.
    )
)

TOKEN = r"433401213:AAF7rVohQzqUaDngq_oUPvn16FYLjXchc_I"
ADMINS = (42928638, 56631662)  # hell03end, evstratbg

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERDATA_PATH = os.path.join(BASE_DIR, "backup", "userdata")
HISTORY_PATH = os.path.join(BASE_DIR, "backup", "conversations")
