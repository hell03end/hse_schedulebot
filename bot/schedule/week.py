from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.bot import Bot
from telegram.ext import ConversationHandler
from telegram.update import Update

from bot.models import Users
from bot.logger import log
from bot.schedule.commons import get_lessons
from bot.service.common_handlers import send_cancel
from bot.utils.functions import is_back, is_cancelled, typing
from bot.utils.keyboards import (SCHEDULE_KEYBOARD, SCHEDULE_KEYBOARD_STUDENT,
                                 WEEK_KEYBOARD, REGISTER_KEYBOARD)
from bot.utils.messages import MESSAGES
from bot.utils.schema import DAY_MAPPING
from bot.utils.states import DAY_OF_WEEK, SCHEDULE, ASK_EMAIL

MESSAGES = MESSAGES['schedule:week']


@log
@typing
def on_week(bot: Bot, update: Update) -> str:
    bot.send_message(
        update.message.chat.id,
        MESSAGES['on_week:ask'],
        ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(WEEK_KEYBOARD, True)
    )
    return DAY_OF_WEEK


@log
@typing
def choose_dow(bot: Bot, update: Update) -> (int, str, None):
    """ Send schedule for given Day Of Week (dow) """
    uid = update.message.from_user.id
    chat_id = update.message.chat.id
    message = update.message.text
    keyboard = SCHEDULE_KEYBOARD_STUDENT
    try:
        user = Users.get(Users.telegram_id == uid)
        if not user.is_student:
            keyboard = SCHEDULE_KEYBOARD
    except BaseException as excinfo:
        print(excinfo)
        bot.send_message(
            uid,
            MESSAGES['on_schedule:unregistered'],
            ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(REGISTER_KEYBOARD, True)
        )
        return ASK_EMAIL

    if is_cancelled(message):
        send_cancel(bot, uid)
        return ConversationHandler.END
    elif is_back(message):
        bot.send_message(
            chat_id,
            MESSAGES['choose_dow:back'],
            ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard, True)
        )
        return SCHEDULE



    lessons = get_lessons(uid)
    if not lessons:
        bot.send_message(chat_id, MESSAGES['choose_dow:empty'], ParseMode.HTML)
        return
    schedule = dict(zip(DAY_MAPPING, [lessons.monday, lessons.tuesday,
                                      lessons.wednesday, lessons.thursday,
                                      lessons.friday, lessons.saturday]))
    if message not in schedule:
        bot.send_message(
            chat_id,
            MESSAGES['choose_dow:spam'](message),
            ParseMode.HTML
        )
        return
    bot.send_message(chat_id, schedule[message], ParseMode.HTML)
