from bot.models import Lessons, Users
from bot.logger import log
import logging


@log
def get_lessons(uid: int) -> (object, None):
    try:
        print(Lessons.get(Users.get(telegram_id=uid).lessons.id == Lessons.id))
        return Lessons.get(Users.get(telegram_id=uid).lessons.id == Lessons.id)
    except BaseException as excinfo:
        logging.warning(excinfo)
