import logging

from bot.utils import log
from models import Lessons, Users


@log
def get_lessons(uid: int) -> (object, None):
    try:
        return (Lessons.select().join(Users)
                .where(Users.telegram_id == uid).get())
    except BaseException as exc:
        logging.warning(exc)
