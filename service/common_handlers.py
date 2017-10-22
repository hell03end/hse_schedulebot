from logger import log
from models import Users
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler
from utils.keyboards import START_KEYBOARD
from utils.messages import MESSAGES

MESSAGES = MESSAGES['common_handlers']

# TODO: add decorator, which asks for corp email


@log
def start(bot: object, update: object) -> None:
    bot.send_message(
        update.message.from_user.id,
        MESSAGES['start:greetings'],
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD)
    )


def register(dispatcher: object) -> None:
    dispatcher.add_handler(CommandHandler('start', start))
