from datetime import datetime

from logger import log
from models import Lessons
from service.common_handlers import start
from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, RegexHandler)
from utils.functions import is_cancelled
from utils.keyboards import SCHEDULE_KEYBOARD, START_KEYBOARD, WEEK_KEYBOARD
from utils.messages import MESSAGES
from utils.schema import DAY_MAPPING
from utils.states import DAY_OF_WEEK

MESSAGES = MESSAGES['week_schedule']


@log
def on_week(bot: object, update: object) -> str:
    bot.send_message(
        update.message.from_user.id,
        MESSAGES['on_week:ask'],
        reply_markup=ReplyKeyboardMarkup(WEEK_KEYBOARD)
    )
    return DAY_OF_WEEK


@log
def on_day(bot: object, update: object) -> int:
    uid = update.message.from_user.id
    chat_id = update.message.chat.id
    message = update.message.text
    if is_cancelled(message):
        bot.send_message(
            uid,
            MESSAGES['on_day:back'],
            reply_markup=ReplyKeyboardMarkup(START_KEYBOARD)
        )

    lessons = Lessons.get(Lessons.student.telegram_id == uid)
    send_params = {
        'chat_id': chat_id,
        'parse_mode': ParseMode.MARKDOWN
    }
    schedule = dict(zip(DAY_MAPPING, [lessons.monday, lessons.tuesday,
                                      lessons.wednesday, lessons.thursday,
                                      lessons.friday, lessons.saturday]))
    day = datetime.now().weekday()
    try:
        bot.send_message(text=schedule[DAY_MAPPING[day]], **send_params)
    except IndexError:
        bot.send_message(text=MESSAGES['on_day:sunday'], **send_params)
    return ConversationHandler.END


@log
def choose_dow(bot: object, update: object) -> int:
    """ Send schedule for given Day Of Week (dow) """
    uid = update.message.from_user.id
    chat_id = update.message.chat.id
    message = update.message.text
    if is_cancelled(message):
        bot.send_message(
            uid,
            MESSAGES['choose_dow:back'],
            reply_markup=ReplyKeyboardMarkup(START_KEYBOARD)
        )

    lessons = Lessons.get(Lessons.student.telegram_id == uid)
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
    return ConversationHandler.END


def register(dispatcher: object) -> None:
    week_schedule = ConversationHandler(
        entry_points=[RegexHandler(SCHEDULE_KEYBOARD[1][0], on_week)],
        states={
            DAY_OF_WEEK: [MessageHandler(Filters.text, choose_dow)],
        },
        fallbacks=[CommandHandler('start', start)]
    )
    day_schedule = ConversationHandler(
        entry_points=[RegexHandler(SCHEDULE_KEYBOARD[0][0], on_day),
                      RegexHandler(SCHEDULE_KEYBOARD[0][1], on_day)],
        states=None,  # is it correct?
        fallbacks=[CommandHandler('start', start)]
    )

    dispatcher.add_handler(week_schedule)
    dispatcher.add_handler(day_schedule)
