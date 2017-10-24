import logging
import pickle

from telegram.ext import ConversationHandler, Dispatcher
from telegram.ext.dispatcher import Dispatcher


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


def save_data(period: (float, int), conv_path: str,
              user_data_path: str) -> None:
    """ Infinite loop for with saving bot state """
    from time import sleep

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


def save_state(period: (float, int)=60, **kwargs) -> None:
    """ Start infinite state saving in separate thread """
    from threading import Thread

    thread = Thread(
        name="save_data",
        args=period,
        kwargs=kwargs,
        target=save_data
    )
    thread.start()


def register(dispatcher: Dispatcher) -> None:
    """ Register all handlers with bot dispatcher """
    from bot import buses, schedule, service, trains
    from telegram.ext import MessageHandler, Filters
    from bot.service.common_handlers import start

    schedule.register(dispatcher)
    service.register(dispatcher)
    buses.register(dispatcher)
    trains.register(dispatcher)
    dispatcher.add_handler(MessageHandler(Filters.text, start))


def init_db() -> None:
    """ (re)Create tables in database """
    from bot.models.tools import create_tables, drop_tables
    from bot.models import TABLES

    drop_tables(TABLES)
    create_tables(TABLES)


def run(token: str, logger_level: int=0, workers: int=10) -> None:
    """ Start bot """
    from config import CONVERSATIONS_PATH, USERDATA_PATH
    from telegram import Bot
    from telegram.ext import Updater
    import logging

    logging.basicConfig(
        filemode='a',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logger_level
    )

    # load previous state to continue chats correctly
    # load_data(CONVERSATIONS_PATH, USERDATA_PATH)

    updater = Updater(token, workers=workers)
    api = Bot(token)  # api is used to resolve name conflicts with main module
    register(updater.dispatcher)

    updater.start_polling()
    updater.idle()
