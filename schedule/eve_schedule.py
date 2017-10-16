from datetime import datetime as dt

from logger import log
from service.common_handlers import start
from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler,
                          RegexHandler)
from utils import DAY_OF_WEEK


def register(dispatcher: object) -> None:
    dispatcher.add_handler()
