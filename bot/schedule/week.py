from bot.logger import log
from bot.models import Lessons
from bot.service.common_handlers import start
from bot.utils.functions import is_cancelled
from bot.utils.keyboards import (SCHEDULE_KEYBOARD, START_KEYBOARD,
                                 WEEK_KEYBOARD)
from bot.utils.messages import MESSAGES
from bot.utils.schema import DAY_MAPPING
from bot.utils.states import DAY_OF_WEEK
from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.bot import Bot
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, RegexHandler)
from telegram.ext.dispatcher import Dispatcher

MESSAGES = MESSAGES['schedule:week']


@log
def on_week(bot: Bot, update: object) -> str:
    bot.send_message(
        update.message.from_user.id,
        MESSAGES['on_week:ask'],
        reply_markup=ReplyKeyboardMarkup(WEEK_KEYBOARD)
    )
    return DAY_OF_WEEK


@log
def choose_dow(bot: Bot, update: object) -> int:
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


def register(dispatcher: Dispatcher) -> None:
    week_schedule = ConversationHandler(
        entry_points=[RegexHandler(SCHEDULE_KEYBOARD[1][0], on_week)],
        states={
            DAY_OF_WEEK: [MessageHandler(Filters.text, choose_dow)],
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dispatcher.add_handler(week_schedule)
