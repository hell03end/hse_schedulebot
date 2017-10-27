import logging
from threading import Thread

from bot.logger import log
from bot.models import Users
from bot.models.update_schedules import get_and_save
from bot.schedule.commons import get_lessons
from bot.utils.functions import is_cancelled, is_stopped, typing
from bot.utils.keyboards import (CITIES_KEYBOARD, REGISTER_KEYBOARD,
                                 START_KEYBOARD)
from bot.utils.messages import MESSAGES, TRIGGERS
from bot.utils.schema import CITIES
from bot.utils.states import ASK_CITY, ASK_EMAIL
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
    message = update.message.text
    if is_cancelled(message):
        send_cancel(bot, chat_id, user_data={
            'reply_markup': ReplyKeyboardMarkup(REGISTER_KEYBOARD, True)
        })
        return ConversationHandler.END

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
    message = update.message.text
    if is_cancelled(message):
        send_cancel(bot, chat_id, user_data={
            'reply_markup': ReplyKeyboardMarkup(REGISTER_KEYBOARD, True)
        })
        return ConversationHandler.END
    elif is_stopped(message):
        on_stop(bot, update)
        return ConversationHandler.END

    bot.send_message(
        chat_id,
        MESSAGES['ask_city:ask'],
        ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(CITIES_KEYBOARD, True)
    )
    return ASK_CITY


@log
def send_cancel(bot: Bot, uid: int, user_data: dict=None) -> int:
    if not user_data:
        user_data = {}
    bot.send_message(
        uid,
        MESSAGES['cancel'],
        ParseMode.HTML,
        reply_markup=user_data.pop('reply_markup', None)
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
        user_data['reply_markup'] = ReplyKeyboardMarkup(
            REGISTER_KEYBOARD, True)
        send_cancel(bot, chat_id, user_data)
        return ConversationHandler.END
    elif is_stopped(message):
        on_stop(message),
        return ConversationHandler.END

    if not Users.check_email(message):
        bot.send_message(
            chat_id,
            MESSAGES['get_email:incorrect'],
            ParseMode.HTML
        )
        return

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
        user_data['reply_markup'] = ReplyKeyboardMarkup(
            REGISTER_KEYBOARD, True)
        send_cancel(bot, chat_id, user_data)
        return ConversationHandler.END
    elif is_stopped(message):
        on_stop(message),
        return ConversationHandler.END

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
        user_data['reply_markup'] = ReplyKeyboardMarkup(
            REGISTER_KEYBOARD, True)
        send_cancel(bot, uid, user_data)
        return ConversationHandler.END
    elif is_stopped(message):
        on_stop(message),
        return ConversationHandler.END

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
    message = update.message.text
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
        return ConversationHandler.END
    user.username = username
    user.save()
    bot.send_message(
        uid,
        MESSAGES['start:greetings'],
        ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD, True)
    )
    return ConversationHandler.END


@log
@typing
def on_stop(bot: Bot, update: Update) -> int:
    uid = update.message.from_user.id
    user = None
    try:
        user = Users.get(Users.telegram_id == uid)
    except BaseException as excinfo:
        logging.debug(excinfo)
    if not user:
        bot.send_message(
            uid,
            MESSAGES['on_stop:unregistered'],
            ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(REGISTER_KEYBOARD, True)
        )
        return
    lessons = get_lessons(uid)
    if lessons:
        lessons.delete_instance()
    user.delete_instance()
    bot.send_message(
        uid,
        MESSAGES['on_stop:complete'],
        ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def register(dispatcher: Dispatcher) -> None:
    registration = ConversationHandler(
        entry_points=[RegexHandler(REGISTER_KEYBOARD[0][0], ask_email)],
        states={
            ASK_EMAIL: [
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
        fallbacks=(CommandHandler('start', start),)
    )

    dispatcher.add_handler(CommandHandler('about', show_about))
    dispatcher.add_handler(CommandHandler('stop', on_stop))
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(registration)
    dispatcher.add_handler(RegexHandler(REGISTER_KEYBOARD[1][0], show_about))
    dispatcher.add_handler(RegexHandler(TRIGGERS['info'], show_about))
