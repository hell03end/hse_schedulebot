from datetime import datetime

from bot.logger import log
from bot.schedule.commons import get_lessons
from bot.service.common_handlers import send_cancel
from bot.utils.functions import is_cancelled, typing
from bot.utils.messages import MESSAGES
from bot.utils.schema import DAY_MAPPING
from telegram import ParseMode
from telegram.bot import Bot
from telegram.update import Update

MESSAGES = MESSAGES['schedule:day']


@log
@typing
def on_day(bot: Bot, update: Update, next_day: bool=False) -> (int, None):
    uid = update.message.from_user.id
    chat_id = update.message.chat.id
    message = update.message.text

    if is_cancelled(message):
        return send_cancel(bot, uid)

    lessons = get_lessons(uid)
    if not lessons:
        bot.send_message(chat_id, MESSAGES['on_day:empty'], ParseMode.HTML)
        return
    schedule = dict(zip(DAY_MAPPING, [lessons.monday, lessons.tuesday,
                                      lessons.wednesday, lessons.thursday,
                                      lessons.friday, lessons.saturday]))
    day = (datetime.now().weekday() + int(next_day)) % 7
    try:
        text = schedule[DAY_MAPPING[day]]
    except IndexError:
        text = MESSAGES['on_day:sunday']
    bot.send_message(chat_id, text, ParseMode.HTML)


@log
def on_tomorrow(bot: Bot, update: Update) -> None:
    return on_day(bot, update, next_day=True)
