from emoji import emojize
from logger import log
from models import Lessons
from service.common_handlers import start
from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, RegexHandler)
from utils import DAY_OF_WEEK, START_KEYBOARD, WEEK_KEYBOARD, is_cancelled


@log
def on_week(bot: object, update: object) -> str:
    calendar = emojize(':tear-off_calendar:')
    uid = update.message.from_user.id
    bot.send_message(
        uid,
        f'Выбери день недели {calendar}',
        reply_markup=ReplyKeyboardMarkup(WEEK_KEYBOARD)
    )
    return DAY_OF_WEEK


@log
def choose_dow(bot: object, update: object) -> None:
    uid = update.message.from_user.id
    chat_id = update.message.chat.id
    message = update.message.text
    if is_cancelled(message):
        bot.send_message(
            uid,
            'Вот предыдущее меню',
            reply_markup=ReplyKeyboardMarkup(START_KEYBOARD)
        )

    lessons = Lessons.get(Lessons.student.telegram_id == uid)
    send_params = {
        'text': 'Выбери вариант на клавиатуре',
        'chat_id': chat_id,
        'parse_mode': ParseMode.HTML
    }
    if message == 'Понедельник':
        send_params['text'] = lessons.monday
    elif message == 'Вторник':
        send_params['text'] = lessons.tuesday,
    elif message == 'Среда':
        send_params['text'] = lessons.wednesday,
    elif message == 'Четверг':
        send_params['text'] = lessons.thursday,
    elif message == 'Пятница':
        send_params['text'] = lessons.friday,
    elif message == 'Суббота':
        send_params['text'] = lessons.saturday
    bot.send_message(**send_params)


def register(dispatcher: object) -> None:
    week_schedule = ConversationHandler(
        entry_points=[RegexHandler('На неделю', on_week)],
        states={
            DAY_OF_WEEK: [MessageHandler(Filters.text, choose_dow)],
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dispatcher.add_handler(week_schedule)
