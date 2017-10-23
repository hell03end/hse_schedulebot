from threading import Thread

from bot.logger import log
from bot.models import Users
from bot.models.update_schedules import get_and_save
from bot.service.common_handlers import send_cancel, start
from bot.utils.functions import is_back, is_cancelled, typing
from bot.utils.keyboards import (BACK_KEY, CITIES_KEYBOARD, SETTINGS_KEYBOARD,
                                 START_KEYBOARD)
from bot.utils.messages import MESSAGES
from bot.utils.schema import CITIES
from bot.utils.states import ASK_CITY, ASK_EMAIL, SETTINGS
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
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
            reply_markup=ReplyKeyboardMarkup(SETTINGS_KEYBOARD, True)
        )
        return ASK_EMAIL
    bot.send_message(
        uid,
        MESSAGES['on_settings:current'].format(user.email, user.city),
        reply_markup=ReplyKeyboardMarkup(SETTINGS_KEYBOARD, True)
    )
    return SETTINGS


@log
@typing
def choose_menu(bot: Bot, update: Update) -> (int, str):
    uid = update.message.from_user.id
    chat_id = update.message.chat.id
    message = update.message.text
    if is_cancelled(message):
        return send_cancel(bot, uid)
    if is_back(message):
        return on_back(bot, update)

    if message == SETTINGS_KEYBOARD[0][0]:
        return show_about(bot, update)
    elif message == SETTINGS_KEYBOARD[1][0]:
        bot.send_message(
            uid,
            text=MESSAGES['choose_menu:ask_email'],
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_EMAIL
    elif message == SETTINGS_KEYBOARD[1][1]:
        bot.send_message(
            uid,
            text=MESSAGES['choose_menu:ask_city'],
            reply_markup=ReplyKeyboardMarkup(CITIES_KEYBOARD, True)
        )
        return ASK_CITY
    elif message == SETTINGS_KEYBOARD[2][0]:
        pass  # mail to developer
    else:
        bot.send_message(
            uid,
            MESSAGES['choose_menu:unknown'],
            reply_markup=ReplyKeyboardMarkup(SETTINGS_KEYBOARD, True)
        )
    return SETTINGS


@log
@typing
def on_back(bot: Bot, update: Update) -> int:
    bot.send_message(
        update.message.from_user.id,
        MESSAGES['on_back:msg'],
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD, True)
    )
    return ConversationHandler.END


@log
@typing
def get_email(bot: Bot, update: Update) -> (int, str):
    uid = update.message.from_user.id
    message = update.message.text
    if is_cancelled(message):
        return send_cancel(bot, uid)

    if not Users.check_email(message):
        bot.send_message(
            uid,
            text=MESSAGES['get_email:incorrect'],
            reply_markup=ReplyKeyboardMarkup(SETTINGS_KEYBOARD, True)
        )
    else:
        user = Users.get(Users.telegram_id == uid)
        user.set_email(message)
        user.set_status(message)
        user.save()

        thread = Thread(
            target=get_and_save,
            kwargs={'email': (user.email, user.student)}
        )
        thread.start()

        bot.send_message(
            uid,
            text=MESSAGES['get_email:correct'],
            reply_markup=ReplyKeyboardMarkup(SETTINGS_KEYBOARD, True)
        )
    return SETTINGS


@log
@typing
def get_city(bot: Bot, update: Update) -> (int, str):
    uid = update.message.from_user.id
    message = update.message.text
    if is_cancelled(message):
        return send_cancel(bot, uid)

    if message not in CITIES:
        bot.send_message(
            uid,
            text=MESSAGES['get_city:incorrect'],
            reply_markup=ReplyKeyboardMarkup(SETTINGS_KEYBOARD, True)
        )
    else:
        user = Users.get(Users.telegram_id == uid)
        user.set_city(message)
        user.save()
        bot.send_message(
            uid,
            text=MESSAGES['get_city:correct'],
            reply_markup=ReplyKeyboardMarkup(SETTINGS_KEYBOARD, True)
        )
    return SETTINGS


@log
@typing
def show_about(bot: Bot, update: Update) -> str:
    bot.send_message(update.message.from_user.id, MESSAGES['show_about'])
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
