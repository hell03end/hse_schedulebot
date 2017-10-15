from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, RegexHandler, \
    Filters, MessageHandler, CommandHandler

from states import *
from utils.keyboards import week_keybord, start_keyboard
from utils.functions import is_cancelled
from service.common_handlers import start
from models import Lessons
from logger import log
import emoji


@log
def on_week(bot, update):
    calendar = emoji.emojize(':tear-off_calendar:')
    uid = update.message.from_user.id
    bot.send_message(
        uid,
        f'Выбери день недели {calendar}',
        reply_markup=ReplyKeyboardMarkup(week_keybord)
    )
    return DAY_OF_WEEK


@log
def choose_dow(bot, update):
    uid = update.message.from_user.id
    chat_id = update.message.chat.id
    message = update.message.text
    if is_cancelled(message):
        bot.send_message(
            uid,
            'Вот предыдущее меню',
            reply_markup=ReplyKeyboardMarkup(start_keyboard)
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


def register(dp):
    week_schedule = ConversationHandler(
        entry_points=[RegexHandler('На неделю', on_week)],
        states={
            DAY_OF_WEEK: [MessageHandler(Filters.text, choose_dow)],
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dp.add_handler(week_schedule)
