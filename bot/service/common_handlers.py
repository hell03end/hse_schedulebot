import logging
from threading import Thread

from bot.logger import log
from bot.models import Users
from bot.models.update_schedules import get_and_save
from bot.utils.functions import is_cancelled, typing
from bot.utils.keyboards import (CITIES_KEYBOARD, REGISTER_KEYBOARD,
                                 START_KEYBOARD)
from bot.utils.messages import MESSAGES, TRIGGERS
from bot.utils.schema import CITIES
from bot.utils.states import ASK_CITY, ASK_EMAIL, INCORRECT_EMAIL
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.bot import Bot
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, RegexHandler)
from telegram.ext.dispatcher import Dispatcher
from telegram.update import Update

MESSAGES = MESSAGES['service:common_handlers']


@log
@typing
def ask_email(bot: Bot, update: Update) -> (int, str):
    chat_id = update.message.chat.id
    if is_cancelled(update.message.text):
        return send_cancel(bot, chat_id)

    bot.send_message(
        chat_id,
        MESSAGES['ask_email:ask'],
        ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_EMAIL


@log
@typing
def ask_city(bot: Bot, update: Update) -> (int, str):
    chat_id = update.message.chat.id
    if is_cancelled(update.message.text):
        return send_cancel(bot, chat_id)

    bot.send_message(
        chat_id,
        MESSAGES['ask_city:ask'],
        ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(CITIES_KEYBOARD, True)
    )
    return ASK_CITY


@log
def send_cancel(bot: Bot, uid: int, user_data: dict=None) -> int:
    bot.send_message(
        uid,
        MESSAGES['cancel'],
        ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD, True)
    )
    if user_data:
        for key, val in user_data.items():
            del key, val
    return ConversationHandler.END


@log
@typing
def get_email(bot: Bot, update: Update, user_data: dict) -> (int, str):
    chat_id = update.message.chat.id
    message = update.message.text
    if is_cancelled(message):
        return send_cancel(bot, chat_id)

    if not Users.check_email(message):
        bot.send_message(
            chat_id,
            MESSAGES['get_email:incorrect'],
            ParseMode.HTML
        )
        return INCORRECT_EMAIL

    user_data['reg_email'] = message

    bot.send_message(chat_id, MESSAGES['get_email:correct'], ParseMode.HTML)
    return ask_city(bot, update)


@log
@typing
def get_city(bot: Bot, update: Update, user_data: dict,
             verbose: bool = False) -> (int, str):
    chat_id = update.message.chat.id
    message = update.message.text
    if is_cancelled(message):
        return send_cancel(bot, chat_id)

    if message not in CITIES:
        bot.send_message(
            chat_id,
            MESSAGES['get_city:incorrect'],
            ParseMode.HTML
        )
        message = "Москва"  # default value
    user_data['reg_city'] = message

    if verbose:
        bot.send_message(chat_id, MESSAGES['get_city:msg'], ParseMode.HTML)
    return add_user(bot, update, user_data)


@log
def add_user(bot: Bot, update: Update, user_data: dict) -> (int, str):
    uid = update.message.from_user.id
    message = update.message.text
    username = update.message.from_user.username
    if is_cancelled(message):
        return send_cancel(bot, uid)

    user = Users.create(telegram_id=uid, username=username)
    user.set_city(user_data['reg_city'])
    user.set_email(user_data['reg_email'])
    user.set_status(user_data['reg_email'])
    user.save()  # TODO: check email is valid

    for key, val in user_data.items():
        del key, val

    thread = Thread(
        name=f"get_and_save::{uid}, {user.email}",
        target=get_and_save,
        args=((user.email, user.is_student, uid),)
    )
    thread.start()

    bot.send_message(
        uid,
        MESSAGES['add_user:msg'],
        ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD, True)
    )
    return ConversationHandler.END


@log
@typing
def show_about(bot: Bot, update: Update) -> int:
    bot.send_message(
        update.message.from_user.id,
        MESSAGES['show_about'],
        ParseMode.HTML
    )


@log
@typing
def start(bot: Bot, update: Update) -> None:
    uid = update.message.from_user.id
    username = update.message.from_user.username
    user = None
    try:
        user = Users.get(Users.telegram_id == uid)
    except BaseException as excinfo:
        logging.debug(excinfo)
    if not user:
        bot.send_message(
            uid,
            MESSAGES['start:greetings_new'],
            ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(REGISTER_KEYBOARD, True)
        )
        return
    user.username = username
    user.save()
    bot.send_message(
        uid,
        MESSAGES['start:greetings'],
        ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD, True)
    )
    return ConversationHandler.END


def register(dispatcher: Dispatcher) -> None:
    registration = ConversationHandler(
        entry_points=[RegexHandler(REGISTER_KEYBOARD[0][0], ask_email)],
        states={
            ASK_EMAIL: [
                MessageHandler(Filters.text, get_email, pass_user_data=True)
            ],
            INCORRECT_EMAIL: [
                MessageHandler(Filters.text, get_email, pass_user_data=True)
            ],
            ASK_CITY: [
                MessageHandler(
                    Filters.text,
                    lambda bot, update, user_data: get_city(
                        bot,
                        update,
                        user_data,
                        verbose=True
                    ),
                    pass_user_data=True
                )
            ],
        },
        fallbacks=(CommandHandler('start', start),),
        allow_reentry=True
    )

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(registration)
    dispatcher.add_handler(RegexHandler(REGISTER_KEYBOARD[1][0], show_about))
    dispatcher.add_handler(RegexHandler(TRIGGERS['info'], show_about))
