import re
from datetime import datetime

from bot.models import Users
from tests.fixtures import CORRECT_EMAILS


def create_users():
    """ Create sample records in Users database """
    # add students to Users
    for idx, email in enumerate(CORRECT_EMAILS['students']):
        Users.create(telegram_id=idx, username=re.sub(r"@.*", r'', email),
                     email=email, dt=datetime.now(), city="moscow")
    # add lecturers to Users
    for idx, email in enumerate(CORRECT_EMAILS['lecturers']):
        Users.create(telegram_id=idx + len(CORRECT_EMAILS['students']),
                     username=re.sub(r"@.*", r'', email), email=email,
                     dt=datetime.now(), city="moscow", student=False)
