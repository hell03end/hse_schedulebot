from bot.models import Lessons, Users
from bot.logger import log
import logging


@log
def get_lessons(uid: int) -> (object, None):
    try:
        return Lessons.select().join(Users).where(
            Users.telegram_id == uid).get()
    except BaseException as excinfo:
        logging.warning(excinfo)
