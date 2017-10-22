from bot.logger import log
from bot.models import Users
from bot.utils.keyboards import START_KEYBOARD
from bot.utils.messages import MESSAGES
from telegram import ReplyKeyboardMarkup
from telegram.bot import Bot
from telegram.ext import CommandHandler
from telegram.ext.dispatcher import Dispatcher

MESSAGES = MESSAGES['service:common_handlers']

# TODO: add decorator, which asks for corp email


@log
def start(bot: Bot, update: object) -> None:
    bot.send_message(
        update.message.from_user.id,
        MESSAGES['start:greetings'],
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD)
    )


def register(dispatcher: Dispatcher) -> None:
    dispatcher.add_handler(CommandHandler('start', start))
