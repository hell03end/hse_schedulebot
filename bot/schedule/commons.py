from bot.models import Lessons, Users
from bot.logger import log
import logging


@log
def get_lessons(uid: int) -> (object, None):
    try:
        print(Lessons.get(Lessons.id == Users.get(Users.telegram_id == uid).lessons.id))
        return Users.get(Users.telegram_id == uid).lessons
    except BaseException as excinfo:
        logging.warning(excinfo)
