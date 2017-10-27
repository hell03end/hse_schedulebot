from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.bot import Bot
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, RegexHandler)
from telegram.ext.dispatcher import Dispatcher
from telegram.update import Update

from bot.logger import log
from bot.models import Lecturers, Users
from bot.schedule.start import start
from bot.service.common_handlers import send_cancel
from bot.utils.functions import is_back, is_cancelled, typing
from bot.utils.keyboards import (BACK_KEY, REGISTER_KEYBOARD,
                                 SCHEDULE_KEYBOARD_STUDENT)
from bot.utils.messages import MESSAGES
from bot.utils.states import ASK_EMAIL, LECTURERS_SCHEDULE, SCHEDULE

MESSAGES = MESSAGES['lect_schedule:start']


def find_lecturer(asked_fio: str) -> list:
    query = Lecturers.select().\
        where(Lecturers.fio.contains(asked_fio.lower())).\
        order_by(Lecturers.fio)
    if query.exists():
        return [[lect.fio] for lect in query]
    return []


@log
@typing
def on_lect_find(bot: Bot, update: Update) -> str:
    bot.send_message(
        update.message.chat.id,
        MESSAGES['find_lect:ask'],
        ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup([BACK_KEY], True)
    )
    return LECTURERS_SCHEDULE    


@log
@typing
def get_lect_name(bot: Bot, update: Update) -> (int, str):
    chat_id = update.message.chat.id
    uid = update.message.from_user.id
    message = update.message.text

    if is_cancelled(message):
        send_cancel(bot, uid)
        return ConversationHandler.END
    elif is_back(message):
        bot.send_message(
            chat_id,
            'К выбору расписания',    # Change!
            ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(SCHEDULE_KEYBOARD_STUDENT, True)
        )
        return SCHEDULE

    # TODO: this should be a decorator
    try:
        user = Users.get(Users.telegram_id == uid)
    except BaseException as excinfo:
        print(excinfo)
        bot.send_message(
            uid,
            MESSAGES['on_schedule:unregistered'],
            ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(REGISTER_KEYBOARD, True)
        )
        return ASK_EMAIL
    
    lect_name = message
    founded_lects = find_lecturer(lect_name)
    if len(founded_lects) > 20:
        # писать, что ты ахуел мальчик, сужай запрос

        return
    keyboard_with_lects = founded_lects
    if not founded_lects:
        message = 'Такого преподавателя нет в ВШЭ('
    else:
        message = 'Список найденных преподавателей. Выбери нужного:'

    keyboard_with_lects.append(['Назад'])
    bot.send_message(
        update.message.from_user.id,
        message,
        reply_markup=ReplyKeyboardMarkup(keyboard_with_lects, True)
    )
    return LECTURERS_SCHEDULE
