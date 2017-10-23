import logging
import pickle

from telegram.ext import ConversationHandler, Dispatcher
from telegram.ext.dispatcher import Dispatcher


def load_data() -> None:
    try:
        with open('backup/conversations', 'rb') as reader:
            ConversationHandler.conversations = pickle.load(reader)
        with open('backup/userdata', 'rb') as reader:
            Dispatcher.user_data = pickle.load(reader)
    except FileNotFoundError as excinfo:
        logging.error("Data file not found: %s", excinfo)
    except BaseException as excinfo:
        logging.error(excinfo)


def save_data() -> None:
    from time import sleep

    while True:
        sleep(60)
        # Before pickling
        resolved = dict()
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
            with open('backup/conversations', 'wb+') as writer:
                pickle.dump(resolved, writer)
            with open('backup/userdata', 'wb+') as writer:
                pickle.dump(Dispatcher.user_data, writer)
        except BaseException as excinfo:
            logging.error(excinfo)


def save_state() -> None:
    from threading import Thread

    thread = Thread(name="save_data", target=save_data)
    thread.start()


def register(dispatcher: Dispatcher) -> None:
    from bot import buses, schedule, service, trains

    buses.register(dispatcher)
    schedule.register(dispatcher)
    service.register(dispatcher)
    trains.register(dispatcher)


def init_db() -> None:
    from bot.models.tools import create_tables, drop_tables
    from bot.models import TABLES

    drop_tables(TABLES)
    create_tables(TABLES)


def run(token: str, logger_level: int=0) -> None:
    from telegram import Bot
    from telegram.ext import Updater
    import logging

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logger_level
    )

    load_data()

    updater = Updater(token)
    api = Bot(token)
    register(updater.dispatcher)

    updater.start_polling()
    updater.idle()
