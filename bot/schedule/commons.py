from bot.models import Lessons, Users
from bot.logger import log


@log
def get_lessons(uid: int) -> (object, None):
    try:
        return Lessons.select().join(Users).where(
            Users.telegram_id == uid).get()
    except BaseException as excinfo:
        print(excinfo)
        return None
