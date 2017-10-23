from bot.logger import log
from bot.models import Lessons, Users
from bot.schedule.commons import get_lessons
from bot.service.common_handlers import send_cancel
from bot.utils.functions import is_back, is_cancelled, typing
from bot.utils.keyboards import SCHEDULE_KEYBOARD, WEEK_KEYBOARD
from bot.utils.messages import MESSAGES
from bot.utils.schema import DAY_MAPPING
from bot.utils.states import DAY_OF_WEEK, SCHEDULE
from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.bot import Bot
from telegram.ext import MessageHandler
from telegram.update import Update

MESSAGES = MESSAGES['schedule:week']


@log
@typing
def on_week(bot: Bot, update: Update) -> str:
    bot.send_message(
        update.message.from_user.id,
        MESSAGES['on_week:ask'],
        reply_markup=ReplyKeyboardMarkup(WEEK_KEYBOARD, True)
    )
    return DAY_OF_WEEK


@log
@typing
def choose_dow(bot: Bot, update: Update) -> (int, str):
    """ Send schedule for given Day Of Week (dow) """
    uid = update.message.from_user.id
    chat_id = update.message.chat.id
    message = update.message.text
    if is_cancelled(message):
        return send_cancel(bot, uid)
    elif is_back(message):
        bot.send_message(
            update.message.from_user.id,
            MESSAGES['choose_dow:back'],
            reply_markup=ReplyKeyboardMarkup(SCHEDULE_KEYBOARD, True)
        )
        return SCHEDULE

    lessons = get_lessons(uid)
    if not lessons:
        bot.send_message(uid, MESSAGES['on_week:empty'])
    else:
        send_params = {
            'text': MESSAGES['choose_dow:ask'],
            'chat_id': chat_id,
            # messages in db are in markdown, look for utils.shcema
            'parse_mode': ParseMode.MARKDOWN
        }
        schedule = dict(zip(DAY_MAPPING, [lessons.monday, lessons.tuesday,
                                          lessons.wednesday, lessons.thursday,
                                          lessons.friday, lessons.saturday]))
        send_params['text'] = schedule[message]
        bot.send_message(**send_params)
