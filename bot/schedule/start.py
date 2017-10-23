from bot.logger import log
from bot.service.common_handlers import start
from bot.utils.keyboards import SCHEDULE_KEYBOARD, START_KEYBOARD, BACK_KEY
from bot.utils.messages import MESSAGES
from telegram import ReplyKeyboardMarkup
from telegram.bot import Bot
from telegram.ext import CommandHandler, ConversationHandler, RegexHandler
from telegram.ext.dispatcher import Dispatcher

MESSAGES = MESSAGES['schedule:start']


@log
def on_schedule(bot: Bot, update: object) -> None:
    bot.send_message(
        update.message.from_user.id,
        MESSAGES['on_schedule:ask'],
        reply_markup=ReplyKeyboardMarkup(SCHEDULE_KEYBOARD, True)
    )


@log
def on_back(bot: Bot, update: object) -> None:
    bot.send_message(
        update.message.from_user.id,
        MESSAGES['on_back:msg'],
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD, True)
    )
    return ConversationHandler.END


def register(dispatcher: Dispatcher) -> None:
    start_schedule = ConversationHandler(
        entry_points=[RegexHandler(START_KEYBOARD[0][0], on_schedule)],
        states={},
        fallbacks=[CommandHandler('start', start)]
    )
    back_from_schedule = ConversationHandler(
        entry_points=[RegexHandler(BACK_KEY[0], on_back)],
        states={},
        fallbacks=[CommandHandler('start', start)]
    )
    dispatcher.add_handler(start_schedule)
    dispatcher.add_handler(back_from_schedule)
