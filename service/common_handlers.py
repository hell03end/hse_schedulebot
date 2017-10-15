from emoji import emojize
from logger import log
from models import Users
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler
from utils.keyboards import START_KEYBOARD

# TODO: add decorator, which asks for corp email


@log
def start(bot: object, update: object) -> None:
    uid = update.message.from_user.id
    winking_face = emojize(':winking_face:')
    msg = f'Привет! У меня можно подсмотреть расписания ' \
          f'электричек или твоей учебы{winking_face}'
    bot.send_message(
        uid,
        msg,
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD)
    )


def register(dispatcher: object) -> None:
    dispatcher.add_handler(CommandHandler('start', start))
