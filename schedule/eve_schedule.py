from datetime import datetime as dt

from logger import log
from service.common_handlers import start
from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler,
                          RegexHandler)
from utils import DAY_OF_WEEK

# from egrul import (client_type, confirm_value, data_client, select_region,
#                    solve_captcha)
# from model import Clients, DoesNotExist, Tasks, Users
# from utils import check_cancel_task, check_password, keyboard_ts, user_data


def register(dispatcher: object) -> None:
    dispatcher.add_handler()
