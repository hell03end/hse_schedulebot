from threading import Thread

from bot.logger import log
from bot.models import Users
from bot.models.update_schedules import get_and_save
from bot.service.common_handlers import send_cancel, start
from bot.utils.functions import is_back, is_cancelled, typing
from bot.utils.keyboards import (BACK_KEY, CITIES_KEYBOARD_BACK,
                                 REGISTER_KEYBOARD, SETTINGS_KEYBOARD,
                                 START_KEYBOARD)
from bot.utils.messages import MESSAGES
from bot.utils.schema import CITIES
from bot.utils.states import ASK_CITY, ASK_EMAIL, SETTINGS
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from telegram.bot import Bot
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, RegexHandler)
from telegram.ext.dispatcher import Dispatcher
from telegram.update import Update

MESSAGES = MESSAGES['service:settings']


@log
@typing
def on_settings(bot: Bot, update: Update) -> str:
    uid = update.message.from_user.id
    try:
        user = Users.get(Users.telegram_id == uid)
    except BaseException as excinfo:
        print(excinfo)
        bot.send_message(
            uid,
            MESSAGES['on_settings:unregistered'],
            ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(REGISTER_KEYBOARD, True)
        )
        return ASK_EMAIL
    send_current(bot, uid, user.email, user.city)
    return SETTINGS


@log
@typing
def choose_menu(bot: Bot, update: Update) -> (int, str):
    chat_id = update.message.chat.id
    message = update.message.text
    if is_cancelled(message):
        return send_cancel(bot, chat_id)
    elif is_back(message):
        return on_back(bot, update)

    if message == SETTINGS_KEYBOARD[0][0]:
        return show_about(bot, update)
    elif message == SETTINGS_KEYBOARD[1][0]:
        bot.send_message(
            chat_id,
            MESSAGES['choose_menu:ask_email'],
            ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup([BACK_KEY], True)
        )
        return ASK_EMAIL
    elif message == SETTINGS_KEYBOARD[1][1]:
        bot.send_message(
            chat_id,
            MESSAGES['choose_menu:ask_city'],
            ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(CITIES_KEYBOARD_BACK, True)
        )
        return ASK_CITY
    elif message == SETTINGS_KEYBOARD[2][0]:
        bot.send_message(
            chat_id,
            MESSAGES['choose_menu:feedback'],
            ParseMode.HTML
        )
    else:
        bot.send_message(
            chat_id,
            MESSAGES['choose_menu:spam'](message),
            ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(SETTINGS_KEYBOARD, True)
        )
    return SETTINGS


@log
@typing
def on_back(bot: Bot, update: Update) -> int:
    bot.send_message(
        update.message.from_user.id,
        MESSAGES['on_back:msg'],
        ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD, True)
    )
    return ConversationHandler.END


@log
def send_current(bot: Bot, uid: int, email: str=None, city: str=None) -> None:
    bot.send_message(
        uid,
        MESSAGES['current'].format(email, city),
        ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(SETTINGS_KEYBOARD, True)
    )


@log
@typing
def get_email(bot: Bot, update: Update) -> (int, str):
    uid = update.message.from_user.id
    message = update.message.text
    if is_cancelled(message):
        return send_cancel(bot, uid)
    elif is_back(message):
        bot.send_message(
            uid,
            MESSAGES['get_email:back'],
            ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(SETTINGS_KEYBOARD, True)
        )
    elif not Users.check_email(message):
        bot.send_message(
            uid,
            MESSAGES['get_email:incorrect'],
            ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(SETTINGS_KEYBOARD, True)
        )
    else:
        user = Users.get(Users.telegram_id == uid)
        user.set_email(message)
        user.set_status(message)
        user.save()  # TODO: check email is correct

        thread = Thread(
            name=f"get_and_save::{uid}, {message}",
            target=get_and_save,
            args=((user.email, user.student, uid), )
        )
        thread.start()

        bot.send_message(uid, MESSAGES['get_email:correct'], ParseMode.HTML)
        send_current(bot, uid, user.email, user.city)
    return SETTINGS


@log
@typing
def get_city(bot: Bot, update: Update) -> (int, str):
    uid = update.message.from_user.id
    message = update.message.text
    if is_cancelled(message):
        return send_cancel(bot, uid)
    elif is_back(message):
        bot.send_message(
            uid,
            MESSAGES['get_city:back'],
            ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(SETTINGS_KEYBOARD, True)
        )
    elif message not in CITIES:
        bot.send_message(
            uid,
            MESSAGES['get_city:incorrect'],
            ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(SETTINGS_KEYBOARD, True)
        )
    else:
        user = Users.get(Users.telegram_id == uid)
        user.set_city(message, update=True)
        user.save()

        bot.send_message(uid, MESSAGES['get_city:correct'], ParseMode.HTML)
        send_current(bot, uid, user.email, user.city)
    return SETTINGS


@log
@typing
def show_about(bot: Bot, update: Update) -> str:
    bot.send_message(
        update.message.chat.id,
        MESSAGES['show_about'],
        ParseMode.HTML
    )
    return SETTINGS


def register(dispatcher: Dispatcher) -> None:
    settings = ConversationHandler(
        entry_points=[
            RegexHandler(START_KEYBOARD[1][0], on_settings),
            CommandHandler('settings', on_settings)
        ],
        states={
            ASK_EMAIL: [MessageHandler(Filters.text, get_email)],
            ASK_CITY: [MessageHandler(Filters.text, get_city)],
            SETTINGS: [MessageHandler(Filters.text, choose_menu)]
        },
        fallbacks=(CommandHandler('start', start), )
    )
    dispatcher.add_handler(settings)
    dispatcher.add_handler(CommandHandler('help', show_about))
