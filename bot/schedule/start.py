from bot.logger import log
from bot.schedule.day import on_day, on_tomorrow
from bot.schedule.week import choose_dow, on_week
from bot.service.common_handlers import send_cancel, start
from bot.utils.functions import is_back, is_cancelled, typing
from bot.utils.keyboards import BACK_KEY, SCHEDULE_KEYBOARD, START_KEYBOARD
from bot.utils.messages import MESSAGES
from bot.utils.states import DAY_OF_WEEK, SCHEDULE
from telegram import ReplyKeyboardMarkup
from telegram.bot import Bot
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, RegexHandler)
from telegram.ext.dispatcher import Dispatcher
from telegram.update import Update

MESSAGES = MESSAGES['schedule:start']


@log
@typing
def on_schedule(bot: Bot, update: Update) -> str:
    bot.send_message(
        update.message.from_user.id,
        MESSAGES['on_schedule:ask'],
        reply_markup=ReplyKeyboardMarkup(SCHEDULE_KEYBOARD, True)
    )
    return SCHEDULE


@log
@typing
def on_back(bot: Bot, update: Update) -> int:
    bot.send_message(
        update.message.from_user.id,
        MESSAGES['on_back:msg'],
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
                RegexHandler(BACK_KEY[0], on_back)
            ],
            DAY_OF_WEEK: [MessageHandler(Filters.text, choose_dow)]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dispatcher.add_handler(start_schedule)
