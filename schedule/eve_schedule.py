from datetime import datetime as dt
from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, RegexHandler, CommandHandler, \
    Filters, MessageHandler, CallbackQueryHandler
from model import Users, Clients, Tasks, DoesNotExist
from states import *
from utils import check_cancel_task, check_password, keyboard_ts, user_data
from logger import log
from egrul import select_region, data_client, solve_captcha, confirm_value, client_type
from bot import start


def register(dp):
    dp.add_handler()