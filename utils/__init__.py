from datetime import datetime as dt

from bot import start
from egrul import (client_type, confirm_value, data_client, select_region,
                   solve_captcha)
from logger import log
from model import Clients, DoesNotExist, Tasks, Users
from states import *
from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler,
                          RegexHandler)
from utils import check_cancel_task, check_password, keyboard_ts, user_data


def register(dp):
    dp.add_handler()
