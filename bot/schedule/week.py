from bot.logger import log
from bot.schedule.commons import get_lessons
from bot.service.common_handlers import send_cancel
from bot.utils.functions import is_back, is_cancelled, typing
from bot.utils.keyboards import SCHEDULE_KEYBOARD, WEEK_KEYBOARD
from bot.utils.messages import MESSAGES
from bot.utils.schema import DAY_MAPPING
from bot.utils.states import DAY_OF_WEEK, SCHEDULE
from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.bot import Bot
from telegram.ext import ConversationHandler
from telegram.update import Update

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

    if is_cancelled(message):
        send_cancel(bot, uid)
        return ConversationHandler.END
    elif is_back(message):
        bot.send_message(
            chat_id,
            MESSAGES['choose_dow:back'],
            ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(SCHEDULE_KEYBOARD, True)
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
