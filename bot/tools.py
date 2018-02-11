import logging
import pickle
from threading import Thread
from time import sleep

from telegram import Bot
from telegram.ext import (ConversationHandler, Dispatcher, Filters,
                          MessageHandler, Updater)
from telegram.ext.dispatcher import Dispatcher

from bot import schedule, service
from bot.models.models import Lecturers, Lessons, Users
from bot.models.tools import create_tables, drop_tables
from bot.service.common_handlers import start
from config import CONVERSATIONS_PATH, USERDATA_PATH


def load_data(conv_path: str, user_data_path: str) -> None:
    try:
        with open(conv_path, 'rb') as reader:
            ConversationHandler.conversations = pickle.load(reader)
        with open(user_data_path, 'rb') as reader:
            Dispatcher.user_data = pickle.load(reader)
    except FileNotFoundError as excinfo:
        logging.error("Data file not found: %s", excinfo)
    except BaseException as excinfo:
        logging.error(excinfo)


def save_data(period: float or int,
              conv_path: str,
              user_data_path: str) -> None:
    """ Infinite loop for with saving bot state """
    while True:
        sleep(period)
        # Before pickling
        resolved = {}
        for k, v in ConversationHandler.conversations.items():
            if isinstance(v, tuple) and len(v) is 2:
                try:
                    # Result of async function
                    new_state = v[1].result()
                except:
                    # In case async function raised an error, fallback to old state
                    new_state = v[0]
                resolved[k] = new_state
            else:
                resolved[k] = v
        try:
            with open(conv_path, 'wb+') as writer:
                pickle.dump(resolved, writer)
            with open(user_data_path, 'wb+') as writer:
                pickle.dump(Dispatcher.user_data, writer)
        except BaseException as excinfo:
            logging.error(excinfo)


def save_state(period: float or int=60, **kwargs) -> None:
    """ Start infinite state saving in separate thread """
    thread = Thread(
        name="save_data",
        args=period,
        kwargs=kwargs,
        target=save_data
    )
    thread.start()


def register(dispatcher: Dispatcher) -> None:
    """ Register all handlers with bot dispatcher """
    service.register(dispatcher)
    schedule.register(dispatcher)
    dispatcher.add_handler(MessageHandler(Filters.text, start))


def init_db() -> None:
    """ (re)Create tables in database """
    drop_tables(Users, Lecturers, Lessons)
    create_tables(Users, Lecturers, Lessons)


def run(token: str, workers: int=10) -> None:
    """ Start bot """
    # load previous state to continue chats correctly
    # load_data(CONVERSATIONS_PATH, USERDATA_PATH)

    updater = Updater(token, workers=workers)
    bot_api = Bot(token)
    register(updater.dispatcher)

    updater.start_polling()
    updater.idle()
