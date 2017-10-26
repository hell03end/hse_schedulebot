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


def find(asked_fio: str) -> list:
    try:
        query = Lecturers.select().\
            where(Lecturers.fio.contains(asked_fio.lower())).\
            order_by(Lecturers.fio)
        return [{'fio': lect.fio} for lect in query]
    except Lecturers.DoesNotExist as err:
        print(err)
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

    bot.send_message(
        update.message.from_user.id,
        'Список найденных преподавателей. Выбери нужного:',
        reply_markup=ReplyKeyboardMarkup(find(lect_name).extend('Назад'), True)
    )
    return LECTURERS_SCHEDULE


# @log
# @typing
# def get_lecturers(bot: Bot, update: Update) -> str:
#     lect_name = update.message.text
#     chat_id = update.message.chat.id

#     if is_back(update.message.text):
#         bot.send_message(
#             chat_id,
#             MESSAGES['choose_dow:back'],
#             ParseMode.HTML,
#             reply_markup=ReplyKeyboardMarkup(SCHEDULE_KEYBOARD_STUDENT, True)
#         )
#         return SCHEDULE
    

#     return LECTURERS_SCHEDULE
