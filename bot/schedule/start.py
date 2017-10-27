from bot.logger import log
from bot.models import Users
from bot.schedule.day import on_day, on_tomorrow
from bot.schedule.week import choose_dow, on_week
from bot.service.common_handlers import on_stop, send_cancel, start
from bot.utils.functions import is_cancelled, is_stopped, typing
from bot.utils.keyboards import (BACK_KEY, REGISTER_KEYBOARD,
                                 SCHEDULE_KEYBOARD, START_KEYBOARD)
from bot.utils.messages import MESSAGES, TRIGGERS
from bot.utils.states import ASK_EMAIL, DAY_OF_WEEK, SCHEDULE
from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.bot import Bot
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, RegexHandler)
from telegram.ext.dispatcher import Dispatcher
from telegram.update import Update

MESSAGES = MESSAGES['schedule:start']


@log
@typing
def on_schedule(bot: Bot, update: Update) -> str:
    uid = update.message.from_user.id
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

    bot.send_message(
        update.message.chat.id,
        MESSAGES['on_schedule:ask'],
        ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(SCHEDULE_KEYBOARD, True)
    )
    return SCHEDULE


@log
@typing
def on_spam(bot: Bot, update: Update) -> str:
    chat_id = update.message.chat.id
    message = update.message.text
    if is_cancelled(message):
        send_cancel(bot, chat_id, user_data={
            'reply_markup': ReplyKeyboardMarkup(START_KEYBOARD, True)
        })
        return ConversationHandler.END
    elif is_stopped(message):
        on_stop(bot, update)
        return ConversationHandler.END

    bot.send_message(
        chat_id,
        MESSAGES['on_spam'](message),
        ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(SCHEDULE_KEYBOARD, True)
    )
    return SCHEDULE


@log
@typing
def on_back(bot: Bot, update: Update) -> int:
    bot.send_message(
        update.message.chat.id,
        MESSAGES['on_back:msg'],
        ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD, True)
    )
    return ConversationHandler.END


def register(dispatcher: Dispatcher) -> None:
    start_schedule = ConversationHandler(
        entry_points=[RegexHandler(START_KEYBOARD[0][0], on_schedule)],
        states={
            SCHEDULE: [
                RegexHandler(SCHEDULE_KEYBOARD[1][0], on_week),
                RegexHandler(SCHEDULE_KEYBOARD[0][0], on_day),
                RegexHandler(SCHEDULE_KEYBOARD[0][1], on_tomorrow),
                RegexHandler(BACK_KEY[0], on_back),
                # RegexHandler(TRIGGERS['all'], on_spam)
            ],
            DAY_OF_WEEK: [MessageHandler(Filters.text, choose_dow)]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dispatcher.add_handler(start_schedule)
