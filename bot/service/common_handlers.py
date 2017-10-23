from threading import Thread

from bot.logger import log
from bot.models import Users
from bot.models.update_schedules import get_and_save
from bot.utils.functions import is_cancelled, typing
from bot.utils.keyboards import (CITIES_KEYBOARD, REGISTER_KEYBOARD,
                                 START_KEYBOARD)
from bot.utils.messages import MESSAGES
from bot.utils.schema import CITIES
from bot.utils.states import ASK_CITY, ASK_EMAIL, INCORRECT_EMAIL
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.bot import Bot
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, RegexHandler)
from telegram.ext.dispatcher import Dispatcher
from telegram.update import Update

MESSAGES = MESSAGES['service:common_handlers']


@log
@typing
def ask_email(bot: Bot, update: Update) -> (int, str):
    uid = update.message.from_user.id
    if is_cancelled(update.message.text):
        return send_cancel(bot, uid)

    bot.send_message(
        uid,
        text=MESSAGES['ask_email:ask'],
        reply_markup=ReplyKeyboardRemove()
    )
    return ASK_EMAIL


@log
@typing
def ask_city(bot: Bot, update: Update) -> (int, str):
    uid = update.message.from_user.id
    if is_cancelled(update.message.text):
        return send_cancel(bot, uid)

    bot.send_message(
        uid,
        text=MESSAGES['ask_city:ask'],
        reply_markup=ReplyKeyboardMarkup(CITIES_KEYBOARD, True)
    )
    return ASK_CITY


@log
def send_cancel(bot: Bot, uid: int) -> int:
    bot.send_message(
        uid,
        text=MESSAGES['cancel'],
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD, True)
    )
    return ConversationHandler.END


@log
@typing
def get_email(bot: Bot, update: Update, user_data: dict) -> (int, str):
    uid = update.message.from_user.id
    message = update.message.text
    if is_cancelled(message):
        return send_cancel(bot, uid)

    if not Users.check_email(message):
        bot.send_message(uid, text=MESSAGES['get_email:incorrect'])
        return INCORRECT_EMAIL

    user_data['reg_email'] = message
    user_data['reg_tg_id'] = uid
    user_data['reg_username'] = update.message.from_user.username

    bot.send_message(uid, text=MESSAGES['get_email:correct'])
    return ask_city(bot, update)


@log
@typing
def get_city(bot: Bot, update: Update, user_data: dict) -> (int, str):
    uid = update.message.from_user.id
    message = update.message.text
    if is_cancelled(message):
        return send_cancel(bot, uid)

    if message not in CITIES:
        bot.send_message(uid, text=MESSAGES['get_city:incorrect'])
        message = "Москва"  # default value

    user_data['reg_city'] = message

    bot.send_message(uid, text=MESSAGES['get_city:msg'])
    return add_user(bot, update, user_data)


@log
@typing
def add_user(bot: Bot, update: Update, user_data: dict) -> (int, str):
    uid = update.message.from_user.id
    message = update.message.text
    if is_cancelled(message):
        return send_cancel(bot, uid)

    user = Users(telegram_id=user_data['reg_tg_id'],
                 username=user_data['reg_username'])
    user.set_city(user_data['reg_city'])
    user.set_email(user_data['reg_email'])
    user.set_status(user_data['reg_email'])
    user.save()

    thread = Thread(
        target=get_and_save,
        kwargs={'email': (user.email, user.student)}
    )
    thread.start()  # update schedules

    bot.send_message(
        uid,
        text=MESSAGES['add_user:msg'],
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD, True)
    )
    return ConversationHandler.END


@log
@typing
def show_about(bot: Bot, update: Update) -> int:
    bot.send_message(
        update.message.from_user.id,
        MESSAGES['show_about'],
        reply_markup=ReplyKeyboardMarkup(REGISTER_KEYBOARD, True)
    )
    return ConversationHandler.END


@log
@typing
def start(bot: Bot, update: Update) -> None:
    uid = update.message.from_user.id
    user = None
    try:
        user = Users.get(Users.telegram_id == uid)
    except BaseException as excinfo:
        print(excinfo)
    if not user:
        bot.send_message(
            uid,
            MESSAGES['start:greetings_new'],
            reply_markup=ReplyKeyboardMarkup(REGISTER_KEYBOARD, True)
        )
        return
    bot.send_message(
        uid,
        MESSAGES['start:greetings'].format(user.username),
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD, True)
    )


def register(dispatcher: Dispatcher) -> None:
    start_handler = CommandHandler('start', start)
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
                MessageHandler(Filters.text, get_city, pass_user_data=True)
            ],
        },
        fallbacks=(start_handler, )
    )
    show_info = ConversationHandler(
        entry_points=[
            RegexHandler(REGISTER_KEYBOARD[1][0], show_about),
            RegexHandler(r"(инфо|о боте|функции)", show_about)
        ],
        states={},
        fallbacks=(start_handler, )
    )

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(registration)
    dispatcher.add_handler(show_info)
